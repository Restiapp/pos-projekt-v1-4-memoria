"""
OrderItem API Routes
Module 1: Rendeléskezelés és Asztalok

Ez a modul tartalmazza az OrderItem entitáshoz kapcsolódó FastAPI végpontokat.
Implementálja a teljes CRUD műveletsort és támogatja a KDS (Kitchen Display System) integrációt.

Alfeladat 5.5: OrderItem Router - Rendelési tételek API végpontjai
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.services.order_item_service import OrderItemService
from backend.service_orders.schemas.order_item import (
    OrderItemCreate,
    OrderItemUpdate,
    OrderItemResponse,
    OrderItemListResponse
)


# Router létrehozása
router = APIRouter(
    prefix="/orders",
    tags=["order-items"]
)


def get_order_item_service() -> OrderItemService:
    """
    Dependency function az OrderItemService injektálásához.

    Returns:
        OrderItemService: OrderItem service instance
    """
    return OrderItemService()


@router.post(
    "/{order_id}/items",
    response_model=OrderItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new item to an order",
    description="""
    Add a new item to an existing order.

    This endpoint allows you to add a product to an order with all necessary details
    including quantity, unit price, selected modifiers, seat assignment, and KDS station.

    **Requirements:**
    - order_id must reference an existing order
    - product_id must reference an existing product
    - quantity must be >= 1
    - unit_price must be >= 0
    - selected_modifiers is optional (JSONB format)
    - seat_id is optional (for person-level tracking)
    - kds_station is optional (for kitchen display routing)

    **Returns:**
    - 201: Successfully created order item with all details
    - 400: Invalid input data
    - 404: Order or product not found
    """
)
def add_item_to_order(
    order_id: int,
    item_data: OrderItemCreate,
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    Új tétel hozzáadása egy rendeléshez.

    Args:
        order_id: Order identifier (path parameter)
        item_data: OrderItemCreate schema with item details
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        OrderItemResponse: Created order item details

    Raises:
        HTTPException 400: If validation fails
        HTTPException 404: If order or product not found
    """
    try:
        # Ensure order_id from path matches the one in the request body
        if item_data.order_id != order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order ID mismatch: path parameter ({order_id}) does not match request body ({item_data.order_id})"
            )

        # Add item to order
        order_item = service.add_item_to_order(db, item_data)
        return order_item

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while adding the item: {str(e)}"
        )


@router.get(
    "/{order_id}/items",
    response_model=list[OrderItemResponse],
    summary="Get all items for an order",
    description="""
    Retrieve all items belonging to a specific order.

    This endpoint returns all order items associated with the given order ID,
    including product details, quantities, modifiers, and KDS status.

    **Path Parameters:**
    - `order_id`: Unique order identifier (integer)

    **Returns:**
    - 200: List of order items (may be empty if no items exist)
    """
)
def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    Rendeléshez tartozó tételek listázása.

    Args:
        order_id: Order identifier
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        list[OrderItemResponse]: List of order items
    """
    try:
        items = service.get_items_by_order(db, order_id)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving order items: {str(e)}"
        )


@router.get(
    "/items/{item_id}",
    response_model=OrderItemResponse,
    summary="Get order item by ID",
    description="""
    Retrieve a single order item by its unique identifier.

    **Path Parameters:**
    - `item_id`: Unique order item identifier (integer)

    **Returns:**
    - 200: Order item details
    - 404: Order item not found
    """
)
def get_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    Rendelési tétel lekérdezése ID alapján.

    Args:
        item_id: Order item unique identifier
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        OrderItemResponse: Order item details

    Raises:
        HTTPException 404: If order item not found
    """
    item = service.get_item_by_id(db, item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with ID {item_id} not found"
        )

    return item


