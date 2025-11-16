"""
Pydantic schemas for Seat entities.

This module defines the request and response schemas for seat operations
in the Service Orders module (Module 1). Seats represent individual seating
positions at a table for person-level order tracking.
"""

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class SeatBase(BaseModel):
    """Base schema for Seat with common fields."""

    table_id: int = Field(
        ...,
        description="Parent table identifier",
        examples=[1, 5, 10]
    )
    seat_number: int = Field(
        ...,
        ge=1,
        description="Seat number within the table (e.g., 1, 2, 3)",
        examples=[1, 2, 3, 4]
    )


class SeatCreate(SeatBase):
    """Schema for creating a new seat."""
    pass


class SeatUpdate(BaseModel):
    """Schema for updating an existing seat."""

    table_id: Optional[int] = Field(
        None,
        description="Parent table identifier"
    )
    seat_number: Optional[int] = Field(
        None,
        ge=1,
        description="Seat number within the table"
    )


class SeatInDB(SeatBase):
    """Schema for seat as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique seat identifier",
        examples=[1, 42]
    )


class SeatResponse(SeatInDB):
    """Schema for seat API responses."""
    pass


class SeatListResponse(BaseModel):
    """Schema for paginated seat list responses."""

    items: list[SeatResponse] = Field(
        ...,
        description="List of seats"
    )
    total: int = Field(
        ...,
        description="Total number of seats",
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
