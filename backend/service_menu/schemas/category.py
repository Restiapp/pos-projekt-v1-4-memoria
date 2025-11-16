"""
Pydantic schemas for Category entities.

This module defines the request and response schemas for category operations
in the Menu Service (Module 0).
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    """Base schema for Category with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Category name",
        examples=["Hamburgerek", "Italok", "Desszertek"]
    )
    parent_id: Optional[int] = Field(
        None,
        description="Parent category ID for hierarchical categorization",
        examples=[1, None]
    )


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Category name"
    )
    parent_id: Optional[int] = Field(
        None,
        description="Parent category ID for hierarchical categorization"
    )


class CategoryInDB(CategoryBase):
    """Schema for category as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique category identifier",
        examples=[1, 42]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when category was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when category was last updated"
    )


class CategoryResponse(CategoryInDB):
    """Schema for category API responses."""
    pass


class CategoryListResponse(BaseModel):
    """Schema for paginated category list responses."""

    items: list[CategoryResponse] = Field(
        ...,
        description="List of categories"
    )
    total: int = Field(
        ...,
        description="Total number of categories",
        examples=[42]
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
