"""
Routers Package - API Endpoints
Module 5: Készletkezelés

API Routers for Service Inventory (Module 5: Készletkezelés).

This package contains all FastAPI routers for the POS Inventory Service.
Ez a csomag tartalmazza a FastAPI router-eket az API végpontokhoz.
"""

from .daily_inventory import daily_inventory_router

__all__ = [
    "daily_inventory_router",
]
