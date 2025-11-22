"""
Pydantic schemas for Product entities.

This module defines the request and response schemas for product operations
in the Menu Service (Module 0), including multi-language support and channel visibility.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ProductTranslation(BaseModel):
    """Schema for a single language translation."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Translated product name",
        examples=["Cheeseburger", "Hamburger mit Käse"]
    )
    description: Optional[str] = Field(
        None,
        description="Translated product description",
        examples=["Delicious beef burger with cheese", "Leckerer Rindfleisch-Burger mit Käse"]
    )


class ProductBase(BaseModel):
    """Base schema for Product with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Product name in default language (Hungarian)",
        examples=["Sajtos Hamburger", "Coca Cola 0.5L"]
    )
    description: Optional[str] = Field(
        None,
        description="Product description",
        examples=["Marhahúsos hamburger sajttal, salátával és paradicsommal"]
    )
    base_price: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Base price in HUF (before modifiers and channel overrides)",
        examples=[1290.00, 450.00]
    )
    category_id: Optional[int] = Field(
        None,
        description="Category identifier",
        examples=[1, 5]
    )
    sku: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Stock Keeping Unit - unique product identifier",
        examples=["BURG-CHEESE-001", "DRINK-COLA-500"]
    )
    is_active: bool = Field(
        True,
        description="Whether the product is active and available for sale",
        examples=[True, False]
    )


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Product name"
    )
    description: Optional[str] = Field(
        None,
        description="Product description"
    )
    base_price: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Base price in HUF"
    )
    category_id: Optional[int] = Field(
        None,
        description="Category identifier"
    )
    sku: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Stock Keeping Unit"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Product availability status"
    )


class ProductInDB(ProductBase):
    """Schema for product as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique product identifier",
        examples=[1, 42]
    )
    translations: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Multi-language translations (ISO language code -> translation object)",
        examples=[{
            "en": {"name": "Cheeseburger", "description": "Delicious beef burger with cheese"},
            "de": {"name": "Cheeseburger", "description": "Leckerer Rindfleisch-Burger mit Käse"}
        }]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when product was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when product was last updated"
    )

    @field_validator('translations')
    @classmethod
    def validate_translations(cls, v: Optional[Dict[str, Dict[str, Any]]]) -> Optional[Dict[str, Dict[str, Any]]]:
        """Validate that translations follow the expected structure."""
        if v is None:
            return v

        for lang_code, translation in v.items():
            if not isinstance(translation, dict):
                raise ValueError(f"Translation for '{lang_code}' must be a dictionary")
            if 'name' not in translation:
                raise ValueError(f"Translation for '{lang_code}' must contain 'name' field")

        return v


from backend.service_menu.schemas.allergen import AllergenResponse

class ProductResponse(ProductInDB):
    """Schema for product API responses."""
    allergens: List[AllergenResponse] = Field(
        default_factory=list,
        description="List of allergens associated with this product"
    )


class ProductDetailResponse(ProductResponse):
    """
    Schema for detailed product response including related entities.

    This can be extended to include modifier groups, images, and channel visibility.
    """
    pass


class ProductListResponse(BaseModel):
    """Schema for paginated product list responses."""

    items: list[ProductResponse] = Field(
        ...,
        description="List of products"
    )
    total: int = Field(
        ...,
        description="Total number of products",
        examples=[150]
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


class ChannelVisibilityBase(BaseModel):
    """Base schema for channel visibility settings."""

    channel_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Sales channel name",
        examples=["Pult", "Kiszállítás", "Helybeni"]
    )
    product_id: int = Field(
        ...,
        description="Product identifier",
        examples=[1, 42]
    )
    price_override: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Channel-specific price override (if different from base_price)",
        examples=[1500.00, None]
    )
    is_visible: bool = Field(
        True,
        description="Whether the product is visible on this channel",
        examples=[True, False]
    )


class ChannelVisibilityCreate(ChannelVisibilityBase):
    """Schema for creating channel visibility settings."""
    pass


class ChannelVisibilityUpdate(BaseModel):
    """Schema for updating channel visibility settings."""

    price_override: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Channel-specific price override"
    )
    is_visible: Optional[bool] = Field(
        None,
        description="Product visibility on channel"
    )


class ChannelVisibilityResponse(ChannelVisibilityBase):
    """Schema for channel visibility API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique channel visibility record identifier",
        examples=[1]
    )
