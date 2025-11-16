"""
Routers Package - API Endpoints
Module 5: Inventory Management and AI OCR

This package contains all API endpoints for the Inventory Service.
"""

from backend.service_inventory.routers.invoices import router as invoice_router

__all__ = [
    "invoice_router",
]
