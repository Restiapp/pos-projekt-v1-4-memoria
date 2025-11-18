"""
Pydantic schemas for Coupon entities.

This module defines the request and response schemas for coupon operations
in the Service CRM module (Module 5).
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class DiscountTypeEnum(str, Enum):
    """Enumeration of discount types."""

    PERCENTAGE = "PERCENTAGE"      # Százalékos kedvezmény (0-100%)
    FIXED_AMOUNT = "FIXED_AMOUNT"  # Fix összegű kedvezmény (HUF)


class CouponBase(BaseModel):
    """Base schema for Coupon with common fields."""

    code: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique coupon code",
        examples=["WELCOME10", "SUMMER2024", "VIP50"]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Description of the coupon offer"
    )
    discount_type: DiscountTypeEnum = Field(
        ...,
        description="Type of discount (percentage or fixed amount)",
        examples=["PERCENTAGE", "FIXED_AMOUNT"]
    )
    discount_value: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Discount value (percentage 0-100 or fixed HUF amount)",
        examples=[10.00, 500.00]
    )
    min_purchase_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Minimum order value required to use coupon (HUF)",
        examples=[1000.00, 5000.00]
    )
    usage_limit: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum number of times this coupon can be used (null = unlimited)",
        examples=[100, 1000, None]
    )
    valid_from: datetime = Field(
        ...,
        description="Coupon validity start date/time"
    )
    valid_until: Optional[datetime] = Field(
        None,
        description="Coupon validity end date/time (null = no expiration)"
    )
    is_active: bool = Field(
        True,
        description="Whether the coupon is currently active"
    )

    @field_validator('discount_value')
    @classmethod
    def validate_discount_value(cls, v, info):
        """Validate discount value based on discount type."""
        discount_type = info.data.get('discount_type')
        if discount_type == DiscountTypeEnum.PERCENTAGE:
            if v > 100:
                raise ValueError('Percentage discount cannot exceed 100%')
        return v


class CouponCreate(CouponBase):
    """Schema for creating a new coupon."""

    customer_id: Optional[int] = Field(
        None,
        gt=0,
        description="Customer ID for customer-specific coupon (null = public coupon)"
    )


class CouponUpdate(BaseModel):
    """Schema for updating an existing coupon."""

    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Description of the coupon"
    )
    discount_type: Optional[DiscountTypeEnum] = Field(
        None,
        description="Type of discount"
    )
    discount_value: Optional[Decimal] = Field(
        None,
        gt=0,
        decimal_places=2,
        description="Discount value"
    )
    min_purchase_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Minimum purchase amount"
    )
    usage_limit: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum usage limit"
    )
    valid_from: Optional[datetime] = Field(
        None,
        description="Validity start date/time"
    )
    valid_until: Optional[datetime] = Field(
        None,
        description="Validity end date/time"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Coupon active status"
    )


class CouponInDB(CouponBase):
    """Schema for coupon as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique coupon identifier",
        examples=[1, 42, 1234]
    )
    customer_id: Optional[int] = Field(
        None,
        description="Customer ID (null for public coupons)"
    )
    usage_count: int = Field(
        ...,
        ge=0,
        description="Current number of times coupon has been used"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when coupon was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when coupon was last updated"
    )


class CouponResponse(CouponInDB):
    """Schema for coupon API responses."""
    pass


class CouponListResponse(BaseModel):
    """Schema for paginated coupon list responses."""

    items: list[CouponResponse] = Field(
        ...,
        description="List of coupons"
    )
    total: int = Field(
        ...,
        description="Total number of coupons",
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


class CouponValidationRequest(BaseModel):
    """Schema for coupon validation request."""

    code: str = Field(
        ...,
        description="Coupon code to validate"
    )
    order_amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Order amount to validate against (HUF)"
    )
    customer_id: Optional[int] = Field(
        None,
        description="Customer ID (for customer-specific coupons)"
    )


class CouponValidationResponse(BaseModel):
    """Schema for coupon validation response."""

    valid: bool = Field(
        ...,
        description="Whether the coupon is valid"
    )
    message: str = Field(
        ...,
        description="Validation message"
    )
    discount_amount: Optional[Decimal] = Field(
        None,
        description="Calculated discount amount in HUF (if valid)"
    )
    coupon: Optional[CouponResponse] = Field(
        None,
        description="Coupon details (if valid)"
    )
