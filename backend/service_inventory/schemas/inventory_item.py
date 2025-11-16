"""
Pydantic schemas for InventoryItem entities.

This module defines the request and response schemas for inventory item operations
in the Inventory Service (Module 5), including stock tracking and cost management.
"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class InventoryItemBase(BaseModel):
    """Base schema for InventoryItem with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Inventory item name",
        examples=["Marhahús", "Paradicsom", "Liszt"]
    )
    unit: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unit of measurement (e.g., 'kg', 'liter', 'db')",
        examples=["kg", "liter", "db", "gramm"]
    )
    current_stock_perpetual: Decimal = Field(
        default=Decimal("0.000"),
        ge=0,
        decimal_places=3,
        description="Current stock quantity (perpetual/automatic inventory)",
        examples=[10.500, 0.000, 150.250]
    )
    last_cost_per_unit: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Last purchase cost per unit in HUF",
        examples=[1500.00, 250.00, 89.90]
    )


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating a new inventory item."""
    pass


class InventoryItemUpdate(BaseModel):
    """Schema for updating an existing inventory item."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Inventory item name"
    )
    unit: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Unit of measurement"
    )
    current_stock_perpetual: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Current stock quantity"
    )
    last_cost_per_unit: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Last cost per unit in HUF"
    )


class InventoryItemInDB(InventoryItemBase):
    """Schema for inventory item as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique inventory item identifier",
        examples=[1, 42, 100]
    )


class InventoryItemResponse(InventoryItemInDB):
    """Schema for inventory item API responses."""
    pass


class InventoryItemListResponse(BaseModel):
    """Schema for paginated inventory item list responses."""

    items: list[InventoryItemResponse] = Field(
        ...,
        description="List of inventory items"
    )
    total: int = Field(
        ...,
        description="Total number of inventory items",
        examples=[50, 100, 200]
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
