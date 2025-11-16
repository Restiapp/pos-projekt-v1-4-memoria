"""
Routers Package - API Endpoints
Module 1: Rendeléskezelés és Asztalok

API Routers for Service Orders (Module 1: Rendeléskezelés és Asztalok).

This package contains all FastAPI routers for the POS Orders Service.
Ez a csomag tartalmazza a FastAPI router-eket az API végpontokhoz.
"""

from .tables import router as tables_router
from .seats import router as seats_router
from backend.service_orders.routers.orders import orders_router
from backend.service_orders.routers.order_items import router as order_items_router

__all__ = [
    "tables_router",
    "seats_router",
    "orders_router",
    "order_items_router",
]
