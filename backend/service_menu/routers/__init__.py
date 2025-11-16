"""
API Routers for Service Menu (Module 0: Terméktörzs és Menü).

This package contains all FastAPI routers for the POS Menu Service.
This package contains all API route definitions for the Menu Service module.
"""

from .categories import router as categories_router
from .products import router as products_router

__all__ = ["categories_router", "products_router"]
