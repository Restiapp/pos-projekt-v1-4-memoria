"""
Pydantic schemas for the Menu Service (Module 0).

This package contains all request/response schemas for the POS Menu Service,
including categories, products, modifiers, and image assets.

Usage:
    from backend.service_menu.schemas import (
        CategoryCreate,
        CategoryResponse,
        ProductCreate,
        ProductResponse,
        ModifierGroupCreate,
        ModifierResponse,
        ImageAssetCreate,
        ImageAssetResponse
    )
"""

# Category schemas
from .category import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryInDB,
    CategoryResponse,
    CategoryListResponse,
)

# Product schemas
from .product import (
    ProductTranslation,
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductInDB,
    ProductResponse,
    ProductDetailResponse,
    ProductListResponse,
    ChannelVisibilityBase,
    ChannelVisibilityCreate,
    ChannelVisibilityUpdate,
    ChannelVisibilityResponse,
)

# Modifier schemas
from .modifier import (
    SelectionType,
    ModifierGroupBase,
    ModifierGroupCreate,
    ModifierGroupUpdate,
    ModifierGroupInDB,
    ModifierGroupResponse,
    ModifierBase,
    ModifierCreate,
    ModifierUpdate,
    ModifierInDB,
    ModifierResponse,
    ModifierGroupWithModifiers,
    ModifierGroupListResponse,
    ProductModifierGroupAssociation,
    ProductModifierGroupAssociationCreate,
    SelectedModifier,
)

# Image asset schemas
from .image_asset import (
    ImageSize,
    ImageAssetBase,
    ImageAssetCreate,
    ImageAssetUpdate,
    ImageAssetInDB,
    ImageAssetResponse,
    ImageAssetListResponse,
    SignedUploadUrl,
    SignedUploadUrlRequest,
    ImageProcessingStatus,
    ImageProcessingEvent,
)

__all__ = [
    # Category
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryInDB",
    "CategoryResponse",
    "CategoryListResponse",
    # Product
    "ProductTranslation",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductInDB",
    "ProductResponse",
    "ProductDetailResponse",
    "ProductListResponse",
    "ChannelVisibilityBase",
    "ChannelVisibilityCreate",
    "ChannelVisibilityUpdate",
    "ChannelVisibilityResponse",
    # Modifier
    "SelectionType",
    "ModifierGroupBase",
    "ModifierGroupCreate",
    "ModifierGroupUpdate",
    "ModifierGroupInDB",
    "ModifierGroupResponse",
    "ModifierBase",
    "ModifierCreate",
    "ModifierUpdate",
    "ModifierInDB",
    "ModifierResponse",
    "ModifierGroupWithModifiers",
    "ModifierGroupListResponse",
    "ProductModifierGroupAssociation",
    "ProductModifierGroupAssociationCreate",
    "SelectedModifier",
    # ImageAsset
    "ImageSize",
    "ImageAssetBase",
    "ImageAssetCreate",
    "ImageAssetUpdate",
    "ImageAssetInDB",
    "ImageAssetResponse",
    "ImageAssetListResponse",
    "SignedUploadUrl",
    "SignedUploadUrlRequest",
    "ImageProcessingStatus",
    "ImageProcessingEvent",
]
