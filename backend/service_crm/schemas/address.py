"""
Pydantic schemas for Address entities.

This module defines the request and response schemas for address operations
in the Service CRM module (Module 5).
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AddressTypeEnum(str, Enum):
    """Enumeration of address types."""

    SHIPPING = "SHIPPING"  # Szállítási cím
    BILLING = "BILLING"    # Számlázási cím
    BOTH = "BOTH"          # Mindkettő


class AddressBase(BaseModel):
    """Base schema for Address with common fields."""

    address_type: AddressTypeEnum = Field(
        AddressTypeEnum.SHIPPING,
        description="Type of address (shipping, billing, or both)",
        examples=["SHIPPING", "BILLING", "BOTH"]
    )
    is_default: bool = Field(
        False,
        description="Whether this is the default address for the customer"
    )
    country: str = Field(
        "Magyarország",
        max_length=100,
        description="Country name",
        examples=["Magyarország"]
    )
    postal_code: str = Field(
        ...,
        min_length=4,
        max_length=10,
        description="Postal code",
        examples=["1011", "6720", "9024"]
    )
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City name",
        examples=["Budapest", "Szeged", "Győr"]
    )
    street_address: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Street name",
        examples=["Fő utca", "Rákóczi út", "Petőfi tér"]
    )
    street_number: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Street number",
        examples=["12", "5/A", "23-25"]
    )
    building: Optional[str] = Field(
        None,
        max_length=50,
        description="Building identifier",
        examples=["A épület", "B блок"]
    )
    floor: Optional[str] = Field(
        None,
        max_length=10,
        description="Floor number",
        examples=["1", "2", "földszint", "fszt"]
    )
    door: Optional[str] = Field(
        None,
        max_length=10,
        description="Door/apartment number",
        examples=["1", "12", "A"]
    )
    company_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Company name (for business addresses)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional delivery notes"
    )


class AddressCreate(AddressBase):
    """Schema for creating a new address."""

    customer_id: int = Field(
        ...,
        gt=0,
        description="ID of the customer this address belongs to"
    )


class AddressUpdate(BaseModel):
    """Schema for updating an existing address."""

    address_type: Optional[AddressTypeEnum] = Field(
        None,
        description="Type of address"
    )
    is_default: Optional[bool] = Field(
        None,
        description="Whether this is the default address"
    )
    country: Optional[str] = Field(
        None,
        max_length=100,
        description="Country name"
    )
    postal_code: Optional[str] = Field(
        None,
        min_length=4,
        max_length=10,
        description="Postal code"
    )
    city: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="City name"
    )
    street_address: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Street name"
    )
    street_number: Optional[str] = Field(
        None,
        min_length=1,
        max_length=20,
        description="Street number"
    )
    building: Optional[str] = Field(
        None,
        max_length=50,
        description="Building identifier"
    )
    floor: Optional[str] = Field(
        None,
        max_length=10,
        description="Floor number"
    )
    door: Optional[str] = Field(
        None,
        max_length=10,
        description="Door/apartment number"
    )
    company_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Company name"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional notes"
    )


class AddressInDB(AddressBase):
    """Schema for address as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique address identifier",
        examples=[1, 42, 1234]
    )
    customer_id: int = Field(
        ...,
        description="Customer ID this address belongs to"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when address was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when address was last updated"
    )


class AddressResponse(AddressInDB):
    """Schema for address API responses."""
    pass


class AddressListResponse(BaseModel):
    """Schema for paginated address list responses."""

    items: list[AddressResponse] = Field(
        ...,
        description="List of addresses"
    )
    total: int = Field(
        ...,
        description="Total number of addresses",
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
