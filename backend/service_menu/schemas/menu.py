"""
Pydantic schemas for Menu V1 entities
Sprint D6: Menu Model V1 Implementation

This module defines request/response schemas for:
- MenuCategory
- MenuItem
- MenuItemVariant
- ModifierGroup
- ModifierOption
- ModifierAssignment

Plus aggregated tree schema for menu display.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class SelectionTypeEnum(str, Enum):
    """Selection type for modifier groups"""
    REQUIRED_SINGLE = "REQUIRED_SINGLE"
    OPTIONAL_SINGLE = "OPTIONAL_SINGLE"
    OPTIONAL_MULTIPLE = "OPTIONAL_MULTIPLE"


# ===========================
# MenuCategory Schemas
# ===========================

class MenuCategoryBase(BaseModel):
    """Base schema for MenuCategory with common fields"""
    name: str = Field(..., max_length=255, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID for subcategories")
    position: int = Field(0, description="Display order position")
    is_active: bool = Field(True, description="Active status")


class MenuCategoryCreate(MenuCategoryBase):
    """Schema for creating a new category"""
    pass


class MenuCategoryUpdate(BaseModel):
    """Schema for updating a category (all fields optional)"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None


class MenuCategoryOut(MenuCategoryBase):
    """Schema for category output"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===========================
# MenuItem Schemas
# ===========================

class MenuItemBase(BaseModel):
    """Base schema for MenuItem with common fields"""
    category_id: Optional[int] = Field(None, description="Category ID")
    name: str = Field(..., max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    base_price_gross: Decimal = Field(..., ge=0, decimal_places=2, description="Base price including VAT")
    vat_rate_dine_in: Decimal = Field(Decimal("5.00"), ge=0, le=100, decimal_places=2, description="VAT rate for dine-in (%)")
    vat_rate_takeaway: Decimal = Field(Decimal("27.00"), ge=0, le=100, decimal_places=2, description="VAT rate for takeaway (%)")
    is_active: bool = Field(True, description="Active status")
    channel_flags: Optional[Dict[str, bool]] = Field(None, description="Channel availability flags")
    metadata_json: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MenuItemCreate(MenuItemBase):
    """Schema for creating a new menu item"""
    pass


class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item (all fields optional)"""
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    base_price_gross: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    vat_rate_dine_in: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    vat_rate_takeaway: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    is_active: Optional[bool] = None
    channel_flags: Optional[Dict[str, bool]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class MenuItemOut(MenuItemBase):
    """Schema for menu item output"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===========================
# MenuItemVariant Schemas
# ===========================

class MenuItemVariantBase(BaseModel):
    """Base schema for MenuItemVariant with common fields"""
    item_id: int = Field(..., description="Parent item ID")
    name: str = Field(..., max_length=255, description="Variant name")
    price_delta: Decimal = Field(Decimal("0.00"), decimal_places=2, description="Price difference from base")
    is_default: bool = Field(False, description="Is this the default variant?")
    is_active: bool = Field(True, description="Active status")


class MenuItemVariantCreate(MenuItemVariantBase):
    """Schema for creating a new variant"""
    pass


class MenuItemVariantUpdate(BaseModel):
    """Schema for updating a variant (all fields optional)"""
    item_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=255)
    price_delta: Optional[Decimal] = Field(None, decimal_places=2)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class MenuItemVariantOut(MenuItemVariantBase):
    """Schema for variant output"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===========================
# ModifierGroup Schemas
# ===========================

class ModifierGroupBase(BaseModel):
    """Base schema for ModifierGroup with common fields"""
    name: str = Field(..., max_length=255, description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    selection_type: SelectionTypeEnum = Field(SelectionTypeEnum.OPTIONAL_MULTIPLE, description="Selection type")
    min_select: int = Field(0, ge=0, description="Minimum selections required")
    max_select: Optional[int] = Field(None, ge=0, description="Maximum selections allowed (null = unlimited)")
    position: int = Field(0, description="Display order position")
    is_active: bool = Field(True, description="Active status")


class ModifierGroupCreate(ModifierGroupBase):
    """Schema for creating a new modifier group"""
    pass


class ModifierGroupUpdate(BaseModel):
    """Schema for updating a modifier group (all fields optional)"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    selection_type: Optional[SelectionTypeEnum] = None
    min_select: Optional[int] = Field(None, ge=0)
    max_select: Optional[int] = Field(None, ge=0)
    position: Optional[int] = None
    is_active: Optional[bool] = None


class ModifierGroupOut(ModifierGroupBase):
    """Schema for modifier group output"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===========================
# ModifierOption Schemas
# ===========================

class ModifierOptionBase(BaseModel):
    """Base schema for ModifierOption with common fields"""
    group_id: int = Field(..., description="Parent group ID")
    name: str = Field(..., max_length=255, description="Option name")
    price_delta_gross: Decimal = Field(Decimal("0.00"), decimal_places=2, description="Price difference from base")
    is_default: bool = Field(False, description="Is this the default option?")
    is_active: bool = Field(True, description="Active status")
    metadata_json: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ModifierOptionCreate(ModifierOptionBase):
    """Schema for creating a new modifier option"""
    pass


class ModifierOptionUpdate(BaseModel):
    """Schema for updating a modifier option (all fields optional)"""
    group_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=255)
    price_delta_gross: Optional[Decimal] = Field(None, decimal_places=2)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    metadata_json: Optional[Dict[str, Any]] = None


class ModifierOptionOut(ModifierOptionBase):
    """Schema for modifier option output"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===========================
# ModifierAssignment Schemas
# ===========================

class ModifierAssignmentBase(BaseModel):
    """Base schema for ModifierAssignment with common fields"""
    group_id: int = Field(..., description="Modifier group ID")
    item_id: Optional[int] = Field(None, description="Menu item ID (if item-level assignment)")
    category_id: Optional[int] = Field(None, description="Category ID (if category-level assignment)")
    applies_to_variants: bool = Field(True, description="Apply to item variants?")
    is_required_override: Optional[bool] = Field(None, description="Override group's required status")
    position: int = Field(0, description="Display order position")


class ModifierAssignmentCreate(ModifierAssignmentBase):
    """Schema for creating a new modifier assignment"""
    pass


class ModifierAssignmentUpdate(BaseModel):
    """Schema for updating a modifier assignment (all fields optional)"""
    group_id: Optional[int] = None
    item_id: Optional[int] = None
    category_id: Optional[int] = None
    applies_to_variants: Optional[bool] = None
    is_required_override: Optional[bool] = None
    position: Optional[int] = None


class ModifierAssignmentOut(ModifierAssignmentBase):
    """Schema for modifier assignment output"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===========================
# Aggregated Tree Schemas
# ===========================

class ModifierOptionTreeOut(BaseModel):
    """Nested modifier option for tree view"""
    id: int
    name: str
    price_delta_gross: Decimal
    is_default: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ModifierGroupTreeOut(BaseModel):
    """Nested modifier group for tree view"""
    id: int
    name: str
    description: Optional[str]
    selection_type: SelectionTypeEnum
    min_select: int
    max_select: Optional[int]
    position: int
    is_active: bool
    options: List[ModifierOptionTreeOut] = []

    model_config = ConfigDict(from_attributes=True)


class MenuItemVariantTreeOut(BaseModel):
    """Nested variant for tree view"""
    id: int
    name: str
    price_delta: Decimal
    is_default: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class MenuItemTreeOut(BaseModel):
    """Nested menu item for tree view"""
    id: int
    name: str
    description: Optional[str]
    base_price_gross: Decimal
    vat_rate_dine_in: Decimal
    vat_rate_takeaway: Decimal
    is_active: bool
    channel_flags: Optional[Dict[str, bool]]
    metadata_json: Optional[Dict[str, Any]]
    variants: List[MenuItemVariantTreeOut] = []
    modifier_groups: List[ModifierGroupTreeOut] = []

    model_config = ConfigDict(from_attributes=True)


class MenuCategoryTreeOut(BaseModel):
    """Full category tree with nested items, variants, and modifiers"""
    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    position: int
    is_active: bool
    items: List[MenuItemTreeOut] = []
    subcategories: List['MenuCategoryTreeOut'] = []  # Self-referencing for hierarchy

    model_config = ConfigDict(from_attributes=True)


# Enable self-referencing for MenuCategoryTreeOut
MenuCategoryTreeOut.model_rebuild()
