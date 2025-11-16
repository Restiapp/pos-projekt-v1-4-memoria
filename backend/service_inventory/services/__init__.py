"""
Service Layer - Module 5: Készletkezelés

Ez a modul exportálja az összes service osztályt,
amelyek a készletkezelési rendszer üzleti logikáját implementálják.
"""

from backend.service_inventory.services.inventory_service import InventoryService
from backend.service_inventory.services.recipe_service import RecipeService

__all__ = [
    'InventoryService',
    'RecipeService',
]
