"""
Routers Package - API Endpoints
Module 1: Rendeléskezelés és Asztalok

API Routers for Service Orders (Module 1: Rendeléskezelés és Asztalok).

This package contains all FastAPI routers for the POS Orders Service.
Ez a csomag tartalmazza a FastAPI router-eket az API végpontokhoz.
"""

from .tables import router as tables_router
from .seats import router as seats_router

__all__ = [
    "tables_router",
    "seats_router",
]
