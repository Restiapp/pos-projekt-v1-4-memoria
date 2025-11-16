"""
Pydantic schemas for the Service Orders module (Module 1).

This package contains all request/response schemas for the POS Service Orders,
including tables, seats, orders, order items, and payments.

Usage:
    from backend.service_orders.schemas import (
        TableCreate,
        TableResponse,
        SeatCreate,
        SeatResponse,
        OrderCreate,
        OrderResponse,
        OrderItemCreate,
        OrderItemResponse,
        PaymentCreate,
        PaymentResponse,
        SplitCheckResponse
    )
"""

# Table schemas
from .table import (
    TableBase,
    TableCreate,
    TableUpdate,
    TableInDB,
    TableResponse,
    TableListResponse,
)

# Seat schemas
from .seat import (
    SeatBase,
    SeatCreate,
    SeatUpdate,
    SeatInDB,
    SeatResponse,
    SeatListResponse,
)

# Order schemas
from .order import (
    OrderTypeEnum,
    OrderStatusEnum,
    OrderBase,
    OrderCreate,
    OrderUpdate,
    OrderInDB,
    OrderResponse,
    OrderListResponse,
)

# Order item schemas
from .order_item import (
    SelectedModifierSchema,
    OrderItemBase,
    OrderItemCreate,
    OrderItemUpdate,
    OrderItemInDB,
    OrderItemResponse,
    OrderItemListResponse,
)

# Payment schemas
from .payment import (
    PaymentBase,
    PaymentCreate,
    PaymentResponse,
    SplitCheckItemSchema,
    SplitCheckResponse,
)

__all__ = [
    # Table
    "TableBase",
    "TableCreate",
    "TableUpdate",
    "TableInDB",
    "TableResponse",
    "TableListResponse",
    # Seat
    "SeatBase",
    "SeatCreate",
    "SeatUpdate",
    "SeatInDB",
    "SeatResponse",
    "SeatListResponse",
    # Order
    "OrderTypeEnum",
    "OrderStatusEnum",
    "OrderBase",
    "OrderCreate",
    "OrderUpdate",
    "OrderInDB",
    "OrderResponse",
    "OrderListResponse",
    # OrderItem
    "SelectedModifierSchema",
    "OrderItemBase",
    "OrderItemCreate",
    "OrderItemUpdate",
    "OrderItemInDB",
    "OrderItemResponse",
    "OrderItemListResponse",
    # Payment
    "PaymentBase",
    "PaymentCreate",
    "PaymentResponse",
    "SplitCheckItemSchema",
    "SplitCheckResponse",
]
