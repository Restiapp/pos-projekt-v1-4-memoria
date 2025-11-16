"""
API Routers for Service Menu (Module 0: Terméktörzs és Menü).

This package contains all FastAPI routers for the POS Menu Service.
"""

from .categories import router as categories_router

__all__ = ["categories_router"]
