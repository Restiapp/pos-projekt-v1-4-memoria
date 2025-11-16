"""
Routers Package - FastAPI Router Exports
Module 5: Készletkezelés

Ez a modul exportálja az összes API routert a service_inventory mikroszolgáltatáshoz.
"""

from backend.service_inventory.routers.inventory_items import router as inventory_items_router

__all__ = ["inventory_items_router"]
