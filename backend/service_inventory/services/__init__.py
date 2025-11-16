"""
Service Layer - Module 5: Készletkezelés

Ez a modul exportálja az összes service osztályt,
amelyek a készletkezelési rendszer üzleti logikáját implementálják.

This module exports business logic services including:
- OCR Service for invoice processing using Google Cloud Document AI
- Inventory Service for managing inventory items
- Recipe Service for managing recipes and ingredients
"""

from backend.service_inventory.services.ocr_service import OcrService, ocr_service
from backend.service_inventory.services.inventory_service import InventoryService
from backend.service_inventory.services.recipe_service import RecipeService

__all__ = [
    # OCR Service (Phase 4.3)
    "OcrService",
    "ocr_service",

    # Inventory Service (Phase 4.1)
    "InventoryService",

    # Recipe Service (Phase 4.2)
    "RecipeService",
]
