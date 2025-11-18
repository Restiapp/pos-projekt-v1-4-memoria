"""
Routers Package - FastAPI Router Exports
Module 5: Készletkezelés és AI OCR

Ez a modul exportálja az összes API routert a service_inventory mikroszolgáltatáshoz.

This package contains all API endpoints for the Inventory Service including:
- Inventory Items management
- Invoice/Receipt OCR upload
- Recipes management
- Daily Inventory sheets
- NAV OSA Integration (V3.0/F3.A)
- Internal Service-to-Service API (V3.0/F3.A)
"""

from backend.service_inventory.routers.inventory_items import router as inventory_items_router
from backend.service_inventory.routers.invoices import router as invoice_router
from .recipes import router as recipes_router
from .daily_inventory import daily_inventory_router
from .internal_router import internal_router
from .osa_integration_router import osa_router

__all__ = [
    # Inventory Items Router (Phase 5.1)
    "inventory_items_router",

    # Recipes Router (Phase 5.2)
    "recipes_router",

    # Invoice/OCR Router (Phase 5.3)
    "invoice_router",

    # Daily Inventory Router (Phase 5.4)
    "daily_inventory_router",

    # Internal API Router (V3.0/F3.A - Stock Deduction)
    "internal_router",

    # NAV OSA Integration Router (V3.0/F3.A - NAV Invoice Integration)
    "osa_router",
]
