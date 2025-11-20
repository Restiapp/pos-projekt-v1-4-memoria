"""
Pydantic schemas for Reservation entities.

This module defines the request and response schemas for reservation operations
in the Service Orders module (Module 1).
"""

from typing import Optional
from datetime import datetime, date, time
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator

from backend.service_orders.models.reservation import ReservationStatus, ReservationSource


class ReservationBase(BaseModel):
    """Base schema for Reservation with common fields."""

    table_id: int = Field(
        ...,
        description="ID of the table to reserve",
        examples=[1, 5, 12]
    )
    customer_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the customer making the reservation",
        examples=["Kiss János", "Smith John"]
    )
    customer_phone: Optional[str] = Field(
        None,
        max_length=50,
        description="Phone number of the customer",
        examples=["+36301234567", "06-30-123-4567"]
    )
    customer_email: Optional[EmailStr] = Field(
        None,
        description="Email address of the customer",
        examples=["janos.kiss@example.com"]
    )
    start_time: datetime = Field(
        ...,
        description="Start time of the reservation (timezone-aware)",
        examples=["2025-01-20T18:00:00+01:00"]
    )
    duration_minutes: int = Field(
        120,
        ge=30,
        le=480,
        description="Duration of the reservation in minutes (30 min - 8 hours)",
        examples=[90, 120, 180]
    )
    guest_count: int = Field(
        ...,
        ge=1,
        le=50,
        description="Number of guests",
        examples=[2, 4, 6]
    )
    notes: Optional[str] = Field(
        None,
        description="Special requests or notes for the reservation",
        examples=["Birthday celebration", "Allergy: nuts", "Window seat preferred"]
    )


class ReservationCreate(ReservationBase):
    """Schema for creating a new reservation."""

    source: ReservationSource = Field(
        ReservationSource.MANUAL,
        description="Source of the reservation (MANUAL, AI, WEB)"
    )


class ReservationUpdate(BaseModel):
    """Schema for updating an existing reservation."""

    table_id: Optional[int] = Field(
        None,
        description="New table ID"
    )
    customer_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated customer name"
    )
    customer_phone: Optional[str] = Field(
        None,
        max_length=50,
        description="Updated phone number"
    )
    customer_email: Optional[EmailStr] = Field(
        None,
        description="Updated email address"
    )
    start_time: Optional[datetime] = Field(
        None,
        description="Updated start time"
    )
    duration_minutes: Optional[int] = Field(
        None,
        ge=30,
        le=480,
        description="Updated duration"
    )
    guest_count: Optional[int] = Field(
        None,
        ge=1,
        le=50,
        description="Updated guest count"
    )
    status: Optional[ReservationStatus] = Field(
        None,
        description="Updated status"
    )
    notes: Optional[str] = Field(
        None,
        description="Updated notes"
    )


class ReservationInDB(ReservationBase):
    """Schema for reservation as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique reservation identifier",
        examples=[1, 42]
    )
    status: ReservationStatus = Field(
        ...,
        description="Current status of the reservation"
    )
    source: ReservationSource = Field(
        ...,
        description="Source of the reservation"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the reservation was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the reservation was last updated"
    )


class ReservationResponse(ReservationInDB):
    """Schema for reservation API responses."""
    pass


class ReservationListResponse(BaseModel):
    """Schema for paginated reservation list responses."""

    items: list[ReservationResponse] = Field(
        ...,
        description="List of reservations"
    )
    total: int = Field(
        ...,
        description="Total number of reservations",
        examples=[150]
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


class AvailabilityQuery(BaseModel):
    """Schema for availability query parameters."""

    date: date = Field(
        ...,
        description="Date to check availability",
        examples=["2025-01-20"]
    )
    guests: int = Field(
        ...,
        ge=1,
        le=50,
        description="Number of guests",
        examples=[4]
    )
    duration_minutes: int = Field(
        120,
        ge=30,
        le=480,
        description="Expected duration in minutes",
        examples=[120]
    )


class TimeSlot(BaseModel):
    """Schema for a single available time slot."""

    time: time = Field(
        ...,
        description="Available time slot",
        examples=["18:00:00", "19:30:00"]
    )
    available_tables: list[int] = Field(
        ...,
        description="List of table IDs available at this time",
        examples=[[1, 2, 5], [3, 7]]
    )


class AvailabilityResponse(BaseModel):
    """Schema for availability check response."""

    date: date = Field(
        ...,
        description="Date queried"
    )
    guests: int = Field(
        ...,
        description="Number of guests queried"
    )
    available_slots: list[TimeSlot] = Field(
        ...,
        description="List of available time slots with tables",
        examples=[
            [
                {"time": "18:00:00", "available_tables": [1, 2, 5]},
                {"time": "18:30:00", "available_tables": [1, 3, 7]},
                {"time": "20:00:00", "available_tables": [2, 5, 8]}
            ]
        ]
    )
    message: Optional[str] = Field(
        None,
        description="Additional message (e.g., if restaurant is closed)",
        examples=["Restaurant is closed on this date", "No tables available for the requested party size"]
    )


class ReservationStatusUpdate(BaseModel):
    """Schema for updating only the reservation status."""

    status: ReservationStatus = Field(
        ...,
        description="New status for the reservation"
    )
