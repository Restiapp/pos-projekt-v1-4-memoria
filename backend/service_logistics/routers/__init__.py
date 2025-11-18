"""
API Routers for Logistics Service (V3.0 Module).

This module exports all API routers for the Logistics Service,
including routers for delivery zones and couriers.
"""

from backend.service_logistics.routers.delivery_zone_router import router as delivery_zone_router
from backend.service_logistics.routers.courier_router import router as courier_router

__all__ = [
    "delivery_zone_router",
    "courier_router",
]
