"""
Pydantic schemas for Order entities.

This module defines the request and response schemas for order operations
in the Service Orders module (Module 1), including order types and statuses.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class OrderTypeEnum(str, Enum):
    """Enumeration of order types for different service channels."""

    HELYBEN = "Helyben"  # Dine-in
    ELVITEL = "Elvitel"  # Takeout
    KISZALLITAS = "Kiszállítás"  # Delivery


class OrderStatusEnum(str, Enum):
    """Enumeration of order statuses throughout the order lifecycle."""

    NYITOTT = "NYITOTT"  # Open - order is being built/modified
    FELDOLGOZVA = "FELDOLGOZVA"  # Processed - sent to kitchen
    LEZART = "LEZART"  # Closed - payment completed
    SZTORNO = "SZTORNÓ"  # Cancelled - order was cancelled


class OrderBase(BaseModel):
    """Base schema for Order with common fields."""

    order_type: OrderTypeEnum = Field(
        ...,
        description="Type of order (dine-in, takeout, delivery)",
        examples=["Helyben", "Elvitel", "Kiszállítás"]
    )
    status: OrderStatusEnum = Field(
        OrderStatusEnum.NYITOTT,
        description="Current order status",
        examples=["NYITOTT", "FELDOLGOZVA", "LEZART"]
    )
    table_id: Optional[int] = Field(
        None,
        description="Associated table identifier (for dine-in orders)",
        examples=[1, 5, None]
    )
    customer_id: Optional[int] = Field(
        None,
        description="Customer identifier (V3.0: for CRM integration)",
        examples=[1, 42, None]
    )
    total_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total order amount in HUF (calculated from order items)",
        examples=[2500.00, 4890.00]
    )
    final_vat_rate: Decimal = Field(
        Decimal("27.00"),
        ge=0,
        le=100,
        decimal_places=2,
        description="Final VAT rate for the order (NTAK-compliant, can be switched from 27% to 5%)",
        examples=[27.00, 5.00]
    )
    ntak_data: Optional[Dict[str, Any]] = Field(
        None,
        description="NTAK (National Tax Authority) compliance data for order summary",
        examples=[{
            "order_summary_id": "ORD-2024-001234",
            "timestamp": "2024-01-15T14:30:00Z"
        }]
    )
    notes: Optional[str] = Field(
        None,
        description="Notes for the order (V3.0)",
        examples=["Allergia: mogyoró", "Kérés: extra gyors kiszolgálás"]
    )


class OrderCreate(OrderBase):
    """Schema for creating a new order."""
    pass


class OrderUpdate(BaseModel):
    """Schema for updating an existing order."""

    order_type: Optional[OrderTypeEnum] = Field(
        None,
        description="Order type"
    )
    status: Optional[OrderStatusEnum] = Field(
        None,
        description="Order status"
    )
    table_id: Optional[int] = Field(
        None,
        description="Table identifier"
    )
    customer_id: Optional[int] = Field(
        None,
        description="Customer identifier"
    )
    total_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total order amount"
    )
    final_vat_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        decimal_places=2,
        description="Final VAT rate"
    )
    ntak_data: Optional[Dict[str, Any]] = Field(
        None,
        description="NTAK compliance data"
    )
    notes: Optional[str] = Field(
        None,
        description="Notes for the order"
    )


class OrderInDB(OrderBase):
    """Schema for order as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique order identifier",
        examples=[1, 42, 1234]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when order was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when order was last updated"
    )


class OrderResponse(OrderInDB):
    """Schema for order API responses."""
    pass


class OrderListResponse(BaseModel):
    """Schema for paginated order list responses."""

    items: list[OrderResponse] = Field(
        ...,
        description="List of orders"
    )
    total: int = Field(
        ...,
        description="Total number of orders",
        examples=[250]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
        examples=[1]
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page",
        examples=[20]
    )
