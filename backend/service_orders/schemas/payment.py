"""
Pydantic schemas for Payment entities and Split-Check operations.

This module defines the request and response schemas for payment operations
and split-check functionality in the Service Orders module (Module 4).
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class PaymentBase(BaseModel):
    """Base schema for Payment with common fields."""

    order_id: int = Field(
        ...,
        description="Parent order identifier",
        examples=[1, 42, 100]
    )
    payment_method: str = Field(
        ...,
        max_length=100,
        description="Payment method (e.g., 'Készpénz', 'Bankkártya', 'OTP SZÉP', 'K&H SZÉP', 'MKB SZÉP')",
        examples=["Készpénz", "Bankkártya", "OTP SZÉP", "K&H SZÉP", "MKB SZÉP"]
    )
    amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Payment amount in HUF",
        examples=[2500.00, 1500.00, 8900.00]
    )


class PaymentCreate(PaymentBase):
    """Schema for creating a new payment."""
    pass


class PaymentResponse(PaymentBase):
    """Schema for payment API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique payment identifier",
        examples=[1, 42, 500]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when payment was created"
    )


class SplitCheckItemSchema(BaseModel):
    """
    Schema for a single seat/person's portion in a split check.

    Represents the amount owed by one person when splitting a bill,
    based on the items associated with their seat.
    """

    seat_id: Optional[int] = Field(
        None,
        description="Seat identifier (None for unassigned items)",
        examples=[1, 2, 3, None]
    )
    seat_number: Optional[int] = Field(
        None,
        description="Seat number at the table (None for unassigned items)",
        examples=[1, 2, 3, None]
    )
    person_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total amount owed by this person in HUF",
        examples=[1500.00, 2500.00, 3200.00]
    )
    item_count: int = Field(
        ...,
        ge=0,
        description="Number of order items assigned to this seat",
        examples=[1, 2, 5]
    )


class SplitCheckResponse(BaseModel):
    """
    Schema for split-check API responses.

    Provides a breakdown of how much each person (seat) owes
    when splitting the bill at a table.
    """

    order_id: int = Field(
        ...,
        description="Parent order identifier",
        examples=[1, 42, 100]
    )
    items: List[SplitCheckItemSchema] = Field(
        ...,
        description="List of amounts owed per seat/person"
    )
    total_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total order amount (sum of all split items) in HUF",
        examples=[5000.00, 12500.00, 8900.00]
    )
