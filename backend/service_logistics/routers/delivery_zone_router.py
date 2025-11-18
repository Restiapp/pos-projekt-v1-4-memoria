"""
DeliveryZone API Router - RESTful endpoints for Delivery Zone Management
V3.0 Module: Logistics Service - Phase 2.A

This module contains FastAPI routes for delivery zones.
Uses the DeliveryZoneService for business logic execution.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_logistics.models.database import get_db
from backend.service_logistics.services.delivery_zone_service import DeliveryZoneService
from backend.service_logistics.schemas.delivery_zone import (
    DeliveryZoneCreate,
    DeliveryZoneUpdate,
    DeliveryZoneResponse,
    DeliveryZoneListResponse,
    GetByAddressRequest,
    GetByAddressResponse,
)

# Create APIRouter
router = APIRouter(
    prefix="/zones",
    tags=["delivery-zones"],
    responses={
        404: {"description": "Delivery zone not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)


@router.post(
    "",
    response_model=DeliveryZoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new delivery zone",
    description="""
    Create a new delivery zone in the system.

    **Business rules:**
    - Zone name (zone_name) must be unique
    - Delivery fee must be >= 0
    - Minimum order value must be >= 0
    - Estimated delivery time must be between 5 and 120 minutes

    **Return values:**
    - 201: Zone successfully created
    - 400: Validation error or zone name already exists
    """,
    response_description="Newly created delivery zone data",
)
def create_delivery_zone(
    zone_data: DeliveryZoneCreate,
    db: Session = Depends(get_db),
) -> DeliveryZoneResponse:
    """
    Create new delivery zone.

    Args:
        zone_data: Delivery zone data (zone_name, description, fees, etc.)
        db: Database session (dependency injection)

    Returns:
        DeliveryZoneResponse: Created delivery zone data

    Raises:
        HTTPException 400: If zone name already exists
    """
    try:
        zone = DeliveryZoneService.create_delivery_zone(db=db, zone_data=zone_data)
        return zone
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=DeliveryZoneListResponse,
    status_code=status.HTTP_200_OK,
    summary="List delivery zones",
    description="""
    Query delivery zones with pagination.

    **Pagination parameters:**
    - page: Page number (starts at 1)
    - page_size: Page size (max 100)
    - active_only: If true, only return active zones

    **Return values:**
    - 200: Zone list successfully retrieved
    - 400: Invalid pagination parameters
    """,
    response_description="List of delivery zones with pagination info",
)
def get_delivery_zones(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Page size (max 100)"),
    active_only: bool = Query(False, description="Only return active zones"),
    db: Session = Depends(get_db),
) -> DeliveryZoneListResponse:
    """
    List delivery zones with pagination.

    Args:
        page: Page number (starts at 1)
        page_size: Page size
        active_only: Filter for active zones only
        db: Database session (dependency injection)

    Returns:
        DeliveryZoneListResponse: Zone list with metadata (total, page, page_size)
    """
    # Calculate skip value based on page
    skip = (page - 1) * page_size

    zones, total = DeliveryZoneService.list_delivery_zones(
        db=db,
        skip=skip,
        limit=page_size,
        active_only=active_only
    )

    return DeliveryZoneListResponse(
        items=zones,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/by-name/{zone_name}",
    response_model=DeliveryZoneResponse,
    status_code=status.HTTP_200_OK,
    summary="Get delivery zone by zone name",
    description="""
    Query delivery zone by zone name (zone_name).

    **Use cases:**
    - Quick zone lookup by name
    - Zone identification by user-friendly identifier

    **Return values:**
    - 200: Zone successfully retrieved
    - 404: Zone not found with the given name
    """,
    response_description="Delivery zone data",
)
def get_delivery_zone_by_name(
    zone_name: str,
    db: Session = Depends(get_db),
) -> DeliveryZoneResponse:
    """
    Get delivery zone by zone name.

    Args:
        zone_name: Zone name/identifier
        db: Database session (dependency injection)

    Returns:
        DeliveryZoneResponse: Delivery zone data

    Raises:
        HTTPException 404: If zone not found
    """
    zone = DeliveryZoneService.get_delivery_zone_by_name(db=db, zone_name=zone_name)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery zone '{zone_name}' not found"
        )
    return zone


@router.get(
    "/{zone_id}",
    response_model=DeliveryZoneResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single delivery zone",
    description="""
    Query single delivery zone by ID.

    **Use cases:**
    - Display zone details
    - Pre-fill edit form
    - Validate zone data

    **Return values:**
    - 200: Zone successfully retrieved
    - 404: Zone not found with the given ID
    """,
    response_description="Delivery zone data",
)
def get_delivery_zone(
    zone_id: int,
    db: Session = Depends(get_db),
) -> DeliveryZoneResponse:
    """
    Get single delivery zone by ID.

    Args:
        zone_id: Zone identifier
        db: Database session (dependency injection)

    Returns:
        DeliveryZoneResponse: Delivery zone data

    Raises:
        HTTPException 404: If zone not found
    """
    zone = DeliveryZoneService.get_delivery_zone(db=db, zone_id=zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery zone (ID: {zone_id}) not found"
        )
    return zone


@router.put(
    "/{zone_id}",
    response_model=DeliveryZoneResponse,
    status_code=status.HTTP_200_OK,
    summary="Update delivery zone",
    description="""
    Update existing delivery zone by ID.

    **Business rules:**
    - Zone name must be unique
    - Fees and values must be >= 0
    - Estimated delivery time must be between 5 and 120 minutes

    **Partial update (PATCH-like behavior):**
    - Only provided fields will be updated
    - Unprovided fields remain unchanged

    **Return values:**
    - 200: Zone successfully updated
    - 404: Zone not found
    - 400: Validation error or zone name conflict
    """,
    response_description="Updated delivery zone data",
)
def update_delivery_zone(
    zone_id: int,
    zone_data: DeliveryZoneUpdate,
    db: Session = Depends(get_db),
) -> DeliveryZoneResponse:
    """
    Update delivery zone.

    Args:
        zone_id: Zone identifier to update
        zone_data: Fields to update (only provided fields change)
        db: Database session (dependency injection)

    Returns:
        DeliveryZoneResponse: Updated delivery zone data

    Raises:
        HTTPException 404: If zone not found
        HTTPException 400: If validation error occurs
    """
    try:
        zone = DeliveryZoneService.update_delivery_zone(db=db, zone_id=zone_id, zone_data=zone_data)
        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Delivery zone (ID: {zone_id}) not found"
            )
        return zone
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{zone_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete delivery zone",
    description="""
    Delete delivery zone by ID.

    **Deletion rules:**
    - Zone is permanently deleted
    - Associated deliveries may become orphaned (depends on relationship config)

    **Return values:**
    - 200: Zone successfully deleted
    - 404: Zone not found

    **Warning:**
    Zone deletion is irreversible!
    """,
    response_description="Deletion confirmation (message and deleted_id)",
)
def delete_delivery_zone(
    zone_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """
    Delete delivery zone.

    Args:
        zone_id: Zone identifier to delete
        db: Database session (dependency injection)

    Returns:
        dict: Deletion confirmation message and deleted ID

    Raises:
        HTTPException 404: If zone not found
    """
    success = DeliveryZoneService.delete_delivery_zone(db=db, zone_id=zone_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery zone (ID: {zone_id}) not found"
        )

    return {
        "message": f"Delivery zone (ID: {zone_id}) successfully deleted",
        "deleted_id": zone_id
    }


# V3.0 - Phase 2.A: MOCK Endpoint for Get-by-Address
@router.post(
    "/get-by-address",
    response_model=GetByAddressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get delivery zone by address (MOCK)",
    description="""
    **MOCK ENDPOINT - V3.0 Phase 2.A**

    Get delivery zone by customer address.

    **Current Implementation:**
    - This is a MOCK implementation
    - Always returns the first active zone (if any exists)
    - Does NOT perform real Google Maps / GeoJSON lookup

    **Phase 3 Implementation:**
    - Will use Google Maps Geocoding API
    - Will perform GeoJSON polygon lookup
    - Will return the actual zone containing the address coordinates

    **Return values:**
    - 200: Response with zone (or null if not found in MOCK mode)
    """,
    response_description="Zone data (MOCK response)",
)
def get_zone_by_address(
    request: GetByAddressRequest,
    db: Session = Depends(get_db),
) -> GetByAddressResponse:
    """
    Get delivery zone by address (MOCK implementation).

    **IMPORTANT:** This is a MOCK endpoint. In Phase 3, this will be replaced
    with real Google Maps / GeoJSON logic.

    Args:
        request: Address request data
        db: Database session (dependency injection)

    Returns:
        GetByAddressResponse: MOCK response with first active zone
    """
    # MOCK IMPLEMENTATION: Return first active zone
    active_zones = DeliveryZoneService.get_active_zones(db=db)

    if active_zones:
        zone = active_zones[0]
        return GetByAddressResponse(
            zone=zone,
            message=f"MOCK: Zone '{zone.zone_name}' matched for address '{request.address}'",
            mock_mode=True
        )
    else:
        return GetByAddressResponse(
            zone=None,
            message=f"MOCK: No active zones found for address '{request.address}'",
            mock_mode=True
        )
