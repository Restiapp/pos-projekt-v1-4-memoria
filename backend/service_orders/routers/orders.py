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
from backend.service_orders.services.payment_service import PaymentService
from backend.service_orders.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderStatusEnum,
    OrderTypeEnum,
    OrderTypeChangeRequest,
    OrderTypeChangeResponse,
    CourierAssignmentRequest,
    CourierAssignmentResponse
)
from backend.service_orders.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    SplitCheckResponse
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


# ============================================================================
# PAYMENT ENDPOINTS (Module 4, Phase 5.7)
# ============================================================================

@orders_router.post(
    "/{order_id}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a payment for an order",
    description="""
    Record a new payment for a specific order.

    This endpoint allows recording payments with various payment methods:
    - Készpénz (Cash)
    - Bankkártya (Credit Card)
    - OTP SZÉP, K&H SZÉP, MKB SZÉP (SZÉP card variants)

    The payment is automatically marked as 'SIKERES' (successful).
    """
)
def record_payment(
    order_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db)
) -> PaymentResponse:
    """
    Record a new payment for an order.

    Args:
        order_id: The unique order identifier
        payment_data: Payment creation data (payment_method, amount)
        db: Database session (injected)

    Returns:
        PaymentResponse: The newly recorded payment

    Raises:
        HTTPException 404: If order is not found
        HTTPException 400: If payment recording fails

    Example request body:
        {
            "order_id": 42,
            "payment_method": "Készpénz",
            "amount": 5000.00
        }
    """
    payment = PaymentService.record_payment(db, payment_data)
    return PaymentResponse.model_validate(payment)


@orders_router.get(
    "/{order_id}/payments",
    response_model=List[PaymentResponse],
    summary="Get all payments for an order",
    description="""
    Retrieve all successful payments associated with a specific order.

    Returns a list of all payments that have been recorded for the order,
    including payment methods and amounts.
    """
)
def get_payments(
    order_id: int,
    db: Session = Depends(get_db)
) -> List[PaymentResponse]:
    """
    Get all payments for a specific order.

    Args:
        order_id: The unique order identifier
        db: Database session (injected)

    Returns:
        List[PaymentResponse]: List of all payments for the order

    Raises:
        HTTPException 404: If order is not found

    Example:
        GET /orders/42/payments
    """
    payments = PaymentService.get_payments_for_order(db, order_id)
    return [PaymentResponse.model_validate(payment) for payment in payments]


@orders_router.get(
    "/{order_id}/split-check",
    response_model=SplitCheckResponse,
    summary="Calculate split-check for an order",
    description="""
    Calculate how much each person (seat) owes when splitting the bill.

    This endpoint groups order items by seat_id and calculates the amount
    owed by each person at the table. Useful for splitting bills among
    multiple diners.

    The response includes:
    - Breakdown per seat (seat_id, amount, item count)
    - Total order amount
    """
)
def get_split_check(
    order_id: int,
    db: Session = Depends(get_db)
) -> SplitCheckResponse:
    """
    Calculate split-check for an order based on seat assignments.

    Args:
        order_id: The unique order identifier
        db: Database session (injected)

    Returns:
        SplitCheckResponse: Breakdown of amounts owed per seat

    Raises:
        HTTPException 404: If order is not found

    Example:
        GET /orders/42/split-check

    Example response:
        {
            "order_id": 42,
            "items": [
                {
                    "seat_id": 1,
                    "seat_number": 1,
                    "person_amount": 2500.00,
                    "item_count": 3
                },
                {
                    "seat_id": 2,
                    "seat_number": 2,
                    "person_amount": 3200.00,
                    "item_count": 2
                }
            ],
            "total_amount": 5700.00
        }
    """
    return PaymentService.calculate_split_check(db, order_id)


@orders_router.post(
    "/{order_id}/status/close",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Close an order",
    description="""
    Close an order after verifying it has been fully paid.

    This endpoint performs several critical operations:
    1. Verifies the order is fully paid
    2. Updates order status to 'LEZART' (Closed)
    3. Triggers NTAK data submission
    4. Triggers inventory deduction

    **Important constraints:**
    - Order must be fully paid (total payments >= total amount)
    - Cannot close an already closed order
    - Cannot close a cancelled order
    """
)
def close_order(
    order_id: int,
    db: Session = Depends(get_db)
) -> OrderResponse:
    """
    Close an order after payment verification.

    Args:
        order_id: The unique order identifier
        db: Database session (injected)

    Returns:
        OrderResponse: The closed order

    Raises:
        HTTPException 404: If order is not found
        HTTPException 400: If order is not fully paid or cannot be closed

    Example:
        POST /orders/42/status/close

    Example success response:
        {
            "id": 42,
            "status": "LEZART",
            "total_amount": 5000.00,
            ...
        }

    Example error response (not fully paid):
        {
            "detail": "A rendelés nem zárható le, mert nincs teljesen kifizetve. Rendelés összege: 5000.00 HUF, Befizetett összeg: 3000.00 HUF"
        }
    """
    # The service layer will raise HTTPException(400) if the order is not fully paid
    # We let this exception propagate naturally to the client
    order = OrderService.close_order(db, order_id)
    return OrderResponse.model_validate(order)


# ============================================================================
# ORDER TYPE CHANGE ENDPOINT (V3.0 / Phase 2.C)
# ============================================================================

