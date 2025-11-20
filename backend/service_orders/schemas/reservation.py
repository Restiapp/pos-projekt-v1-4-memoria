"""
Pydantic schemas for Reservation entities.

This module defines the request and response schemas for reservation operations
in the Service Orders module (Module 1).
"""

from typing import Optional
from datetime import date, time, datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ReservationStatus(str, Enum):
    """Reservation status enumeration."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class ReservationBase(BaseModel):
    """Base schema for Reservation with common fields."""

    table_id: int = Field(
        ...,
        description="ID of the table being reserved",
        examples=[1, 5, 10]
    )
    customer_id: Optional[int] = Field(
        None,
        description="CRM customer ID (optional)",
        examples=[42, 123]
    )
    guest_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the guest making the reservation",
        examples=["John Doe", "Jane Smith", "Kovács János"]
    )
    guest_phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Contact phone number",
        examples=["+36 30 123 4567", "06-20-555-1234"]
    )
    guest_email: Optional[EmailStr] = Field(
        None,
        description="Contact email address",
        examples=["john.doe@example.com", "kovacs.janos@email.hu"]
    )
    reservation_date: date = Field(
        ...,
        description="Date of the reservation",
        examples=["2025-01-20", "2025-02-14"]
    )
    reservation_time: time = Field(
        ...,
        description="Time of the reservation",
        examples=["18:00:00", "19:30:00"]
    )
    guest_count: int = Field(
        ...,
        ge=1,
        description="Number of guests",
        examples=[2, 4, 6]
    )
    duration_minutes: Optional[int] = Field(
        120,
        ge=30,
        le=480,
        description="Duration of the reservation in minutes (default: 120)",
        examples=[90, 120, 180]
    )
    status: Optional[ReservationStatus] = Field(
        ReservationStatus.PENDING,
        description="Reservation status",
        examples=["PENDING", "CONFIRMED"]
    )
    special_requests: Optional[str] = Field(
        None,
        description="Special requests or notes",
        examples=["Birthday celebration", "Window table preferred", "Vegetarian menu"]
    )


class ReservationCreate(ReservationBase):
    """Schema for creating a new reservation."""
    pass


class ReservationUpdate(BaseModel):
    """Schema for updating an existing reservation."""

    table_id: Optional[int] = Field(
        None,
        description="ID of the table being reserved"
    )
    customer_id: Optional[int] = Field(
        None,
        description="CRM customer ID"
    )
    guest_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Name of the guest"
    )
    guest_phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Contact phone number"
    )
    guest_email: Optional[EmailStr] = Field(
        None,
        description="Contact email address"
    )
    reservation_date: Optional[date] = Field(
        None,
        description="Date of the reservation"
    )
    reservation_time: Optional[time] = Field(
        None,
        description="Time of the reservation"
    )
    guest_count: Optional[int] = Field(
        None,
        ge=1,
        description="Number of guests"
    )
    duration_minutes: Optional[int] = Field(
        None,
        ge=30,
        le=480,
        description="Duration in minutes"
    )
    status: Optional[ReservationStatus] = Field(
        None,
        description="Reservation status"
    )
    special_requests: Optional[str] = Field(
        None,
        description="Special requests or notes"
    )


class ReservationInDB(ReservationBase):
    """Schema for reservation as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique reservation identifier",
        examples=[1, 42]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when reservation was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when reservation was last updated"
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
        examples=[50]
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
