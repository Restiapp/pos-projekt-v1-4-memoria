"""
Pydantic schemas for OrderItem entities.

This module defines the request and response schemas for order item operations
in the Service Orders module (Module 1), including selected modifiers for each item.
"""

from decimal import Decimal
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class KDSStatusEnum(str, Enum):
    """Enumeration of Kitchen Display System (KDS) statuses for order items."""

    WAITING = "WAITING"       # Item is waiting to be prepared
    PREPARING = "PREPARING"   # Item is currently being prepared
    READY = "READY"           # Item is ready to be served
    SERVED = "SERVED"         # Item has been served to customer


class SelectedModifierSchema(BaseModel):
    """
    Schema for a modifier selected in an order item.

    Stores the modifier choice made by the customer when ordering a product.
    This is denormalized data stored as JSONB in the database for historical accuracy.
    """

    group_name: str = Field(
        ...,
        description="Modifier group name (e.g., 'Zsemle típusa', 'Extra feltétek')",
        examples=["Zsemle típusa", "Extra feltétek", "Méret"]
    )
    modifier_name: str = Field(
        ...,
        description="Selected modifier name (e.g., 'Szezámos zsemle', 'Extra sajt')",
        examples=["Szezámos zsemle", "Extra sajt", "Nagy méret"]
    )
    price: Decimal = Field(
        ...,
        decimal_places=2,
        description="Price adjustment from this modifier at the time of order",
        examples=[0.00, 150.00, 200.00]
    )


class OrderItemBase(BaseModel):
    """Base schema for OrderItem with common fields."""

    order_id: int = Field(
        ...,
        description="Parent order identifier",
        examples=[1, 42, 100]
    )
    product_id: int = Field(
        ...,
        description="Product identifier from the menu",
        examples=[5, 12, 33]
    )
    seat_id: Optional[int] = Field(
        None,
        description="Seat identifier for person-level order tracking (optional)",
        examples=[1, 2, None]
    )
    quantity: int = Field(
        ...,
        ge=1,
        description="Quantity of this product ordered",
        examples=[1, 2, 3]
    )
    unit_price: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Unit price at the time of order (including modifiers, before quantity multiplication)",
        examples=[1290.00, 450.00, 2100.00]
    )
    selected_modifiers: Optional[List[SelectedModifierSchema]] = Field(
        None,
        description="List of modifiers selected for this order item",
        examples=[[
            {
                "group_name": "Zsemle típusa",
                "modifier_name": "Szezámos zsemle",
                "price": 0.00
            },
            {
                "group_name": "Extra feltétek",
                "modifier_name": "Extra sajt",
                "price": 150.00
            }
        ]]
    )
    course: Optional[str] = Field(
        None,
        max_length=50,
        description="Course type (V3.0: e.g., 'Előétel', 'Főétel', 'Desszert')",
        examples=["Előétel", "Főétel", "Desszert", "Levesek"]
    )
    notes: Optional[str] = Field(
        None,
        description="Item-level notes (V3.0)",
        examples=["Extra fűszeres", "Gluténmentes"]
    )
    kds_station: Optional[str] = Field(
        None,
        max_length=50,
        description="Kitchen Display System station assignment (e.g., 'GRILL', 'COLD', 'BAR')",
        examples=["GRILL", "COLD", "BAR", "DESSERT"]
    )
    kds_status: Optional[KDSStatusEnum] = Field(
        KDSStatusEnum.WAITING,
        description="Kitchen Display System status for this item",
        examples=["WAITING", "PREPARING", "READY", "SERVED"]
    )


class OrderItemCreate(OrderItemBase):
    """Schema for creating a new order item."""
    pass


class OrderItemUpdate(BaseModel):
    """Schema for updating an existing order item."""

    order_id: Optional[int] = Field(
        None,
        description="Parent order identifier"
    )
    product_id: Optional[int] = Field(
        None,
        description="Product identifier"
    )
    seat_id: Optional[int] = Field(
        None,
        description="Seat identifier"
    )
    quantity: Optional[int] = Field(
        None,
        ge=1,
        description="Quantity ordered"
    )
    unit_price: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Unit price"
    )
    selected_modifiers: Optional[List[SelectedModifierSchema]] = Field(
        None,
        description="Selected modifiers list"
    )
    course: Optional[str] = Field(
        None,
        max_length=50,
        description="Course type"
    )
    notes: Optional[str] = Field(
        None,
        description="Item-level notes"
    )
    kds_station: Optional[str] = Field(
        None,
        max_length=50,
        description="KDS station assignment"
    )
    kds_status: Optional[KDSStatusEnum] = Field(
        None,
        description="KDS status"
    )


class OrderItemInDB(OrderItemBase):
    """Schema for order item as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique order item identifier",
        examples=[1, 42, 500]
    )


class OrderItemResponse(OrderItemInDB):
    """Schema for order item API responses."""
    pass


class OrderItemListResponse(BaseModel):
    """Schema for paginated order item list responses."""

    items: list[OrderItemResponse] = Field(
        ...,
        description="List of order items"
    )
    total: int = Field(
        ...,
        description="Total number of order items",
        examples=[500]
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
