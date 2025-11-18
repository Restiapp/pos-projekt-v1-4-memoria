"""
Pydantic schemas for Courier entities.

This module defines the request and response schemas for courier operations
in the Service Logistics module (V3.0 - Phase 2.A).
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, EmailStr

# Import the CourierStatus enum from the model
from backend.service_logistics.models.courier import CourierStatus


class CourierBase(BaseModel):
    """Base schema for Courier with common fields."""

    courier_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Courier's full name",
        examples=["Kovács János", "Nagy Péter", "Tóth Anna"]
    )
    phone: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Courier's phone number (unique)",
        examples=["+36301234567", "+36209876543", "06301234567"]
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Courier's email address (unique, optional)",
        examples=["kovacs.janos@example.com", "courier@delivery.hu"]
    )
    status: CourierStatus = Field(
        default=CourierStatus.OFFLINE,
        description="Current status of the courier",
        examples=["available", "on_delivery", "offline", "break"]
    )
    is_active: bool = Field(
        default=True,
        description="Whether this courier is active in the system"
    )


class CourierCreate(CourierBase):
    """Schema for creating a new courier."""
    pass


class CourierUpdate(BaseModel):
    """Schema for updating an existing courier."""

    courier_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Courier's name"
    )
    phone: Optional[str] = Field(
        None,
        min_length=1,
        max_length=20,
        description="Courier's phone number"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Courier's email address"
    )
    status: Optional[CourierStatus] = Field(
        None,
        description="Courier status"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Active status"
    )


class CourierInDB(CourierBase):
    """Schema for courier as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique courier identifier",
        examples=[1, 42]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the courier was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the courier was last updated"
    )


class CourierResponse(CourierInDB):
    """Schema for courier API responses."""
    pass


class CourierListResponse(BaseModel):
    """Schema for paginated courier list responses."""

    items: list[CourierResponse] = Field(
        ...,
        description="List of couriers"
    )
    total: int = Field(
        ...,
        description="Total number of couriers",
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
