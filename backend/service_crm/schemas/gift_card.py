"""
Pydantic schemas for Gift Card entities.

This module defines the request and response schemas for gift card operations
in the Service CRM module (Module 5).
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class GiftCardBase(BaseModel):
    """Base schema for Gift Card with common fields."""

    card_code: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique gift card code",
        examples=["GIFT-2024-ABC123", "GC-XYZ789"]
    )
    pin_code: Optional[str] = Field(
        None,
        max_length=10,
        description="Optional PIN code for security",
        examples=["1234", "9876"]
    )
    initial_balance: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Initial balance amount (HUF)",
        examples=[5000.00, 10000.00, 50000.00]
    )
    valid_until: Optional[datetime] = Field(
        None,
        description="Expiration date/time (null = no expiration)"
    )
    is_active: bool = Field(
        True,
        description="Whether the gift card is currently active"
    )


class GiftCardCreate(GiftCardBase):
    """Schema for creating a new gift card."""

    customer_id: Optional[int] = Field(
        None,
        gt=0,
        description="Customer ID to assign gift card to (null = unassigned)"
    )
    purchased_by_customer_id: Optional[int] = Field(
        None,
        gt=0,
        description="Customer ID who purchased the gift card"
    )
    purchase_order_id: Optional[int] = Field(
        None,
        gt=0,
        description="Order ID where gift card was purchased"
    )


class GiftCardUpdate(BaseModel):
    """Schema for updating an existing gift card."""

    pin_code: Optional[str] = Field(
        None,
        max_length=10,
        description="Update PIN code"
    )
    valid_until: Optional[datetime] = Field(
        None,
        description="Update expiration date/time"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Update active status"
    )
    customer_id: Optional[int] = Field(
        None,
        gt=0,
        description="Assign/reassign to customer"
    )


class GiftCardInDB(GiftCardBase):
    """Schema for gift card as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique gift card identifier",
        examples=[1, 42, 1234]
    )
    customer_id: Optional[int] = Field(
        None,
        description="Customer ID (null if unassigned)"
    )
    current_balance: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Current remaining balance (HUF)"
    )
    purchased_by_customer_id: Optional[int] = Field(
        None,
        description="Customer ID who purchased the gift card"
    )
    purchase_order_id: Optional[int] = Field(
        None,
        description="Order ID where gift card was purchased"
    )
    issued_at: datetime = Field(
        ...,
        description="Timestamp when gift card was issued"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when gift card was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when gift card was last updated"
    )
    last_used_at: Optional[datetime] = Field(
        None,
        description="Timestamp when gift card was last used"
    )


class GiftCardResponse(GiftCardInDB):
    """Schema for gift card API responses with computed properties."""

    is_valid: bool = Field(
        ...,
        description="Whether the gift card is currently valid (active, has balance, not expired)"
    )
    is_assigned: bool = Field(
        ...,
        description="Whether the gift card is assigned to a customer"
    )
    usage_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of gift card balance used"
    )

    model_config = ConfigDict(from_attributes=True)


class GiftCardListResponse(BaseModel):
    """Schema for paginated gift card list responses."""

    items: list[GiftCardResponse] = Field(
        ...,
        description="List of gift cards"
    )
    total: int = Field(
        ...,
        description="Total number of gift cards",
        examples=[100]
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


class GiftCardRedemption(BaseModel):
    """Schema for redeeming/using a gift card."""

    card_code: str = Field(
        ...,
        description="Gift card code to redeem"
    )
    pin_code: Optional[str] = Field(
        None,
        description="PIN code (if required)"
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Amount to redeem from gift card (HUF)",
        examples=[1000.00, 5000.00]
    )
    order_id: Optional[int] = Field(
        None,
        description="Order ID where gift card is being used"
    )

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate redemption amount is positive."""
        if v <= 0:
            raise ValueError('Redemption amount must be greater than zero')
        return v


class GiftCardRedemptionResponse(BaseModel):
    """Schema for gift card redemption response."""

    success: bool = Field(
        ...,
        description="Whether redemption was successful"
    )
    message: str = Field(
        ...,
        description="Response message"
    )
    redeemed_amount: Optional[Decimal] = Field(
        None,
        description="Amount successfully redeemed (HUF)"
    )
    remaining_balance: Optional[Decimal] = Field(
        None,
        description="Remaining balance after redemption (HUF)"
    )
    gift_card: Optional[GiftCardResponse] = Field(
        None,
        description="Updated gift card details (if successful)"
    )


class GiftCardBalanceUpdate(BaseModel):
    """Schema for updating gift card balance (e.g., refunds, adjustments)."""

    amount: Decimal = Field(
        ...,
        description="Amount to add (positive) or subtract (negative) from balance (HUF)",
        examples=[1000.00, -500.00]
    )
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Reason for balance adjustment",
        examples=["Refund from cancelled order", "Promotional bonus", "Balance correction"]
    )
