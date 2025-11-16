"""
Routers Package - API Endpoints
Module 1: Rendeléskezelés és Asztalok

Ez a package tartalmazza az összes FastAPI router-t a Service Orders modulhoz.
"""

from backend.service_orders.routers.orders import orders_router

__all__ = ["orders_router"]
