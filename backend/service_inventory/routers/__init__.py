"""
Routers Package - API Endpoints
Module 5: Készletkezelés

API Routers for Service Inventory (Module 5: Készletkezelés).

This package contains all FastAPI routers for the POS Inventory Service.
Ez a csomag tartalmazza a FastAPI router-eket az API végpontokhoz.
"""

from .recipes import router as recipes_router

__all__ = [
    "recipes_router",
]