@router.put(
    "/items/{item_id}",
    response_model=OrderItemResponse,
    summary="Update order item",
    description="""
    Update an existing order item by its ID.

    This endpoint allows partial updates - you only need to provide the fields
    you want to change. All other fields will remain unchanged.

    **Path Parameters:**
    - `item_id`: Unique order item identifier (integer)

    **Request Body:**
    - Any combination of updatable fields (all optional)

    **Returns:**
    - 200: Updated order item details
    - 404: Order item not found
    - 400: Invalid update data
    """
)
def update_order_item(
    item_id: int,
    item_data: OrderItemUpdate,
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    Rendelési tétel frissítése.

    Args:
        item_id: Order item unique identifier
        item_data: OrderItemUpdate schema with fields to update
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        OrderItemResponse: Updated order item details

    Raises:
        HTTPException 404: If order item not found
        HTTPException 400: If validation fails
    """
    try:
        item = service.update_order_item(db, item_id, item_data)

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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the order item: {str(e)}"
        )


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete order item",
    description="""
    Delete an order item by its ID.

    This operation removes the item from the order permanently.

    **Path Parameters:**
    - `item_id`: Unique order item identifier (integer)

    **Returns:**
    - 204: Order item successfully deleted (no content)
    - 404: Order item not found
    """
)
def delete_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    Rendelési tétel törlése.

    Args:
        item_id: Order item unique identifier
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: If order item not found
    """
    success = service.delete_order_item(db, item_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with ID {item_id} not found"
        )

    return None


@router.patch(
    "/items/{item_id}/kds-status",
    response_model=OrderItemResponse,
    summary="Update KDS status of order item",
    description="""
    Update the Kitchen Display System (KDS) status of an order item.

    This endpoint is specifically designed for KDS workflow updates
    (e.g., VÁRAKOZIK -> KÉSZÜL -> KÉSZ -> KISZOLGÁLVA).

    **Path Parameters:**
    - `item_id`: Unique order item identifier (integer)

    **Query Parameters:**
    - `status`: New KDS status (e.g., 'VÁRAKOZIK', 'KÉSZÜL', 'KÉSZ', 'KISZOLGÁLVA')

    **Returns:**
    - 200: Updated order item with new KDS status
    - 404: Order item not found
    - 400: Invalid status value
    """
)
def update_kds_status(
    item_id: int,
    status_value: str = Query(..., alias="status", description="New KDS status"),
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    Rendelési tétel KDS státuszának frissítése.

    Args:
        item_id: Order item unique identifier
        status_value: New KDS status
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        OrderItemResponse: Updated order item details

    Raises:
        HTTPException 404: If order item not found
        HTTPException 400: If status value is invalid
    """
    try:
        item = service.update_kds_status(db, item_id, status_value)

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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating KDS status: {str(e)}"
        )


# Additional endpoints for specific use cases

@router.get(
    "/seats/{seat_id}/items",
    response_model=list[OrderItemResponse],
    summary="Get all items for a seat",
    description="""
    Retrieve all items assigned to a specific seat.

    This endpoint is useful for person-level bill splitting and tracking
    who ordered what at a table.

    **Path Parameters:**
    - `seat_id`: Unique seat identifier (integer)

    **Returns:**
    - 200: List of order items for the seat (may be empty)
    """
)
def get_items_by_seat(
    seat_id: int,
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    Székhelyhez tartozó tételek lekérdezése.

    Args:
        seat_id: Seat identifier
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        list[OrderItemResponse]: List of order items for the seat
    """
    try:
        items = service.get_items_by_seat(db, seat_id)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving seat items: {str(e)}"
        )


@router.get(
    "/kds/stations/{station}/items",
    response_model=list[OrderItemResponse],
    summary="Get items for a KDS station",
    description="""
    Retrieve all items assigned to a specific Kitchen Display System (KDS) station.

    This endpoint is designed for KDS integration, allowing kitchen stations
    to see their assigned items with optional status filtering.

    **Path Parameters:**
    - `station`: KDS station name (e.g., 'Konyha', 'Pizza', 'Pult')

    **Query Parameters:**
    - `kds_status`: Optional KDS status filter (e.g., 'VÁRAKOZIK', 'KÉSZÜL', 'KÉSZ')

    **Returns:**
    - 200: List of order items for the station (may be empty)
    """
)
def get_items_by_kds_station(
    station: str,
    kds_status: Optional[str] = Query(None, description="Filter by KDS status"),
    db: Session = Depends(get_db),
    service: OrderItemService = Depends(get_order_item_service)
):
    """
    KDS állomáshoz tartozó tételek lekérdezése.

    Args:
        station: KDS station name
        kds_status: Optional KDS status filter
        db: Database session (injected)
        service: OrderItemService instance (injected)

    Returns:
        list[OrderItemResponse]: List of order items for the station
    """
    try:
        items = service.get_items_by_kds_station(db, station, kds_status)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving KDS station items: {str(e)}"
        )
