"""
Product API Routes
Module 0: Terméktörzs és Menü

Ez a modul tartalmazza a Product entitáshoz kapcsolódó FastAPI végpontokat.
Implementálja a teljes CRUD műveletsort és támogatja a lapozást és szűrést.

Alfeladat 7.2: AI fordítás integráció - A POST és PUT végpontok
automatikusan lefordítják a termékeket háttérfolyamatként.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session

from backend.service_menu.database import get_db_connection
from backend.service_menu.services.product_service import ProductService
from backend.service_menu.services.translation_service import TranslationService
from backend.service_menu.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse
)


# Router létrehozása
router = APIRouter(
    prefix="/products",
    tags=["products"]
)


def get_product_service() -> ProductService:
    """
    Dependency function a ProductService injektálásához.

    Returns:
        ProductService: Product service instance
    """
    return ProductService()


def get_translation_service() -> TranslationService:
    """
    Dependency function a TranslationService injektálásához.

    Returns:
        TranslationService: Translation service instance
    """
    return TranslationService()


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="""
    Create a new product in the menu system.

    This endpoint allows you to create a new product with all necessary details
    including name, description, base price, category association, SKU, and active status.

    **AI Translation (Alfeladat 7.2):**
    - Automatically translates product name and description to multiple languages
    - Translation happens in the background (asynchronous)
    - Supported languages: English, German, French, Italian, Spanish

    **Requirements:**
    - Product name is required (1-255 characters)
    - Base price must be >= 0
    - SKU must be unique if provided

    **Returns:**
    - 201: Successfully created product with all details
    - 400: Invalid input data or duplicate SKU
    """
)
def create_product(
    product_data: ProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_connection),
    service: ProductService = Depends(get_product_service),
    translation_service: TranslationService = Depends(get_translation_service)
):
    """
    Új termék létrehozása AI fordítással.

    A termék létrehozása után automatikusan elindít egy háttérfolyamatot,
    amely lefordítja a termék nevét és leírását több nyelvre.

    Args:
        product_data: ProductCreate schema with product details
        background_tasks: FastAPI background tasks (injected)
        db: Database session (injected)
        service: ProductService instance (injected)
        translation_service: TranslationService instance (injected)

    Returns:
        ProductResponse: Created product details

    Raises:
        HTTPException 400: If SKU already exists or validation fails
    """
    try:
        # 1. Termék létrehozása
        product = service.create_product(db, product_data)

        # 2. AI fordítás háttérfolyamatként (Alfeladat 7.2)
        # A fordítás aszinkron módon történik, nem blokkolja a választ
        background_tasks.add_task(
            service.update_product_translations,
            db=db,
            product_id=product.id,
            translation_service=translation_service
        )

        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the product: {str(e)}"
        )


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Get all products with pagination",
    description="""
    Retrieve a paginated list of products with optional filtering.

    This endpoint supports:
    - **Pagination**: Control the number of results and skip records
    - **Filtering**: Filter by active status, category

    **Query Parameters:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records to return (default: 20, max: 100)
    - `include_inactive`: Include inactive products (default: true)
    - `category_id`: Filter by category ID (optional)

    **Returns:**
    - 200: Paginated list of products with metadata (total count, page info)
    """
)
def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    include_inactive: bool = Query(True, description="Include inactive products in results"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db_connection),
    service: ProductService = Depends(get_product_service)
):
    """
    Termékek listázása lapozással és szűréssel.

    Args:
        skip: Pagination offset
        limit: Page size
        include_inactive: Whether to include inactive products
        category_id: Optional category filter
        db: Database session (injected)
        service: ProductService instance (injected)

    Returns:
        ProductListResponse: Paginated list with metadata
    """
    try:
        # Filter by category if specified
        if category_id is not None:
            products = service.get_products_by_category(
                db=db,
                category_id=category_id,
                skip=skip,
                limit=limit,
                include_inactive=include_inactive
            )
        else:
            products = service.get_all_products(
                db=db,
                skip=skip,
                limit=limit,
                include_inactive=include_inactive
            )

        # Get total count
        total = service.count_products(db=db, include_inactive=include_inactive)

        # Calculate page number
        page = (skip // limit) + 1 if limit > 0 else 1

        return ProductListResponse(
            items=products,
            total=total,
            page=page,
            page_size=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving products: {str(e)}"
        )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="""
    Retrieve a single product by its unique identifier.

    **Path Parameters:**
    - `product_id`: Unique product identifier (integer)

    **Returns:**
    - 200: Product details
    - 404: Product not found
    """
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db_connection),
    service: ProductService = Depends(get_product_service)
):
    """
    Termék lekérdezése ID alapján.

    Args:
        product_id: Product unique identifier
        db: Database session (injected)
        service: ProductService instance (injected)

    Returns:
        ProductResponse: Product details

    Raises:
        HTTPException 404: If product not found
    """
    product = service.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    description="""
    Update an existing product by its ID.

    This endpoint allows partial updates - you only need to provide the fields
    you want to change. All other fields will remain unchanged.

    **AI Translation (Alfeladat 7.2):**
    - If name or description is updated, automatically re-translates to all languages
    - Translation happens in the background (asynchronous)
    - Existing translations are updated with new values

    **Path Parameters:**
    - `product_id`: Unique product identifier (integer)

    **Request Body:**
    - Any combination of updatable fields (all optional)

    **Returns:**
    - 200: Updated product details
    - 404: Product not found
    - 400: Invalid update data or duplicate SKU
    """
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_connection),
    service: ProductService = Depends(get_product_service),
    translation_service: TranslationService = Depends(get_translation_service)
):
    """
    Termék frissítése AI fordítással.

    Ha a termék neve vagy leírása megváltozik, automatikusan újrafordítja
    a terméket minden támogatott nyelvre háttérfolyamatként.

    Args:
        product_id: Product unique identifier
        product_data: ProductUpdate schema with fields to update
        background_tasks: FastAPI background tasks (injected)
        db: Database session (injected)
        service: ProductService instance (injected)
        translation_service: TranslationService instance (injected)

    Returns:
        ProductResponse: Updated product details

    Raises:
        HTTPException 404: If product not found
        HTTPException 400: If validation fails or SKU already exists
    """
    try:
        # 1. Termék frissítése
        product = service.update_product(db, product_id, product_data)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )

        # 2. AI fordítás újragenerálása, ha a név vagy leírás változott (Alfeladat 7.2)
        # Csak akkor fordítunk újra, ha a név vagy leírás módosult
        update_dict = product_data.model_dump(exclude_unset=True)
        if 'name' in update_dict or 'description' in update_dict:
            background_tasks.add_task(
                service.update_product_translations,
                db=db,
                product_id=product.id,
                translation_service=translation_service
            )

        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the product: {str(e)}"
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="""
    Delete a product by its ID.

    **Warning:** This is a hard delete operation. The product will be permanently
    removed from the database. Consider using the soft delete functionality
    (setting is_active to false) for safer deletion.

    **Path Parameters:**
    - `product_id`: Unique product identifier (integer)

    **Returns:**
    - 204: Product successfully deleted (no content)
    - 404: Product not found
    """
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db_connection),
    service: ProductService = Depends(get_product_service)
):
    """
    Termék törlése.

    Args:
        product_id: Product unique identifier
        db: Database session (injected)
        service: ProductService instance (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: If product not found
    """
    success = service.delete_product(db, product_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    return None
