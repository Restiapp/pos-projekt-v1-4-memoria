"""
Pydantic schemas for Payment entities and Split-Check operations.

This module defines the request and response schemas for payment operations
and split-check functionality in the Service Orders module (Module 4).
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator


class PaymentMethodEnum(str, Enum):
    """
    Supported payment methods in the POS system.

    Maps user-friendly codes to internal method names.
    """
    CASH = "cash"
    CARD = "card"
    SZEP_CARD = "szep_card"
    TRANSFER = "transfer"
    VOUCHER = "voucher"


class PaymentBase(BaseModel):
    """Base schema for Payment with common fields."""

    payment_method: str = Field(
        ...,
        max_length=100,
        description="Payment method (e.g., 'cash', 'card', 'szep_card', 'transfer', 'voucher')",
        examples=["cash", "card", "szep_card"]
    )
    amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Payment amount in HUF",
        examples=[2500.00, 1500.00, 8900.00]
    )


class PaymentCreate(PaymentBase):
    """Schema for creating a new payment (single payment)."""
    pass


class SplitPaymentRequest(BaseModel):
    """
    Schema for split payment requests.

    Allows recording multiple payments for an order in a single request.
    The total of all payments must match the order's total_amount.
    """
    payments: List[PaymentBase] = Field(
        ...,
        min_length=1,
        description="List of payments to record (must sum to order total)",
        examples=[[
            {"payment_method": "cash", "amount": 3000.00},
            {"payment_method": "card", "amount": 2000.00}
        ]]
    )

    @field_validator('payments')
    @classmethod
    def validate_payments_not_empty(cls, v):
        """Ensure at least one payment is provided."""
        if not v:
            raise ValueError("At least one payment must be provided")
        return v


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


class PaymentMethodInfo(BaseModel):
    """
    Schema for payment method information.

    Provides details about a single payment method supported by the system.
    """
    code: str = Field(
        ...,
        description="Payment method code (e.g., 'cash', 'card', 'szep_card')",
        examples=["cash", "card", "szep_card"]
    )
    display_name: str = Field(
        ...,
        description="Human-readable display name",
        examples=["Készpénz", "Bankkártya", "SZÉP kártya"]
    )
    enabled: bool = Field(
        default=True,
        description="Whether this payment method is currently enabled"
    )


class PaymentMethodsResponse(BaseModel):
    """
    Schema for GET /payments/methods response.

    Returns list of available payment methods.
    """
    methods: List[PaymentMethodInfo] = Field(
        ...,
        description="List of available payment methods"
    )


class SplitPaymentResponse(BaseModel):
    """
    Schema for split payment operation responses.

    Returns information about all recorded payments and validation results.
    """
    order_id: int = Field(
        ...,
        description="Order identifier",
        examples=[42, 100]
    )
    payments: List[PaymentResponse] = Field(
        ...,
        description="List of successfully recorded payments"
    )
    total_paid: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total amount paid across all payments",
        examples=[5000.00, 8900.00]
    )
    order_total: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Order's total amount",
        examples=[5000.00, 8900.00]
    )
    fully_paid: bool = Field(
        ...,
        description="Whether the order is now fully paid"
    )
