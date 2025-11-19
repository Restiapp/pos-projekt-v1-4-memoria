"""
KDS (Kitchen Display System) API Routes
Module 1: Rendeléskezelés és Asztalok

This module contains FastAPI endpoints for the Kitchen Display System (KDS).
It provides specialized endpoints for managing order items in the kitchen workflow
with English status values (WAITING, IN_PROGRESS, READY).

Task B1: KDS Backend Model Implementation
- GET /kds/items?station=: List active order items for a specific station
- PATCH /kds/items/{itemId}/status: Update item status with validation
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.service_orders.models.database import get_db
from backend.service_orders.services.order_item_service import OrderItemService
from backend.service_orders.schemas.order_item import OrderItemResponse
from backend.service_orders.enums import KDSStatus, validate_kds_status_transition, get_allowed_transitions


# Router creation
router = APIRouter(
    prefix="/kds",
    tags=["kds"]
)


def get_order_item_service() -> OrderItemService:
    """
    Dependency function for OrderItemService injection.

    Returns:
        OrderItemService: OrderItem service instance
    """
    return OrderItemService()


class KDSStatusUpdateRequest(BaseModel):
    """Schema for KDS status update requests."""

    status: str = Field(
        ...,
        description="New KDS status (WAITING, IN_PROGRESS, READY)",
        examples=["WAITING", "IN_PROGRESS", "READY"]
    )

    def validate_status(self) -> None:
        """Validate that the status is a valid KDS status."""
        if not KDSStatus.is_valid(self.status):
            raise ValueError(
                f"Invalid KDS status: {self.status}. "
                f"Valid values are: {', '.join(KDSStatus.values())}"
            )


@router.get(
    "/items",
    response_model=list[OrderItemResponse],
    summary="Get active order items for a KDS station",
    description="""
    Retrieve all active order items for a specific Kitchen Display System (KDS) station.

    This endpoint is designed for KDS integration, allowing kitchen stations
    to view their assigned items filtered by station name.

    **Query Parameters:**
    - `station`: KDS station name (e.g., 'hot_kitchen', 'cold_station', 'bar')
      - Required parameter

    **Returns:**
    - 200: List of order items for the station (may be empty)
    - 400: Missing or invalid station parameter

    **Example:**
    ```
    GET /api/v1/kds/items?station=hot_kitchen
    ```
    """
)
def get_kds_items(
    station: str = Query(..., description="KDS station name (e.g., 'hot_kitchen', 'cold_station')"),
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    Get all active order items for a specific KDS station.

    Args:
        station: KDS station name (required query parameter)
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        list[OrderItemResponse]: List of order items for the station

    Raises:
        HTTPException 400: If station parameter is missing or empty
    """
    if not station or station.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Station parameter is required and cannot be empty"
        )

    try:
        # Get items for the specified station (without status filter to show all active items)
        items = service.get_items_by_kds_station(db, station, kds_status=None)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving KDS items: {str(e)}"
        )


@router.patch(
    "/items/{item_id}/status",
    response_model=OrderItemResponse,
    summary="Update KDS status of an order item",
    description="""
    Update the Kitchen Display System (KDS) status of an order item with validation.

    This endpoint enforces valid status transitions:
    - WAITING → IN_PROGRESS
    - IN_PROGRESS → READY (or back to WAITING if needed)
    - READY → IN_PROGRESS (allows reverting if needed)

    **Path Parameters:**
    - `item_id`: Unique order item identifier (integer)

    **Request Body:**
    ```json
    {
        "status": "IN_PROGRESS"
    }
    ```

    **Returns:**
    - 200: Updated order item with new KDS status
    - 400: Invalid status or invalid transition
    - 404: Order item not found

    **Status Transition Examples:**
    - ✅ WAITING → IN_PROGRESS (valid)
    - ✅ IN_PROGRESS → READY (valid)
    - ❌ WAITING → READY (invalid - must go through IN_PROGRESS)
    """
)
def update_kds_item_status(
    item_id: int,
    status_update: KDSStatusUpdateRequest,
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    Update the KDS status of an order item with validation.

    Args:
        item_id: Order item unique identifier
        status_update: Status update request with new status
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        OrderItemResponse: Updated order item details

    Raises:
        HTTPException 400: If status is invalid or transition is not allowed
        HTTPException 404: If order item not found
    """
    try:
        # Validate that the new status is a valid KDS status
        status_update.validate_status()
        new_status = status_update.status

        # Get the current item to check current status
        current_item = service.get_item_by_id(db, item_id)

        if not current_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order item with ID {item_id} not found"
            )

        # Validate the status transition
        current_status = current_item.kds_status

        # If current status is Hungarian, we need to handle the transition differently
        # For now, we'll allow transitions from Hungarian statuses to English statuses
        if current_status in ['VÁRAKOZIK', 'KÉSZÜL', 'KÉSZ', 'KISZOLGÁLVA']:
            # Allow migration from Hungarian to English statuses
            pass
        elif not validate_kds_status_transition(current_status, new_status):
            allowed = get_allowed_transitions(current_status)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from '{current_status}' to '{new_status}'. "
                       f"Allowed transitions: {', '.join(allowed) if allowed else 'none'}"
            )

        # Update the status
        item = service.update_kds_status(db, item_id, new_status)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order item with ID {item_id} not found"
            )

        return item

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating KDS status: {str(e)}"
        )
