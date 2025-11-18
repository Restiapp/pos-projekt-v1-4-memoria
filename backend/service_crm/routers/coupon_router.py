"""
Coupon Router - FastAPI Endpoints for Coupon Management
Module 5: Customer Relationship Management (CRM)

Ez a router felelős a kuponok REST API végpontjaiért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- Kupon validáció
- Kedvezmény számítás
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_crm.models.database import get_db
from backend.service_crm.services.coupon_service import CouponService
from backend.service_crm.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponListResponse,
    CouponValidationRequest,
    CouponValidationResponse,
    DiscountTypeEnum
)

# Router létrehozása
coupons_router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"],
    responses={404: {"description": "Coupon not found"}}
)


@coupons_router.post(
    "/",
    response_model=CouponResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new coupon",
    description="Creates a new coupon with discount rules and validity period."
)
def create_coupon(
    coupon_data: CouponCreate,
    db: Session = Depends(get_db)
) -> CouponResponse:
    """
    Create a new coupon.

    Args:
        coupon_data: Coupon creation data (code, discount type, value, etc.)
        db: Database session (injected)

    Returns:
        CouponResponse: The newly created coupon

    Raises:
        HTTPException 400: If coupon code already exists or data is invalid

    Example request body:
        {
            "code": "WELCOME10",
            "description": "10% discount for new customers",
            "discount_type": "PERCENTAGE",
            "discount_value": 10.00,
            "min_purchase_amount": 1000.00,
            "usage_limit": 100,
            "valid_from": "2024-01-01T00:00:00Z",
            "valid_until": "2024-12-31T23:59:59Z",
            "is_active": true
        }
    """
    coupon = CouponService.create_coupon(db, coupon_data)
    return CouponResponse.model_validate(coupon)


@coupons_router.get(
    "/",
    response_model=CouponListResponse,
    summary="List all coupons",
    description="Retrieve a paginated list of coupons with optional filtering."
)
def get_coupons(
    skip: int = Query(0, ge=0, description="Number of coupons to skip (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of coupons to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID (null for public coupons)"),
    discount_type: Optional[DiscountTypeEnum] = Query(None, description="Filter by discount type"),
    db: Session = Depends(get_db)
) -> CouponListResponse:
    """
    Get a list of coupons with optional filtering.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        is_active: Optional filter by active/inactive status
        customer_id: Optional filter by customer-specific coupons
        discount_type: Optional filter by discount type
        db: Database session (injected)

    Returns:
        CouponListResponse: Paginated list of coupons with metadata

    Example:
        GET /coupons?skip=0&limit=20&is_active=true
    """
    discount_type_str = discount_type.value if discount_type else None

    coupons = CouponService.get_coupons(
        db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        customer_id=customer_id,
        discount_type=discount_type_str
    )

    total = CouponService.count_coupons(
        db,
        is_active=is_active,
        customer_id=customer_id,
        discount_type=discount_type_str
    )

    page = (skip // limit) + 1 if limit > 0 else 1

    return CouponListResponse(
        items=[CouponResponse.model_validate(coupon) for coupon in coupons],
        total=total,
        page=page,
        page_size=limit
    )


@coupons_router.get(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="Get coupon by ID",
    description="Retrieve a single coupon by its unique identifier."
)
def get_coupon(
    coupon_id: int,
    db: Session = Depends(get_db)
) -> CouponResponse:
    """
    Get a specific coupon by ID.

    Args:
        coupon_id: Coupon's unique identifier
        db: Database session (injected)

    Returns:
        CouponResponse: Coupon details

    Raises:
        HTTPException 404: If coupon not found

    Example:
        GET /coupons/42
    """
    coupon = CouponService.get_coupon(db, coupon_id)
    return CouponResponse.model_validate(coupon)


@coupons_router.put(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="Update coupon",
    description="Update an existing coupon's information."
)
def update_coupon(
    coupon_id: int,
    coupon_data: CouponUpdate,
    db: Session = Depends(get_db)
) -> CouponResponse:
    """
    Update a coupon's information.

    Args:
        coupon_id: Coupon's unique identifier
        coupon_data: Updated coupon data
        db: Database session (injected)

    Returns:
        CouponResponse: Updated coupon details

    Raises:
        HTTPException 404: If coupon not found
        HTTPException 400: If data is invalid

    Example request body:
        {
            "is_active": false,
            "description": "Updated description"
        }
    """
    coupon = CouponService.update_coupon(db, coupon_id, coupon_data)
    return CouponResponse.model_validate(coupon)


@coupons_router.delete(
    "/{coupon_id}",
    summary="Delete coupon",
    description="Delete a coupon from the system."
)
def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a coupon.

    Args:
        coupon_id: Coupon's unique identifier
        db: Database session (injected)

    Returns:
        dict: Confirmation message

    Raises:
        HTTPException 404: If coupon not found

    Example:
        DELETE /coupons/42
    """
    return CouponService.delete_coupon(db, coupon_id)


@coupons_router.get(
    "/code/{code}",
    response_model=CouponResponse,
    summary="Get coupon by code",
    description="Retrieve a coupon by its unique code."
)
def get_coupon_by_code(
    code: str,
    db: Session = Depends(get_db)
) -> CouponResponse:
    """
    Get a coupon by code.

    Args:
        code: Coupon code
        db: Database session (injected)

    Returns:
        CouponResponse: Coupon details

    Raises:
        HTTPException 404: If coupon not found

    Example:
        GET /coupons/code/WELCOME10
    """
    coupon = CouponService.get_coupon_by_code(db, code)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kupon nem található ezzel a kóddal: {code}"
        )
    return CouponResponse.model_validate(coupon)


@coupons_router.post(
    "/validate",
    response_model=CouponValidationResponse,
    summary="Validate coupon",
    description="Validate a coupon code and calculate the discount amount."
)
def validate_coupon(
    validation_request: CouponValidationRequest,
    db: Session = Depends(get_db)
) -> CouponValidationResponse:
    """
    Validate a coupon and calculate discount.

    Args:
        validation_request: Coupon validation request (code, order amount, customer ID)
        db: Database session (injected)

    Returns:
        CouponValidationResponse: Validation result with discount amount

    Example request body:
        {
            "code": "WELCOME10",
            "order_amount": 5000.00,
            "customer_id": 42
        }

    Example response:
        {
            "valid": true,
            "message": "A kupon érvényes",
            "discount_amount": 500.00,
            "coupon": {...}
        }
    """
    result = CouponService.validate_coupon(db, validation_request)

    # Convert coupon object to CouponResponse if present
    if result["coupon"]:
        result["coupon"] = CouponResponse.model_validate(result["coupon"])

    return CouponValidationResponse(**result)


@coupons_router.post(
    "/{coupon_id}/use",
    response_model=CouponResponse,
    summary="Increment coupon usage",
    description="Increment the usage counter for a coupon (called after successful order)."
)
def increment_coupon_usage(
    coupon_id: int,
    db: Session = Depends(get_db)
) -> CouponResponse:
    """
    Increment coupon usage counter.

    This endpoint should be called after a successful order
    to track coupon usage and enforce usage limits.

    Args:
        coupon_id: Coupon's unique identifier
        db: Database session (injected)

    Returns:
        CouponResponse: Updated coupon with incremented usage count

    Raises:
        HTTPException 404: If coupon not found

    Example:
        POST /coupons/42/use
    """
    coupon = CouponService.increment_usage(db, coupon_id)
    return CouponResponse.model_validate(coupon)
