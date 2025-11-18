"""
Pydantic Schemas for Logistics Service (V3.0 Module).

This module exports all Pydantic schemas for the Logistics Service,
including schemas for delivery zones and couriers.
"""

from backend.service_logistics.schemas.delivery_zone import (
    DeliveryZoneBase,
    DeliveryZoneCreate,
    DeliveryZoneUpdate,
    DeliveryZoneInDB,
    DeliveryZoneResponse,
    DeliveryZoneListResponse,
    GetByAddressRequest,
    GetByAddressResponse,
)

from backend.service_logistics.schemas.courier import (
    CourierBase,
    CourierCreate,
    CourierUpdate,
    CourierInDB,
    CourierResponse,
    CourierListResponse,
)

__all__ = [
    # Delivery Zone Schemas
    "DeliveryZoneBase",
    "DeliveryZoneCreate",
    "DeliveryZoneUpdate",
    "DeliveryZoneInDB",
    "DeliveryZoneResponse",
    "DeliveryZoneListResponse",
    "GetByAddressRequest",
    "GetByAddressResponse",
    # Courier Schemas
    "CourierBase",
    "CourierCreate",
    "CourierUpdate",
    "CourierInDB",
    "CourierResponse",
    "CourierListResponse",
]
