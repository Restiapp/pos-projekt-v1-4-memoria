"""
Image API Router - RESTful endpoints for Product Image Management
Module 0: Terméktörzs és Menü

Ez a modul tartalmazza a termékképekhez kapcsolódó FastAPI route-okat.
Használja a GCSService-t a signed URL generálásához és az ImageAsset modellt
a képek metaadatainak tárolásához.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_menu.database import get_db_connection
from backend.service_menu.services.gcs_service import GCSService
from backend.service_menu.services.product_service import ProductService
from backend.service_menu.models.image_asset import ImageAsset
from backend.service_menu.schemas.image_asset import (
    SignedUploadUrl,
    SignedUploadUrlRequest,
    ImageAssetResponse,
    ImageAssetListResponse,
)

# APIRouter létrehozása
router = APIRouter(
    prefix="/products",
    tags=["images"],
    responses={
        404: {"description": "Product or image not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)


def get_gcs_service() -> GCSService:
    """
    Dependency function a GCSService injektálásához.

    Returns:
        GCSService: GCS service instance
    """
    return GCSService()


def get_product_service() -> ProductService:
    """
    Dependency function a ProductService injektálásához.

    Returns:
        ProductService: Product service instance
    """
    return ProductService()


@router.post(
    "/{product_id}/images/upload-url",
    response_model=SignedUploadUrl,
    status_code=status.HTTP_200_OK,
    summary="Generate signed URL for image upload",
    description="""
    Generate a time-limited signed URL for uploading a product image directly to Google Cloud Storage.

    **Workflow:**
    1. Frontend calls this endpoint to get a signed URL
    2. Frontend uploads the image directly to GCS using the signed URL (PUT request)
    3. Frontend creates an ImageAsset record with the returned gcs_url

    **Requirements:**
    - Product must exist (product_id validation)
    - Content type must be one of: image/jpeg, image/png, image/webp, image/gif
    - File name must be provided

    **Returns:**
    - 200: Signed URL generated successfully
    - 404: Product not found
    - 400: Invalid content type or file name
    """,
    response_description="Signed URL and metadata for direct GCS upload",
)
def generate_upload_url(
    product_id: int,
    request_data: SignedUploadUrlRequest,
    db: Session = Depends(get_db_connection),
    gcs_service: GCSService = Depends(get_gcs_service),
    product_service: ProductService = Depends(get_product_service),
) -> SignedUploadUrl:
    """
    Signed URL generálása GCS képfeltöltéshez.

    Args:
        product_id: Termék azonosító
        request_data: Upload URL kérés adatok (file_name, content_type)
        db: Database session (dependency injection)
        gcs_service: GCS service instance (dependency injection)
        product_service: Product service instance (dependency injection)

    Returns:
        SignedUploadUrl: Signed URL adatok feltöltéshez

    Raises:
        HTTPException 404: Ha a termék nem található
        HTTPException 400: Ha érvénytelen content_type vagy file_name
    """
    # Ellenőrizzük, hogy a termék létezik-e
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    try:
        # Signed URL generálása
        upload_data = gcs_service.generate_signed_upload_url(
            file_name=request_data.file_name,
            content_type=request_data.content_type,
            product_id=product_id
        )

        return SignedUploadUrl(**upload_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating upload URL: {str(e)}"
        )


@router.get(
    "/{product_id}/images",
    response_model=ImageAssetListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all images for a product",
    description="""
    Retrieve all images associated with a specific product.

    **Use cases:**
    - Display product images in the frontend
    - Manage product image gallery
    - Verify uploaded images

    **Pagination:**
    - skip: Number of records to skip (offset)
    - limit: Maximum number of records to return (max 100)

    **Returns:**
    - 200: Image list retrieved successfully
    - 404: Product not found
    """,
    response_description="List of product images with pagination metadata",
)
def get_product_images(
    product_id: int,
    skip: int = Query(0, ge=0, description="Kihagyott elemek száma (pagination offset)"),
    limit: int = Query(100, ge=1, le=100, description="Max. visszaadott elemek száma"),
    db: Session = Depends(get_db_connection),
    product_service: ProductService = Depends(get_product_service),
) -> ImageAssetListResponse:
    """
    Termékhez tartozó képek listázása.

    Args:
        product_id: Termék azonosító
        skip: Pagination offset (kihagyott elemek száma)
        limit: Pagination limit (max elemszám)
        db: Database session (dependency injection)
        product_service: Product service instance (dependency injection)

    Returns:
        ImageAssetListResponse: Képek listája metaadatokkal (total, page, page_size)

    Raises:
        HTTPException 404: Ha a termék nem található
    """
    # Ellenőrizzük, hogy a termék létezik-e
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    # Képek lekérdezése a termékhez
    query = db.query(ImageAsset).filter(ImageAsset.product_id == product_id)

    # Total count
    total = query.count()

    # Lapozás alkalmazása
    images = query.offset(skip).limit(limit).all()

    # Pagination metadata számítása
    page = (skip // limit) + 1 if limit > 0 else 1
    page_size = len(images)

    return ImageAssetListResponse(
        items=images,
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete(
    "/{product_id}/images/{image_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete a product image",
    description="""
    Delete a specific product image from both the database and Google Cloud Storage.

    **Cascade deletion:**
    - Removes the image metadata from the database
    - Deletes the original image from GCS
    - Does NOT delete resized variants (handled by Cloud Function cleanup)

    **Returns:**
    - 200: Image deleted successfully
    - 404: Product or image not found
    - 400: Image does not belong to the specified product
    """,
    response_description="Deletion confirmation message",
)
def delete_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db_connection),
    gcs_service: GCSService = Depends(get_gcs_service),
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    """
    Termékhez tartozó kép törlése.

    Args:
        product_id: Termék azonosító
        image_id: Kép azonosító
        db: Database session (dependency injection)
        gcs_service: GCS service instance (dependency injection)
        product_service: Product service instance (dependency injection)

    Returns:
        dict: Törlés megerősítő üzenet és a törölt ID

    Raises:
        HTTPException 404: Ha a termék vagy kép nem található
        HTTPException 400: Ha a kép nem tartozik a megadott termékhez
    """
    # Ellenőrizzük, hogy a termék létezik-e
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    # Kép lekérdezése
    image = db.query(ImageAsset).filter(ImageAsset.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found"
        )

    # Ellenőrizzük, hogy a kép a megadott termékhez tartozik-e
    if image.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image {image_id} does not belong to product {product_id}"
        )

    # GCS blob törlése
    gcs_url = image.gcs_url_original
    try:
        gcs_service.delete_blob(gcs_url)
    except Exception as e:
        # Logoljuk a hibát, de folytatjuk a törlést az adatbázisban
        # (a blob esetleg már törölve lett vagy nem létezik)
        print(f"Warning: Failed to delete GCS blob {gcs_url}: {str(e)}")

    # Database rekord törlése
    db.delete(image)
    db.commit()

    return {
        "message": f"Image {image_id} deleted successfully from product {product_id}",
        "deleted_image_id": image_id,
        "product_id": product_id
    }
