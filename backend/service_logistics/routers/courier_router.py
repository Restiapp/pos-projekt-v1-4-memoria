"""
Courier API Router - RESTful endpoints for Courier Management
V3.0 Module: Logistics Service - Phase 2.A

This module contains FastAPI routes for couriers.
Uses the CourierService for business logic execution.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_logistics.models.database import get_db
from backend.service_logistics.models.courier import CourierStatus
from backend.service_logistics.services.courier_service import CourierService
from backend.service_logistics.schemas.courier import (
    CourierCreate,
    CourierUpdate,
    CourierResponse,
    CourierListResponse,
)

# Create APIRouter
router = APIRouter(
    prefix="/couriers",
    tags=["couriers"],
    responses={
        404: {"description": "Courier not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)


@router.post(
    "",
    response_model=CourierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new courier",
    description="""
    Create a new courier in the system.

    **Business rules:**
    - Phone number must be unique
    - Email must be unique (if provided)
    - Status defaults to OFFLINE
    - is_active defaults to True

    **Return values:**
    - 201: Courier successfully created
    - 400: Validation error or phone/email already exists
    """,
    response_description="Newly created courier data",
)
def create_courier(
    courier_data: CourierCreate,
    db: Session = Depends(get_db),
) -> CourierResponse:
    """
    Create new courier.

    Args:
        courier_data: Courier data (name, phone, email, status, etc.)
        db: Database session (dependency injection)

    Returns:
        CourierResponse: Created courier data

    Raises:
        HTTPException 400: If phone or email already exists
    """
    try:
        courier = CourierService.create_courier(db=db, courier_data=courier_data)
        return courier
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=CourierListResponse,
    status_code=status.HTTP_200_OK,
    summary="List couriers",
    description="""
    Query couriers with pagination and filtering.

    **Pagination parameters:**
    - page: Page number (starts at 1)
    - page_size: Page size (max 100)

    **Filter parameters:**
    - status: Filter by courier status (available, on_delivery, offline, break)
    - active_only: If true, only return active couriers

    **Return values:**
    - 200: Courier list successfully retrieved
    - 400: Invalid pagination parameters
    """,
    response_description="List of couriers with pagination info",
)
def get_couriers(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Page size (max 100)"),
    status: Optional[CourierStatus] = Query(None, description="Filter by status"),
    active_only: bool = Query(False, description="Only return active couriers"),
    db: Session = Depends(get_db),
) -> CourierListResponse:
    """
    List couriers with pagination and filtering.

    Args:
        page: Page number (starts at 1)
        page_size: Page size
        status: Filter by courier status (optional)
        active_only: Filter for active couriers only
        db: Database session (dependency injection)

    Returns:
        CourierListResponse: Courier list with metadata (total, page, page_size)
    """
    # Calculate skip value based on page
    skip = (page - 1) * page_size

    couriers, total = CourierService.list_couriers(
        db=db,
        skip=skip,
        limit=page_size,
        status=status,
        active_only=active_only
    )

    return CourierListResponse(
        items=couriers,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/available",
    response_model=list[CourierResponse],
    status_code=status.HTTP_200_OK,
    summary="Get available couriers",
    description="""
    Get all available couriers (status=AVAILABLE and is_active=True).

    **Use cases:**
    - Assign delivery to available courier
    - Display available couriers in admin panel
    - Check courier availability before assigning order

    **Return values:**
    - 200: List of available couriers
    """,
    response_description="List of available couriers",
)
def get_available_couriers(
    db: Session = Depends(get_db),
) -> list[CourierResponse]:
    """
    Get all available couriers.

    Args:
        db: Database session (dependency injection)

    Returns:
        list[CourierResponse]: List of available couriers
    """
    return CourierService.get_available_couriers(db=db)


@router.get(
    "/by-phone/{phone}",
    response_model=CourierResponse,
    status_code=status.HTTP_200_OK,
    summary="Get courier by phone number",
    description="""
    Query courier by phone number.

    **Use cases:**
    - Quick courier lookup by phone
    - Verify courier identity by phone
    - Courier identification by unique phone number

    **Return values:**
    - 200: Courier successfully retrieved
    - 404: Courier not found with the given phone
    """,
    response_description="Courier data",
)
def get_courier_by_phone(
    phone: str,
    db: Session = Depends(get_db),
) -> CourierResponse:
    """
    Get courier by phone number.

    Args:
        phone: Courier's phone number
        db: Database session (dependency injection)

    Returns:
        CourierResponse: Courier data

    Raises:
        HTTPException 404: If courier not found
    """
    courier = CourierService.get_courier_by_phone(db=db, phone=phone)
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Courier with phone '{phone}' not found"
        )
    return courier


@router.get(
    "/{courier_id}",
    response_model=CourierResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single courier",
    description="""
    Query single courier by ID.

    **Use cases:**
    - Display courier details
    - Pre-fill edit form
    - Validate courier data

    **Return values:**
    - 200: Courier successfully retrieved
    - 404: Courier not found with the given ID
    """,
    response_description="Courier data",
)
def get_courier(
    courier_id: int,
    db: Session = Depends(get_db),
) -> CourierResponse:
    """
    Get single courier by ID.

    Args:
        courier_id: Courier identifier
        db: Database session (dependency injection)

    Returns:
        CourierResponse: Courier data

    Raises:
        HTTPException 404: If courier not found
    """
    courier = CourierService.get_courier(db=db, courier_id=courier_id)
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Courier (ID: {courier_id}) not found"
        )
    return courier


@router.put(
    "/{courier_id}",
    response_model=CourierResponse,
    status_code=status.HTTP_200_OK,
    summary="Update courier",
    description="""
    Update existing courier by ID.

    **Business rules:**
    - Phone number must be unique
    - Email must be unique (if provided)

    **Partial update (PATCH-like behavior):**
    - Only provided fields will be updated
    - Unprovided fields remain unchanged

    **Return values:**
    - 200: Courier successfully updated
    - 404: Courier not found
    - 400: Validation error or phone/email conflict
    """,
    response_description="Updated courier data",
)
def update_courier(
    courier_id: int,
    courier_data: CourierUpdate,
    db: Session = Depends(get_db),
) -> CourierResponse:
    """
    Update courier.

    Args:
        courier_id: Courier identifier to update
        courier_data: Fields to update (only provided fields change)
        db: Database session (dependency injection)

    Returns:
        CourierResponse: Updated courier data

    Raises:
        HTTPException 404: If courier not found
        HTTPException 400: If validation error occurs
    """
    try:
        courier = CourierService.update_courier(db=db, courier_id=courier_id, courier_data=courier_data)
        if not courier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Courier (ID: {courier_id}) not found"
            )
        return courier
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{courier_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete courier",
    description="""
    Delete courier by ID.

    **Deletion rules:**
    - Courier is permanently deleted
    - Associated deliveries may become orphaned (depends on relationship config)

    **Return values:**
    - 200: Courier successfully deleted
    - 404: Courier not found

    **Warning:**
    Courier deletion is irreversible!
    """,
    response_description="Deletion confirmation (message and deleted_id)",
)
def delete_courier(
    courier_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """
    Delete courier.

    Args:
        courier_id: Courier identifier to delete
        db: Database session (dependency injection)

    Returns:
        dict: Deletion confirmation message and deleted ID

    Raises:
        HTTPException 404: If courier not found
    """
    success = CourierService.delete_courier(db=db, courier_id=courier_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Courier (ID: {courier_id}) not found"
        )

    return {
        "message": f"Courier (ID: {courier_id}) successfully deleted",
        "deleted_id": courier_id
    }


@router.patch(
    "/{courier_id}/status",
    response_model=CourierResponse,
    status_code=status.HTTP_200_OK,
    summary="Update courier status",
    description="""
    Update courier status only.

    **Valid statuses:**
    - AVAILABLE: Available for deliveries
    - ON_DELIVERY: Currently delivering
    - OFFLINE: Not available
    - BREAK: On break

    **Use cases:**
    - Courier starts shift (OFFLINE -> AVAILABLE)
    - Courier accepts delivery (AVAILABLE -> ON_DELIVERY)
    - Courier finishes delivery (ON_DELIVERY -> AVAILABLE)
    - Courier takes break (AVAILABLE -> BREAK)
    - Courier ends shift (ANY -> OFFLINE)

    **Return values:**
    - 200: Status successfully updated
    - 404: Courier not found
    """,
    response_description="Updated courier data",
)
def update_courier_status(
    courier_id: int,
    new_status: CourierStatus = Query(..., description="New courier status"),
    db: Session = Depends(get_db),
) -> CourierResponse:
    """
    Update courier status.

    Args:
        courier_id: Courier identifier
        new_status: New status to set
        db: Database session (dependency injection)

    Returns:
        CourierResponse: Updated courier data

    Raises:
        HTTPException 404: If courier not found
    """
    courier = CourierService.update_courier_status(db=db, courier_id=courier_id, new_status=new_status)
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Courier (ID: {courier_id}) not found"
        )
    return courier
