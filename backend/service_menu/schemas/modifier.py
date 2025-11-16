"""
Pydantic schemas for Modifier and ModifierGroup entities.

This module defines the request and response schemas for complex modifiers
in the Menu Service (Module 0), supporting features like required single-choice
selections (e.g., bun type) and optional multi-choice selections (e.g., extra toppings).
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class SelectionType(str, Enum):
    """Enumeration of modifier group selection types."""

    SINGLE_CHOICE_REQUIRED = "SINGLE_CHOICE_REQUIRED"
    SINGLE_CHOICE_OPTIONAL = "SINGLE_CHOICE_OPTIONAL"
    MULTIPLE_CHOICE_OPTIONAL = "MULTIPLE_CHOICE_OPTIONAL"
    MULTIPLE_CHOICE_REQUIRED = "MULTIPLE_CHOICE_REQUIRED"


class ModifierGroupBase(BaseModel):
    """Base schema for ModifierGroup with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Modifier group name",
        examples=["Zsemle típusa", "Extra feltétek", "Méret"]
    )
    selection_type: SelectionType = Field(
        ...,
        description="Type of selection allowed in this group",
        examples=["SINGLE_CHOICE_REQUIRED", "MULTIPLE_CHOICE_OPTIONAL"]
    )
    min_selection: int = Field(
        0,
        ge=0,
        description="Minimum number of modifiers that must be selected",
        examples=[0, 1]
    )
    max_selection: int = Field(
        1,
        ge=1,
        description="Maximum number of modifiers that can be selected",
        examples=[1, 8]
    )

    @field_validator('max_selection')
    @classmethod
    def validate_max_selection(cls, v: int, info) -> int:
        """Ensure max_selection is greater than or equal to min_selection."""
        if 'min_selection' in info.data and v < info.data['min_selection']:
            raise ValueError('max_selection must be greater than or equal to min_selection')
        return v


class ModifierGroupCreate(ModifierGroupBase):
    """Schema for creating a new modifier group."""
    pass


class ModifierGroupUpdate(BaseModel):
    """Schema for updating an existing modifier group."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Modifier group name"
    )
    selection_type: Optional[SelectionType] = Field(
        None,
        description="Type of selection allowed"
    )
    min_selection: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum number of selections"
    )
    max_selection: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum number of selections"
    )


class ModifierGroupInDB(ModifierGroupBase):
    """Schema for modifier group as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique modifier group identifier",
        examples=[1, 42]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when modifier group was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when modifier group was last updated"
    )


class ModifierGroupResponse(ModifierGroupInDB):
    """Schema for modifier group API responses."""
    pass


class ModifierBase(BaseModel):
    """Base schema for Modifier with common fields."""

    group_id: int = Field(
        ...,
        description="Parent modifier group identifier",
        examples=[1, 5]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Modifier name",
        examples=["Szezámos zsemle", "Extra sajt", "Nagy méret"]
    )
    price_modifier: Decimal = Field(
        Decimal("0.00"),
        decimal_places=2,
        description="Price adjustment for this modifier (can be negative for discounts)",
        examples=[0.00, 150.00, -50.00]
    )
    is_default: bool = Field(
        False,
        description="Whether this modifier is selected by default",
        examples=[True, False]
    )


class ModifierCreate(ModifierBase):
    """Schema for creating a new modifier."""
    pass


class ModifierUpdate(BaseModel):
    """Schema for updating an existing modifier."""

    group_id: Optional[int] = Field(
        None,
        description="Parent modifier group identifier"
    )
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Modifier name"
    )
    price_modifier: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Price adjustment"
    )
    is_default: Optional[bool] = Field(
        None,
        description="Default selection status"
    )


class ModifierInDB(ModifierBase):
    """Schema for modifier as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique modifier identifier",
        examples=[1, 42]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when modifier was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when modifier was last updated"
    )


class ModifierResponse(ModifierInDB):
    """Schema for modifier API responses."""
    pass


class ModifierGroupWithModifiers(ModifierGroupResponse):
    """
    Extended modifier group schema including all its modifiers.

    Useful for displaying complete modifier options when building an order.
    """

    modifiers: list[ModifierResponse] = Field(
        default_factory=list,
        description="List of modifiers in this group"
    )


class ModifierGroupListResponse(BaseModel):
    """Schema for paginated modifier group list responses."""

    items: list[ModifierGroupResponse] = Field(
        ...,
        description="List of modifier groups"
    )
    total: int = Field(
        ...,
        description="Total number of modifier groups",
        examples=[25]
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


class ProductModifierGroupAssociation(BaseModel):
    """Schema for associating modifier groups with products."""

    product_id: int = Field(
        ...,
        description="Product identifier",
        examples=[1, 42]
    )
    group_id: int = Field(
        ...,
        description="Modifier group identifier",
        examples=[1, 5]
    )


class ProductModifierGroupAssociationCreate(ProductModifierGroupAssociation):
    """Schema for creating a product-modifier group association."""
    pass


class SelectedModifier(BaseModel):
    """
    Schema for a modifier selected in an order item.

    Used when creating order items to record which modifiers were chosen.
    """

    group_name: str = Field(
        ...,
        description="Modifier group name",
        examples=["Zsemle típusa", "Extra feltétek"]
    )
    modifier_name: str = Field(
        ...,
        description="Selected modifier name",
        examples=["Szezámos zsemle", "Extra sajt"]
    )
    price: Decimal = Field(
        ...,
        decimal_places=2,
        description="Price adjustment from this modifier",
        examples=[0.00, 150.00]
    )
