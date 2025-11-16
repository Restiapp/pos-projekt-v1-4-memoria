"""
Pydantic schemas for Recipe entities.

This module defines the request and response schemas for recipe operations
in the Inventory Service (Module 5). Recipes define the ingredients (inventory items)
required to produce menu products and their quantities.
"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class RecipeBase(BaseModel):
    """Base schema for Recipe with common fields."""

    product_id: int = Field(
        ...,
        description="Product identifier (from Menu Service)",
        examples=[1, 42, 100]
    )
    inventory_item_id: int = Field(
        ...,
        description="Inventory item identifier (ingredient)",
        examples=[1, 5, 25]
    )
    quantity_used: Decimal = Field(
        ...,
        gt=0,
        decimal_places=3,
        description="Quantity of inventory item used per product unit",
        examples=[0.250, 1.500, 10.000]
    )


class RecipeCreate(RecipeBase):
    """Schema for creating a new recipe."""
    pass


class RecipeUpdate(BaseModel):
    """Schema for updating an existing recipe."""

    product_id: Optional[int] = Field(
        None,
        description="Product identifier"
    )
    inventory_item_id: Optional[int] = Field(
        None,
        description="Inventory item identifier"
    )
    quantity_used: Optional[Decimal] = Field(
        None,
        gt=0,
        decimal_places=3,
        description="Quantity of inventory item used"
    )


class RecipeInDB(RecipeBase):
    """Schema for recipe as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique recipe identifier",
        examples=[1, 42, 100]
    )


class RecipeResponse(RecipeInDB):
    """Schema for recipe API responses."""
    pass


class RecipeDetailResponse(RecipeResponse):
    """
    Schema for detailed recipe response including related entities.

    This can be extended to include product and inventory item details.
    """
    pass


class RecipeListResponse(BaseModel):
    """Schema for paginated recipe list responses."""

    items: list[RecipeResponse] = Field(
        ...,
        description="List of recipes"
    )
    total: int = Field(
        ...,
        description="Total number of recipes",
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
