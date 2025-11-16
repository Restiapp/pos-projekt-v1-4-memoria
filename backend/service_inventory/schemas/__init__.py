"""
Pydantic schemas for the Inventory Service (Module 5).

This package contains all request/response schemas for the POS Inventory Service,
including inventory items, recipes, supplier invoices, and daily inventory management.

Usage:
    from backend.service_inventory.schemas import (
        InventoryItemCreate,
        InventoryItemResponse,
        RecipeCreate,
        RecipeResponse,
        SupplierInvoiceCreate,
        SupplierInvoiceResponse,
        DailyInventorySheetCreate,
        DailyInventoryCountCreate
    )
"""

# Inventory Item schemas
from .inventory_item import (
    InventoryItemBase,
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemInDB,
    InventoryItemResponse,
    InventoryItemListResponse,
)

# Recipe schemas
from .recipe import (
    RecipeBase,
    RecipeCreate,
    RecipeUpdate,
    RecipeInDB,
    RecipeResponse,
    RecipeDetailResponse,
    RecipeListResponse,
)

# Supplier Invoice schemas
from .supplier_invoice import (
    OCRLineItem,
    OCRData,
    SupplierInvoiceBase,
    SupplierInvoiceCreate,
    SupplierInvoiceUpdate,
    SupplierInvoiceInDB,
    SupplierInvoiceResponse,
    SupplierInvoiceDetailResponse,
    SupplierInvoiceListResponse,
)

# Daily Inventory schemas
from .daily_inventory import (
    DailyInventorySheetBase,
    DailyInventorySheetCreate,
    DailyInventorySheetUpdate,
    DailyInventorySheetInDB,
    DailyInventorySheetResponse,
    DailyInventorySheetDetailResponse,
    DailyInventorySheetListResponse,
    DailyInventoryCountBase,
    CountItem,
    DailyInventoryCountCreate,
    DailyInventoryCountUpdate,
    DailyInventoryCountInDB,
    DailyInventoryCountResponse,
    DailyInventoryCountDetailResponse,
    DailyInventoryCountListResponse,
)

__all__ = [
    # Inventory Item
    "InventoryItemBase",
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "InventoryItemInDB",
    "InventoryItemResponse",
    "InventoryItemListResponse",
    # Recipe
    "RecipeBase",
    "RecipeCreate",
    "RecipeUpdate",
    "RecipeInDB",
    "RecipeResponse",
    "RecipeDetailResponse",
    "RecipeListResponse",
    # Supplier Invoice
    "OCRLineItem",
    "OCRData",
    "SupplierInvoiceBase",
    "SupplierInvoiceCreate",
    "SupplierInvoiceUpdate",
    "SupplierInvoiceInDB",
    "SupplierInvoiceResponse",
    "SupplierInvoiceDetailResponse",
    "SupplierInvoiceListResponse",
    # Daily Inventory Sheet
    "DailyInventorySheetBase",
    "DailyInventorySheetCreate",
    "DailyInventorySheetUpdate",
    "DailyInventorySheetInDB",
    "DailyInventorySheetResponse",
    "DailyInventorySheetDetailResponse",
    "DailyInventorySheetListResponse",
    # Daily Inventory Count
    "DailyInventoryCountBase",
    "CountItem",
    "DailyInventoryCountCreate",
    "DailyInventoryCountUpdate",
    "DailyInventoryCountInDB",
    "DailyInventoryCountResponse",
    "DailyInventoryCountDetailResponse",
    "DailyInventoryCountListResponse",
]
