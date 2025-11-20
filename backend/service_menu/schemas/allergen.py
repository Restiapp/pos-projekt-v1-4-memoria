"""
Pydantic schemas for Allergen entities.

This module defines the request and response schemas for allergen operations
in the Menu Service (Module 0).
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class AllergenBase(BaseModel):
    """Base schema for Allergen with common fields."""

    code: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Allergen code (e.g., GL for Gluten, MILK, NUTS)",
        examples=["GL", "MILK", "NUTS", "EGG", "FISH"]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Allergen name",
        examples=["Glutén", "Tej", "Mogyoró", "Tojás", "Hal"]
    )
    icon_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL to allergen icon image",
        examples=["https://example.com/icons/gluten.png"]
    )


class AllergenCreate(AllergenBase):
    """Schema for creating a new allergen."""
    pass


class AllergenUpdate(BaseModel):
    """Schema for updating an existing allergen."""

    code: Optional[str] = Field(
        None,
        min_length=1,
        max_length=10,
        description="Allergen code"
    )
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Allergen name"
    )
    icon_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL to allergen icon image"
    )


class AllergenInDB(AllergenBase):
    """Schema for allergen as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique allergen identifier",
        examples=[1, 42]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when allergen was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when allergen was last updated"
    )


class AllergenResponse(AllergenInDB):
    """Schema for allergen API responses."""
    pass


class AllergenListResponse(BaseModel):
    """Schema for paginated allergen list responses."""

    items: List[AllergenResponse] = Field(
        ...,
        description="List of allergens"
    )
    total: int = Field(
        ...,
        description="Total number of allergens",
        examples=[14]
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


class ProductAllergenAssignment(BaseModel):
    """Schema for assigning allergens to a product."""

    allergen_ids: List[int] = Field(
        ...,
        description="List of allergen IDs to assign to the product",
        examples=[[1, 2, 3], [5, 7]]
    )
