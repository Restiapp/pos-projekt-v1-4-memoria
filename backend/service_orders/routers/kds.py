"""
KDS API Routes - Kitchen Display System
Module 1: Rendeléskezelés és Asztalok / Epic B: Konyha/KDS

Ez a modul tartalmazza a Kitchen Display System (KDS) API végpontjait.
Támogatja a konyhai tételek listázását, státusz frissítését és automatikus
rendelés státusz kezelést.

Epic B1: KDS Backend Core Implementation
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.services.kds_service import KDSService
from backend.service_orders.schemas.order_item import (
    OrderItemResponse,
    KDSStatusEnum
)


# Router létrehozása
router = APIRouter(
    prefix="/kds",
    tags=["kds"]
)


def get_kds_service() -> KDSService:
    """
    Dependency function a KDSService injektálásához.

    Returns:
        KDSService: KDS service instance
    """
    return KDSService()


@router.get(
    "/active-items",
    response_model=List[Dict[str, Any]],
    summary="Get active KDS items",
    description="""
    Retrieve all active (non-SERVED) order items for the Kitchen Display System.

    Items are grouped by table/order and can be filtered by KDS station.
    This endpoint is designed for kitchen displays to show pending orders.

    **Query Parameters:**
    - `station`: Optional filter by KDS station (e.g., 'GRILL', 'COLD', 'BAR')

    **Returns:**
    - 200: List of orders with their active items, grouped by table/order

    **Response Structure:**
    ```json
    [
        {
            "order_id": 1,
            "table_id": 5,
            "table_number": "T5",
            "order_type": "Helyben",
            "order_status": "NYITOTT",
            "created_at": "2024-01-15T14:30:00",
            "items": [
                {
                    "id": 1,
                    "product_id": 10,
                    "quantity": 2,
                    "kds_status": "WAITING",
                    "kds_station": "GRILL",
                    ...
                }
            ]
        }
    ]
    ```

    **Use Cases:**
    - Kitchen display screens showing pending orders
    - Station-specific displays (e.g., only GRILL items)
    - Real-time order monitoring
    """
)
def get_active_items(
    station: Optional[str] = Query(
        None,
        description="Filter by KDS station (e.g., 'GRILL', 'COLD', 'BAR')",
        examples=["GRILL", "COLD", "BAR"]
    ),
    db: Session = Depends(get_db),
    service: KDSService = Depends(get_kds_service)
):
    """
    Aktív (nem SERVED) tételek lekérdezése a KDS számára.

    Args:
        station: Opcionális KDS állomás szűrés
        db: Database session (injected)
        service: KDSService instance (injected)

    Returns:
        List[Dict]: Csoportosított rendelések listája az aktív tételekkel
    """
    try:
        active_items = service.get_active_items(db, station)
        return active_items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving active items: {str(e)}"
        )


@router.patch(
    "/items/{item_id}/status",
    response_model=OrderItemResponse,
    summary="Update KDS item status",
    description="""
    Update the Kitchen Display System status of an order item.

    This endpoint updates the KDS status of an item and automatically updates
    the order status to FELDOLGOZVA (Processed) if all items become READY.

    **Path Parameters:**
    - `item_id`: Unique order item identifier (integer)

    **Request Body:**
    - `status`: New KDS status (WAITING, PREPARING, READY, SERVED)

    **Status Workflow:**
    1. WAITING - Item is waiting to be prepared
    2. PREPARING - Item is currently being prepared
    3. READY - Item is ready to be served
    4. SERVED - Item has been served to customer

    **Business Logic:**
    - When an item status is updated to READY
    - If ALL items in the order are READY
    - The order status is automatically updated to FELDOLGOZVA

    **Returns:**
    - 200: Updated order item with new KDS status
    - 400: Invalid status value
    - 404: Order item not found

    **Example Request:**
    ```json
    {
        "status": "PREPARING"
    }
    ```
    """
)
def update_item_status(
    item_id: int,
    status: KDSStatusEnum = Body(
        ...,
        description="New KDS status",
        embed=True,
        examples=["WAITING", "PREPARING", "READY", "SERVED"]
    ),
    db: Session = Depends(get_db),
    service: KDSService = Depends(get_kds_service)
):
    """
    Tétel KDS státuszának frissítése.

    Automatikusan frissíti a rendelés státuszát is, ha minden tétel READY.

    Args:
        item_id: Order item unique identifier
        status: New KDS status (KDSStatusEnum)
        db: Database session (injected)
        service: KDSService instance (injected)

    Returns:
        OrderItemResponse: Updated order item details

    Raises:
        HTTPException 404: If order item not found
        HTTPException 400: If status value is invalid
    """
    try:
        item = service.update_item_status(db, item_id, status)

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


@router.get(
    "/stations/{station}/items",
    response_model=List[OrderItemResponse],
    summary="Get items by KDS station",
    description="""
    Retrieve all items assigned to a specific KDS station with optional status filtering.

    This endpoint is useful for station-specific displays and filtering.

    **Path Parameters:**
    - `station`: KDS station name (e.g., 'GRILL', 'COLD', 'BAR')

    **Query Parameters:**
    - `kds_status`: Optional status filter (WAITING, PREPARING, READY, SERVED)

    **Returns:**
    - 200: List of order items for the station
    """
)
def get_items_by_station(
    station: str,
    kds_status: Optional[KDSStatusEnum] = Query(
        None,
        description="Filter by KDS status"
    ),
    db: Session = Depends(get_db),
    service: KDSService = Depends(get_kds_service)
):
    """
    KDS állomáshoz tartozó tételek lekérdezése státusz szűréssel.

    Args:
        station: KDS station name
        kds_status: Optional KDS status filter
        db: Database session (injected)
        service: KDSService instance (injected)

    Returns:
        List[OrderItemResponse]: List of order items for the station
    """
    try:
        items = service.get_items_by_station_and_status(db, station, kds_status)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving station items: {str(e)}"
        )


@router.patch(
    "/items/{item_id}/urgent",
    response_model=OrderItemResponse,
    summary="Toggle urgent flag for KDS item",
    description="""
    Toggle the urgent flag for a Kitchen Display System item.

    This endpoint allows waiters to mark drinks or other items as urgent,
    which will display them with visual priority indicators (red border, flashing icon)
    in the KDS display.

    **Path Parameters:**
    - `item_id`: Unique order item identifier (integer)

    **Request Body:**
    - `is_urgent`: Boolean flag (true/false)

    **Returns:**
    - 200: Updated order item with new urgent flag
    - 404: Order item not found

    **Example Request:**
    ```json
    {
        "is_urgent": true
    }
    ```

    **Use Cases:**
    - Marking urgent drink orders at the bar
    - Priority handling for time-sensitive items
    - VIP customer orders
    """
)
def toggle_urgent_flag(
    item_id: int,
    is_urgent: bool = Body(
        ...,
        description="Urgent flag value",
        embed=True,
        examples=[True, False]
    ),
    db: Session = Depends(get_db),
    service: KDSService = Depends(get_kds_service)
):
    """
    Toggle urgent flag for a KDS item.

    Args:
        item_id: Order item unique identifier
        is_urgent: New urgent flag value (True/False)
        db: Database session (injected)
        service: KDSService instance (injected)

    Returns:
        OrderItemResponse: Updated order item details

    Raises:
        HTTPException 404: If order item not found
    """
    try:
        item = service.toggle_urgent_flag(db, item_id, is_urgent)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order item with ID {item_id} not found"
            )

        return item

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while toggling urgent flag: {str(e)}"
        )
