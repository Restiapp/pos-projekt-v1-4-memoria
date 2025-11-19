"""
Pydantic schemas for Discount entities.

This module defines the request and response schemas for discount operations
in the Service Orders module, including order-level and item-level discounts.

V3.0 Feature: Discount Management (Task A4)
"""

from decimal import Decimal
from enum import Enum
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict


class DiscountTypeEnum(str, Enum):
    """Enumeration of discount types."""

    PERCENTAGE = "percentage"  # Percentage-based discount (e.g., 10%)
    FIXED = "fixed"  # Fixed amount discount (e.g., 500 HUF)


class DiscountDetails(BaseModel):
    """
    Schema for discount details stored in discount_details JSONB field.

    This structure is used for both order-level and item-level discounts.
    Stored as JSONB in the database for flexibility and audit trail.
    """

    model_config = ConfigDict(use_enum_values=True)

    type: DiscountTypeEnum = Field(
        ...,
        description="Type of discount: percentage or fixed amount",
        examples=["percentage", "fixed"]
    )
    value: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Discount value (percentage 0-100 or fixed amount in HUF)",
        examples=[10.00, 500.00, 15.50]
    )
    reason: Optional[str] = Field(
        None,
        max_length=255,
        description="Reason for applying the discount",
        examples=[
            "Törzsvásárlói kedvezmény",
            "Manager által engedélyezett",
            "Promóciós akció",
            "Kompenzáció lassú kiszolgálás miatt"
        ]
    )
    applied_by_user_id: int = Field(
        ...,
        description="ID of the employee who applied the discount",
        examples=[1, 5, 12]
    )
    applied_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the discount was applied"
    )
    coupon_code: Optional[str] = Field(
        None,
        max_length=50,
        description="Coupon code if discount was applied via coupon (optional)",
        examples=["SUMMER2024", "WELCOME10", None]
    )

    @field_validator('value')
    @classmethod
    def validate_discount_value(cls, v: Decimal, info) -> Decimal:
        """
        Validate discount value based on type.

        - Percentage discounts must be between 0 and 100
        - Fixed amount discounts must be >= 0
        """
        discount_type = info.data.get('type')

        if discount_type == DiscountTypeEnum.PERCENTAGE:
            if v < 0 or v > 100:
                raise ValueError("Percentage discount must be between 0 and 100")
        elif discount_type == DiscountTypeEnum.FIXED:
            if v < 0:
                raise ValueError("Fixed discount must be >= 0")

        return v


class ApplyDiscountRequest(BaseModel):
    """
    Schema for applying a discount to an order or order item.

    Used for both order-level discounts (POST /orders/{id}/apply-discount)
    and item-level discounts (PATCH /orders/{id}/items/{itemId}).
    """

    discount_type: DiscountTypeEnum = Field(
        ...,
        description="Type of discount to apply",
        examples=["percentage", "fixed"]
    )
    discount_value: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Discount value (percentage 0-100 or fixed amount in HUF)",
        examples=[10.00, 500.00]
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Reason for applying the discount (required for audit trail)",
        examples=[
            "Törzsvásárlói kedvezmény",
            "Manager által engedélyezett",
            "Kompenzáció"
        ]
    )
    coupon_code: Optional[str] = Field(
        None,
        max_length=50,
        description="Optional coupon code",
        examples=["SUMMER2024", None]
    )

    @field_validator('discount_value')
    @classmethod
    def validate_discount_value(cls, v: Decimal, info) -> Decimal:
        """Validate discount value based on type."""
        discount_type = info.data.get('discount_type')

        if discount_type == DiscountTypeEnum.PERCENTAGE:
            if v < 0 or v > 100:
                raise ValueError("Percentage discount must be between 0 and 100")
        elif discount_type == DiscountTypeEnum.FIXED:
            if v < 0:
                raise ValueError("Fixed discount must be >= 0")

        return v


class ApplyOrderDiscountRequest(ApplyDiscountRequest):
    """
    Schema for applying a discount to an entire order.

    Endpoint: POST /orders/{id}/apply-discount
    """
    pass


class ApplyItemDiscountRequest(ApplyDiscountRequest):
    """
    Schema for applying a discount to a single order item.

    Used in: PATCH /orders/{id}/items/{itemId}
    """
    pass


class DiscountCalculationResult(BaseModel):
    """
    Schema for discount calculation results.

    Returned when a discount is successfully applied to show the
    before/after amounts and the discount breakdown.
    """

    original_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Original amount before discount",
        examples=[5000.00, 1200.00]
    )
    discount_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Amount of discount applied",
        examples=[500.00, 120.00]
    )
    final_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Final amount after discount",
        examples=[4500.00, 1080.00]
    )
    discount_details: DiscountDetails = Field(
        ...,
        description="Details of the applied discount"
    )


class OrderDiscountResponse(BaseModel):
    """
    Schema for order-level discount application response.

    Endpoint: POST /orders/{id}/apply-discount
    """

    order_id: int = Field(
        ...,
        description="Order identifier",
        examples=[1, 42]
    )
    message: str = Field(
        ...,
        description="Success message",
        examples=["Kedvezmény sikeresen alkalmazva a rendelésre"]
    )
    calculation: DiscountCalculationResult = Field(
        ...,
        description="Discount calculation breakdown"
    )
    updated_total: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Updated total order amount after discount",
        examples=[4500.00]
    )


class ItemDiscountResponse(BaseModel):
    """
    Schema for item-level discount application response.

    Used in: PATCH /orders/{id}/items/{itemId}
    """

    item_id: int = Field(
        ...,
        description="Order item identifier",
        examples=[1, 42]
    )
    order_id: int = Field(
        ...,
        description="Parent order identifier",
        examples=[1, 42]
    )
    message: str = Field(
        ...,
        description="Success message",
        examples=["Kedvezmény sikeresen alkalmazva a tételre"]
    )
    calculation: DiscountCalculationResult = Field(
        ...,
        description="Discount calculation breakdown"
    )
    updated_item_total: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Updated item total (unit_price * quantity) after discount",
        examples=[1080.00]
    )
    updated_order_total: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Updated total order amount after recalculation",
        examples=[5380.00]
    )


class RemoveDiscountResponse(BaseModel):
    """
    Schema for discount removal response.

    Used when removing a discount from an order or item.
    """

    message: str = Field(
        ...,
        description="Success message",
        examples=["Kedvezmény sikeresen eltávolítva"]
    )
    previous_discount: Optional[DiscountDetails] = Field(
        None,
        description="Previously applied discount details"
    )
    updated_total: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Updated total amount after discount removal",
        examples=[5000.00]
    )