@orders_router.patch(
    "/{order_id}/change-type",
    response_model=OrderTypeChangeResponse,
    status_code=status.HTTP_200_OK,
    summary="Change order type (Átültetés)",
    description="""
    **V3.0 / Phase 3.B Feature**: Change the order type (Átültetés) from one service channel to another.

    This endpoint allows changing the order type, for example:
    - From "Helyben" (Dine-in) to "Elvitel" (Takeout)
    - From "Helyben" (Dine-in) to "Kiszállítás" (Delivery)
    - From "Elvitel" (Takeout) to "Kiszállítás" (Delivery)
    - Or any other combination

    **Important constraints:**
    - Only works for orders with status "NYITOTT" (Open)
    - Cannot be applied to processed, closed, or cancelled orders
    - The new order type must be different from the current type
    - For "Kiszállítás" type, customer_zip_code is required for delivery zone lookup

    **Side effects:**
    - Notifies service_inventory about the type change (MOCK in Phase 2.C)
    - Checks delivery zone via service_logistics if switching to delivery (REAL in Phase 3.B)
    - Updates NTAK metadata for audit trail
    - Adds a note to the order with the change details

    **Phase 3.B Enhancement**: Real HTTP calls to service_logistics for ZIP code based zone lookup.
    """
)
def change_order_type(
    order_id: int,
    request: OrderTypeChangeRequest,
    db: Session = Depends(get_db)
) -> OrderTypeChangeResponse:
    """
    **[V3.0 / Phase 3.B FEATURE]**

    Change the order type (Átültetés).

    This endpoint is critical for handling customer requests to change
    how they want to receive their order (e.g., switching from dine-in
    to takeout or delivery).

    Args:
        order_id: The unique order identifier
        request: OrderTypeChangeRequest with new_order_type, optional reason, address, and ZIP code
        db: Database session (injected)

    Returns:
        OrderTypeChangeResponse: The updated order with change confirmation

    Raises:
        HTTPException 404: If order is not found
        HTTPException 400: If order status is not "NYITOTT" (Open)
        HTTPException 400: If new type is same as current type
        HTTPException 400: If type change fails

    Example request body (Kiszállítás):
        {
            "new_order_type": "Kiszállítás",
            "reason": "Vevő kérésére",
            "customer_address": "1051 Budapest, Alkotmány utca 12.",
            "customer_zip_code": "1051"
        }

    Example request body (Elvitel):
        {
            "new_order_type": "Elvitel",
            "reason": "Vevő kérésére"
        }

    Example success response:
        {
            "order": {
                "id": 42,
                "order_type": "Kiszállítás",
                "status": "NYITOTT",
                ...
            },
            "previous_type": "Helyben",
            "new_type": "Kiszállítás",
            "message": "Rendelés típusa sikeresen megváltoztatva: Helyben -> Kiszállítás"
        }

    Example error response (order not open):
        {
            "detail": "A rendelés típusa csak NYITOTT státuszú rendeléseknél módosítható. Jelenlegi státusz: FELDOLGOZVA"
        }
    """
    # Call the service layer which handles all business logic and validation
    updated_order, previous_type = OrderService.change_order_type(
        db=db,
        order_id=order_id,
        new_order_type=request.new_order_type.value,
        reason=request.reason,
        customer_address=request.customer_address,
        customer_zip_code=request.customer_zip_code
    )

    # Build the response
    return OrderTypeChangeResponse(
        order=OrderResponse.model_validate(updated_order),
        previous_type=previous_type,
        new_type=request.new_order_type,
        message=f"Rendelés típusa sikeresen megváltoztatva: {previous_type} -> {request.new_order_type.value}"
    )


# ============================================================================
# COURIER ASSIGNMENT ENDPOINT (V3.0 / LOGISTICS-FIX)
# ============================================================================

@orders_router.post(
    "/{order_id}/assign-courier",
    response_model=CourierAssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign courier to order",
    description="""
    **V3.0 / LOGISTICS-FIX Feature**: Assign a courier to a delivery order.

    This endpoint allows assigning a courier from service_logistics to a delivery order.

    **Important constraints:**
    - Only works for orders with type "Kiszállítás" (Delivery)
    - Automatically updates courier status to ON_DELIVERY via service_logistics API

    **Side effects:**
    - Updates the order's courier_id field
    - Calls service_logistics to update courier status to ON_DELIVERY
    - Updates NTAK metadata for audit trail
    - Adds a note to the order with the courier assignment details
    """
)
def assign_courier_to_order(
    order_id: int,
    request: CourierAssignmentRequest,
    db: Session = Depends(get_db)
) -> CourierAssignmentResponse:
    """
    **[V3.0 / LOGISTICS-FIX FEATURE]**

    Assign a courier to a delivery order.

    This endpoint is critical for logistics management, allowing the system
    to track which courier is assigned to which delivery order.

    Args:
        order_id: The unique order identifier
        request: CourierAssignmentRequest with courier_id
        db: Database session (injected)

    Returns:
        CourierAssignmentResponse: The updated order with assigned courier

    Raises:
        HTTPException 404: If order is not found
        HTTPException 400: If order type is not "Kiszállítás"
        HTTPException 400: If courier assignment fails

    Example request body:
        {
            "courier_id": 5
        }

    Example success response:
        {
            "order": {
                "id": 42,
                "order_type": "Kiszállítás",
                "courier_id": 5,
                ...
            },
            "courier_id": 5,
            "message": "Futár sikeresen hozzárendelve a rendeléshez"
        }

    Example error response (not delivery order):
        {
            "detail": "Csak 'Kiszállítás' típusú rendelésekhez lehet futárt rendelni. Jelenlegi típus: Helyben"
        }
    """
    # Call the service layer which handles all business logic and validation
    updated_order = OrderService.assign_courier(
        db=db,
        order_id=order_id,
        courier_id=request.courier_id
    )

    # Build the response
    return CourierAssignmentResponse(
        order=OrderResponse.model_validate(updated_order),
        courier_id=request.courier_id,
        message="Futár sikeresen hozzárendelve a rendeléshez"
    )
