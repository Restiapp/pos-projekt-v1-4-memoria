"""
Pydantic schemas for IncomingInvoice entities.

This module defines the request and response schemas for incoming invoice operations
in the Inventory Service (Module 5), including NAV OSA integration for fetching
incoming invoices from the Hungarian tax authority system.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, ConfigDict, field_validator


class NAVInvoiceData(BaseModel):
    """
    Schema for NAV OSA invoice data.

    This schema represents the structured invoice data received from
    the NAV Online Számlázó API.
    """

    invoice_number: str = Field(
        ...,
        description="Invoice number from NAV system",
        examples=["NAV-2024-12345", "INV-98765"]
    )
    supplier_tax_number: Optional[str] = Field(
        None,
        description="Supplier tax number (Hungarian format: XXXXXXXX-Y-ZZ)",
        examples=["12345678-1-23", "98765432-2-44"]
    )
    supplier_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Supplier name from NAV",
        examples=["Metro Cash & Carry Kft.", "Tesco Áruház Zrt."]
    )
    invoice_date: Optional[date] = Field(
        None,
        description="Invoice issue date"
    )
    total_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total invoice amount",
        examples=[125000.00, 45000.00]
    )
    currency: str = Field(
        default="HUF",
        max_length=3,
        description="Currency code (ISO 4217)",
        examples=["HUF", "EUR", "USD"]
    )
    line_items: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Invoice line items from NAV"
    )
    additional_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional NAV invoice data"
    )


class IncomingInvoiceBase(BaseModel):
    """Base schema for IncomingInvoice with common fields."""

    invoice_number: str = Field(
        ...,
        max_length=100,
        description="Invoice number (must be unique)",
        examples=["NAV-2024-12345", "INV-98765"]
    )
    supplier_tax_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Supplier tax number",
        examples=["12345678-1-23"]
    )
    supplier_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Supplier name",
        examples=["Metro Cash & Carry Kft.", "Tesco Áruház Zrt."]
    )
    invoice_date: Optional[date] = Field(
        None,
        description="Invoice issue date"
    )
    total_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total invoice amount",
        examples=[125000.00, 45000.00]
    )
    currency: str = Field(
        default="HUF",
        max_length=3,
        description="Currency code (ISO 4217)",
        examples=["HUF", "EUR", "USD"]
    )
    status: str = Field(
        default="NEW",
        max_length=50,
        description="Invoice processing status",
        examples=["NEW", "REVIEWED", "SETTLED"]
    )


class IncomingInvoiceCreate(IncomingInvoiceBase):
    """Schema for creating a new incoming invoice."""

    nav_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Full NAV OSA API response data"
    )


class IncomingInvoiceUpdate(BaseModel):
    """Schema for updating an existing incoming invoice."""

    supplier_tax_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Supplier tax number"
    )
    supplier_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Supplier name"
    )
    invoice_date: Optional[date] = Field(
        None,
        description="Invoice issue date"
    )
    total_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total invoice amount"
    )
    currency: Optional[str] = Field(
        None,
        max_length=3,
        description="Currency code"
    )
    nav_data: Optional[Dict[str, Any]] = Field(
        None,
        description="NAV OSA API response data"
    )
    status: Optional[str] = Field(
        None,
        max_length=50,
        description="Invoice processing status"
    )


class IncomingInvoiceInDB(IncomingInvoiceBase):
    """Schema for incoming invoice as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique incoming invoice identifier",
        examples=[1, 42, 100]
    )
    nav_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Full NAV OSA API response (stored as JSONB)"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the invoice was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the invoice was last updated"
    )


class IncomingInvoiceResponse(IncomingInvoiceInDB):
    """Schema for incoming invoice API responses."""
    pass


class IncomingInvoiceDetailResponse(IncomingInvoiceResponse):
    """
    Schema for detailed incoming invoice response including parsed NAV data.

    This schema can include additional computed fields or related entities.
    """

    parsed_nav_data: Optional[NAVInvoiceData] = Field(
        None,
        description="Parsed NAV data as structured object"
    )


class IncomingInvoiceListResponse(BaseModel):
    """Schema for paginated incoming invoice list responses."""

    items: List[IncomingInvoiceResponse] = Field(
        ...,
        description="List of incoming invoices"
    )
    total: int = Field(
        ...,
        description="Total number of incoming invoices",
        examples=[25, 50, 100]
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


class FetchIncomingInvoicesRequest(BaseModel):
    """Schema for fetching incoming invoices from NAV OSA."""

    from_date: Optional[date] = Field(
        None,
        description="Fetch invoices from this date onwards"
    )
    to_date: Optional[date] = Field(
        None,
        description="Fetch invoices up to this date"
    )
    test_mode: bool = Field(
        default=True,
        description="Use NAV test environment"
    )


class FetchIncomingInvoicesResponse(BaseModel):
    """Schema for fetch incoming invoices operation response."""

    success: bool = Field(
        ...,
        description="Whether the fetch operation succeeded"
    )
    fetched_count: int = Field(
        ...,
        ge=0,
        description="Number of invoices fetched from NAV",
        examples=[5, 10, 25]
    )
    saved_count: int = Field(
        ...,
        ge=0,
        description="Number of invoices saved to database (new invoices only)",
        examples=[5, 10, 25]
    )
    message: str = Field(
        ...,
        description="Human-readable message about the operation"
    )
    invoices: List[IncomingInvoiceResponse] = Field(
        default=[],
        description="List of fetched and saved invoices"
    )
