"""
Routers package for Service Orders Module
Module 1: Rendeléskezelés és Asztalok

This package contains all API route handlers for the orders service.
"""

from backend.service_orders.routers.order_items import router as order_items_router

__all__ = [
    "order_items_router"
]
