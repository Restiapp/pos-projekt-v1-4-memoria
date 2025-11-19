"""
Pydantic schemas for OrderItem entities.

This module defines the request and response schemas for order item operations
in the Service Orders module (Module 1), including selected modifiers for each item.
"""

from decimal import Decimal
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator


class CourseType(str, Enum):
    """
    Enum for valid course types.

    Defines the allowed values for the 'course' field in order items.
    """
    STARTER = "starter"
    MAIN = "main"
    DESSERT = "dessert"
    DRINK = "drink"
    OTHER = "other"


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
    course: Optional[CourseType] = Field(
        None,
        description="Course type (V3.0: starter, main, dessert, drink, other)",
        examples=["starter", "main", "dessert", "drink"]
    )
    notes: Optional[str] = Field(
        None,
        description="Item-level notes (V3.0)",
        examples=["Extra fűszeres", "Gluténmentes"]
    )
    kds_station: Optional[str] = Field(
        None,
        max_length=50,
        description="Kitchen Display System station assignment (e.g., 'Konyha', 'Pizza', 'Pult')",
        examples=["Konyha", "Pizza", "Pult", "Desszert"]
    )
    kds_status: Optional[str] = Field(
        "VÁRAKOZIK",
        max_length=50,
        description="Kitchen Display System status for this item",
        examples=["VÁRAKOZIK", "KÉSZÜL", "KÉSZ", "KISZOLGÁLVA"]
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
    course: Optional[CourseType] = Field(
        None,
        description="Course type (starter, main, dessert, drink, other)"
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
    kds_status: Optional[str] = Field(
        None,
        max_length=50,
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
