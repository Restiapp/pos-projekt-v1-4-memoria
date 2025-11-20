"""
Pydantic schemas for Customer entities.

This module defines the request and response schemas for customer operations
in the Service CRM module (Module 5).
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class CustomerBase(BaseModel):
    """Base schema for Customer with common fields."""

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Customer's first name",
        examples=["János", "Kovács"]
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Customer's last name",
        examples=["Nagy", "Kiss"]
    )
    email: EmailStr = Field(
        ...,
        description="Customer's email address (unique)",
        examples=["janos.nagy@example.com"]
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Customer's phone number",
        examples=["+36301234567", "06301234567"]
    )
    marketing_consent: bool = Field(
        False,
        description="Customer's consent for marketing emails"
    )
    sms_consent: bool = Field(
        False,
        description="Customer's consent for SMS marketing"
    )
    birth_date: Optional[datetime] = Field(
        None,
        description="Customer's birth date"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the customer"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Customer tags/labels (e.g., ['VIP', 'Regular', 'New'])",
        examples=[["VIP", "Regular"], ["New Customer"]]
    )
    last_visit: Optional[datetime] = Field(
        None,
        description="Last visit/order timestamp"
    )


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer."""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating an existing customer."""

    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Customer's first name"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Customer's last name"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Customer's email address"
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Customer's phone number"
    )
    marketing_consent: Optional[bool] = Field(
        None,
        description="Customer's consent for marketing emails"
    )
    sms_consent: Optional[bool] = Field(
        None,
        description="Customer's consent for SMS marketing"
    )
    birth_date: Optional[datetime] = Field(
        None,
        description="Customer's birth date"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the customer"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Customer tags/labels"
    )
    last_visit: Optional[datetime] = Field(
        None,
        description="Last visit/order timestamp"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Customer account status"
    )


class CustomerInDB(CustomerBase):
    """Schema for customer as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique customer identifier",
        examples=[1, 42, 1234]
    )
    customer_uid: str = Field(
        ...,
        description="Unique customer UID (Vendégszám)",
        examples=["CUST-123456", "CUST-789012"]
    )
    loyalty_points: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Customer's loyalty points balance"
    )
    total_spent: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total amount spent by customer (HUF)"
    )
    total_orders: int = Field(
        ...,
        ge=0,
        description="Total number of orders placed"
    )
    is_active: bool = Field(
        ...,
        description="Customer account status"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when customer was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when customer was last updated"
    )


class CustomerResponse(CustomerInDB):
    """Schema for customer API responses."""
    pass


class CustomerListResponse(BaseModel):
    """Schema for paginated customer list responses."""

    items: list[CustomerResponse] = Field(
        ...,
        description="List of customers"
    )
    total: int = Field(
        ...,
        description="Total number of customers",
        examples=[250]
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


class LoyaltyPointsUpdate(BaseModel):
    """Schema for updating customer loyalty points."""

    points: Decimal = Field(
        ...,
        description="Points to add (positive) or subtract (negative)",
        examples=[10.00, -5.00]
    )
    reason: Optional[str] = Field(
        None,
        description="Reason for points adjustment",
        examples=["Purchase reward", "Birthday bonus", "Points correction"]
    )
