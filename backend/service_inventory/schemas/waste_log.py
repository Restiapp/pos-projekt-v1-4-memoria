"""
Pydantic schemas for WasteLog entities.

This module defines the request and response schemas for waste logging operations
in the Inventory Service (Module 5), including waste tracking and reporting.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class WasteLogBase(BaseModel):
    """Base schema for WasteLog with common fields."""

    inventory_item_id: int = Field(
        ...,
        gt=0,
        description="Inventory item ID that was wasted",
        examples=[1, 42, 100]
    )
    quantity: Decimal = Field(
        ...,
        gt=0,
        decimal_places=3,
        description="Wasted quantity",
        examples=[1.500, 0.250, 10.000]
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Reason for waste (e.g., 'expired', 'damaged', 'quality_issue', 'other')",
        examples=["expired", "damaged", "quality_issue", "other"]
    )
    waste_date: date = Field(
        ...,
        description="Date when the waste occurred",
        examples=["2025-01-20"]
    )
    noted_by: Optional[str] = Field(
        None,
        max_length=100,
        description="Person who noted the waste",
        examples=["Nagy János", "Kiss Anna"]
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional notes about the waste",
        examples=["Lejárt szavatossági idő", "Sérült csomagolás"]
    )


class WasteLogCreate(WasteLogBase):
    """Schema for creating a new waste log entry."""
    pass


class WasteLogInDB(WasteLogBase):
    """Schema for waste log as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique waste log identifier",
        examples=[1, 42, 100]
    )
    created_at: str = Field(
        ...,
        description="Timestamp when the waste log was created",
        examples=["2025-01-20T10:30:00Z"]
    )


class WasteLogResponse(WasteLogInDB):
    """Schema for waste log API responses."""
    pass


class WasteLogListResponse(BaseModel):
    """Schema for paginated waste log list responses."""

    items: list[WasteLogResponse] = Field(
        ...,
        description="List of waste logs"
    )
    total: int = Field(
        ...,
        description="Total number of waste logs",
        examples=[50, 100, 200]
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
