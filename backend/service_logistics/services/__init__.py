"""
Service Layer for Logistics Service (V3.0 Module).

This module exports all service classes for the Logistics Service,
including services for delivery zones and couriers.
"""

from backend.service_logistics.services.delivery_zone_service import (
    DeliveryZoneService,
    delivery_zone_service,
)

from backend.service_logistics.services.courier_service import (
    CourierService,
    courier_service,
)

__all__ = [
    # Delivery Zone Service
    "DeliveryZoneService",
    "delivery_zone_service",
    # Courier Service
    "CourierService",
    "courier_service",
]
