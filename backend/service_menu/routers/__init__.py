"""
Routers package for Menu Service API endpoints.

This package contains all API route definitions for the Menu Service module.
"""

from backend.service_menu.routers.products import router as products_router

__all__ = ["products_router"]
