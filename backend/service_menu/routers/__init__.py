"""
Routers Package - API Endpoints
Module 0: Terméktörzs és Menü

API Routers for Service Menu (Module 0: Terméktörzs és Menü).

This package contains all FastAPI routers for the POS Menu Service.
This package contains all API route definitions for the Menu Service module.
Ez a csomag tartalmazza a FastAPI router-eket az API végpontokhoz.
"""

from .categories import router as categories_router
from .products import router as products_router
from .modifier_groups import router as modifier_groups_router
from .channels import router as channels_router

__all__ = ["categories_router", "products_router", "modifier_groups_router", "channels_router"]
