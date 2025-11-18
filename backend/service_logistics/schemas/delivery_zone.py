"""
Pydantic schemas for DeliveryZone entities.

This module defines the request and response schemas for delivery zone operations
in the Service Logistics module (V3.0 - Phase 2.A).
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class DeliveryZoneBase(BaseModel):
    """Base schema for DeliveryZone with common fields."""

    zone_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique zone identifier/name",
        examples=["Downtown", "Belváros", "Kertváros"]
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Detailed description of the delivery zone",
        examples=["Belváros és környéke, 2 km körzetben"]
    )
    delivery_fee: float = Field(
        default=0.0,
        ge=0.0,
        description="Delivery fee for this zone in HUF",
        examples=[0.0, 500.0, 1000.0]
    )
    min_order_value: float = Field(
        default=0.0,
        ge=0.0,
        description="Minimum order value required for delivery in HUF",
        examples=[0.0, 2000.0, 3000.0]
    )
    estimated_delivery_time_minutes: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Estimated delivery time in minutes",
        examples=[15, 30, 45, 60]
    )
    is_active: bool = Field(
        default=True,
        description="Whether this zone is active for deliveries"
    )


class DeliveryZoneCreate(DeliveryZoneBase):
    """Schema for creating a new delivery zone."""
    pass


class DeliveryZoneUpdate(BaseModel):
    """Schema for updating an existing delivery zone."""

    zone_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Zone identifier/name"
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Zone description"
    )
    delivery_fee: Optional[float] = Field(
        None,
        ge=0.0,
        description="Delivery fee in HUF"
    )
    min_order_value: Optional[float] = Field(
        None,
        ge=0.0,
        description="Minimum order value in HUF"
    )
    estimated_delivery_time_minutes: Optional[int] = Field(
        None,
        ge=5,
        le=120,
        description="Estimated delivery time in minutes"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Active status"
    )


class DeliveryZoneInDB(DeliveryZoneBase):
    """Schema for delivery zone as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique delivery zone identifier",
        examples=[1, 42]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the zone was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the zone was last updated"
    )


class DeliveryZoneResponse(DeliveryZoneInDB):
    """Schema for delivery zone API responses."""
    pass


class DeliveryZoneListResponse(BaseModel):
    """Schema for paginated delivery zone list responses."""

    items: list[DeliveryZoneResponse] = Field(
        ...,
        description="List of delivery zones"
    )
    total: int = Field(
        ...,
        description="Total number of delivery zones",
        examples=[25]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
        examples=[1]
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page",
        examples=[20]
    )


# V3.0 - Phase 2.A: MOCK Endpoint for Get-by-Address
class GetByAddressRequest(BaseModel):
    """
    Schema for get-by-address request (V3.0 - Phase 2.A MOCK).

    This is a MOCK implementation. In Phase 3, this will be replaced
    with real Google Maps / GeoJSON logic.
    """

    address: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Customer delivery address",
        examples=[
            "Budapest, Andrássy út 1.",
            "1051 Budapest, Alkotmány utca 12.",
            "Debrecen, Piac utca 45."
        ]
    )


class GetByAddressResponse(BaseModel):
    """
    Schema for get-by-address response (V3.0 - Phase 2.A MOCK).

    This is a MOCK implementation. In Phase 3, this will return
    real zone data based on Google Maps / GeoJSON lookup.
    """

    zone: Optional[DeliveryZoneResponse] = Field(
        None,
        description="Matched delivery zone (or None if not found)"
    )
    message: str = Field(
        ...,
        description="Response message",
        examples=[
            "MOCK: Zone matched for address",
            "MOCK: No zone found for address"
        ]
    )
    mock_mode: bool = Field(
        default=True,
        description="Indicates this is a MOCK response (will be False in Phase 3)"
    )
