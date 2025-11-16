"""
Order Router - FastAPI Endpoints for Order Management
Module 1: Rendeléskezelés és Asztalok

Ez a router felelős a rendelések REST API végpontjaiért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- NTAK ÁFA váltás végpont (27% -> 5%)

Fázis 5.3 & 5.4: Order Router és NTAK Végpont
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.services.order_service import OrderService
from backend.service_orders.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderStatusEnum,
    OrderTypeEnum
)

# Router létrehozása
orders_router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Order not found"}}
)


@orders_router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="Creates a new order in the system with specified type, status, and table assignment."
)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
) -> OrderResponse:
    """
    Create a new order.

    Args:
        order_data: Order creation data (type, status, table_id, etc.)
        db: Database session (injected)

    Returns:
        OrderResponse: The newly created order

    Raises:
        HTTPException 400: If order data is invalid

    Example request body:
        {
            "order_type": "Helyben",
            "status": "NYITOTT",
            "table_id": 5,
            "total_amount": 0,
            "final_vat_rate": 27.00
        }
    """
    order = OrderService.create_order(db, order_data)
    return OrderResponse.model_validate(order)


@orders_router.get(
    "/",
    response_model=OrderListResponse,
    summary="List all orders",
    description="Retrieve a paginated list of orders with optional filtering by type, status, or table."
)
def get_orders(
    skip: int = Query(0, ge=0, description="Number of orders to skip (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of orders to return"),
    order_type: Optional[OrderTypeEnum] = Query(None, description="Filter by order type"),
    order_status: Optional[OrderStatusEnum] = Query(None, alias="status", description="Filter by status"),
    table_id: Optional[int] = Query(None, description="Filter by table ID"),
    db: Session = Depends(get_db)
) -> OrderListResponse:
    """
    Get a list of orders with optional filtering.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        order_type: Optional filter by order type (Helyben, Elvitel, Kiszállítás)
        order_status: Optional filter by status (NYITOTT, FELDOLGOZVA, LEZART, SZTORNO)
        table_id: Optional filter by table ID
        db: Database session (injected)

    Returns:
        OrderListResponse: Paginated list of orders with metadata

    Example:
        GET /orders?skip=0&limit=20&status=NYITOTT
    """
    # Convert enum to string for service layer
    order_type_str = order_type.value if order_type else None
    status_str = order_status.value if order_status else None

    # Get orders from service
    orders = OrderService.get_orders(
        db,
        skip=skip,
        limit=limit,
        order_type=order_type_str,
        status=status_str,
        table_id=table_id
    )

    # Get total count for pagination
    total = OrderService.count_orders(
        db,
        order_type=order_type_str,
        status=status_str,
        table_id=table_id
    )

    # Calculate page number
    page = (skip // limit) + 1 if limit > 0 else 1

    return OrderListResponse(
        items=[OrderResponse.model_validate(order) for order in orders],
        total=total,
        page=page,
        page_size=limit
    )


@orders_router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    description="Retrieve a single order by its unique identifier."
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
) -> OrderResponse:
    """
    Get a single order by ID.

    Args:
        order_id: The unique order identifier
        db: Database session (injected)

    Returns:
        OrderResponse: The requested order

    Raises:
        HTTPException 404: If order is not found

    Example:
        GET /orders/42
    """
    order = OrderService.get_order(db, order_id)
    return OrderResponse.model_validate(order)


@orders_router.put(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update an order",
    description="Update an existing order's details (status, type, table assignment, etc.)."
)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db)
) -> OrderResponse:
    """
    Update an existing order.

    Args:
        order_id: The unique order identifier
        order_data: Order update data (partial updates supported)
        db: Database session (injected)

    Returns:
        OrderResponse: The updated order

    Raises:
        HTTPException 404: If order is not found
        HTTPException 400: If update data is invalid

    Example request body:
        {
            "status": "FELDOLGOZVA"
        }
    """
    order = OrderService.update_order(db, order_id, order_data)
    return OrderResponse.model_validate(order)


@orders_router.delete(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an order",
    description="Delete an order from the system."
)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete an order.

    Args:
        order_id: The unique order identifier
        db: Database session (injected)

    Returns:
        dict: Confirmation message with deleted order ID

    Raises:
        HTTPException 404: If order is not found
        HTTPException 400: If deletion fails

    Example response:
        {
            "message": "Rendelés sikeresen törölve",
            "order_id": 42
        }
    """
    result = OrderService.delete_order(db, order_id)
    return result


# ============================================================================
# NTAK SPECIFIC ENDPOINTS
# ============================================================================

@orders_router.patch(
    "/{order_id}/status/set-vat-to-local",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="[NTAK] Set VAT to local rate (5%)",
    description="""
    **NTAK Critical Endpoint**: Switch VAT rate from standard (27%) to local consumption rate (5%).

    This endpoint implements NTAK (National Tourism Data Service) compliance for VAT rate switching.
    According to Hungarian tax regulations, orders consumed on-premises can use the reduced 5% VAT rate.

    **Important constraints:**
    - Only works for orders with status "NYITOTT" (Open)
    - Cannot be applied to processed, closed, or cancelled orders
    - Updates NTAK metadata for audit trail

    **NTAK Compliance:**
    - Standard VAT: 27%
    - Local consumption VAT: 5%
    - Switching only allowed for open orders
    """
)
def set_vat_to_local(
    order_id: int,
    db: Session = Depends(get_db)
) -> OrderResponse:
    """
    **[KRITIKUS NTAK VÉGPONT]**

    Switch order VAT rate from 27% to 5% for local consumption.

    This endpoint is critical for NTAK compliance and must only be used
    for orders that are consumed on-premises (helyben fogyasztás).

    Args:
        order_id: The unique order identifier
        db: Database session (injected)

    Returns:
        OrderResponse: The updated order with 5% VAT rate

    Raises:
        HTTPException 404: If order is not found
        HTTPException 400: If order status is not "NYITOTT" (Open)

    Example:
        PATCH /orders/42/status/set-vat-to-local

    Example success response:
        {
            "id": 42,
            "order_type": "Helyben",
            "status": "NYITOTT",
            "final_vat_rate": 5.00,
            "ntak_data": {
                "vat_change_reason": "Helyi felhasználás (NTAK)",
                "previous_vat_rate": "27.00",
                "new_vat_rate": "5.00"
            },
            ...
        }

    Example error response (order not open):
        {
            "detail": "Az ÁFA kulcs csak NYITOTT státuszú rendeléseknél módosítható. Jelenlegi státusz: FELDOLGOZVA"
        }
    """
    # Call the service layer which handles all business logic and validation
    order = OrderService.set_vat_to_local(db, order_id)
    return OrderResponse.model_validate(order)
