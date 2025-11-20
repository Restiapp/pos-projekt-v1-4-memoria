"""
Models Package - SQLAlchemy ORM Models
Module 5: Készletkezelés

Ez a package tartalmazza az összes adatbázis modellt a service_inventory-hez.

Importálás:
    from backend.service_inventory.models import (
        Base,
        InventoryItem,
        Recipe,
        SupplierInvoice,
        DailyInventorySheet,
        DailyInventoryCount,
        WasteLog,
        IncomingInvoice,
        IncomingInvoiceItem,
        InvoiceStatus,
        StockMovement,
        MovementReason
    )
"""

# Import Base first
from backend.service_inventory.models.database import Base

# Import all models
from backend.service_inventory.models.inventory_item import InventoryItem
from backend.service_inventory.models.recipe import Recipe
from backend.service_inventory.models.supplier_invoice import SupplierInvoice
from backend.service_inventory.models.daily_inventory_sheet import (
    DailyInventorySheet,
    DailyInventoryCount,
    daily_inventory_sheet_items
)
from backend.service_inventory.models.waste_log import WasteLog
from backend.service_inventory.models.incoming_invoice import (
    IncomingInvoice,
    IncomingInvoiceItem,
    InvoiceStatus
)
from backend.service_inventory.models.stock_movement import (
    StockMovement,
    MovementReason
)

# Export all models
__all__ = [
    'Base',
    'InventoryItem',
    'Recipe',
    'SupplierInvoice',
    'DailyInventorySheet',
    'DailyInventoryCount',
    'daily_inventory_sheet_items',
    'WasteLog',
    'IncomingInvoice',
    'IncomingInvoiceItem',
    'InvoiceStatus',
    'StockMovement',
    'MovementReason',
]
