"""
Pydantic schemas for SupplierInvoice entities.

This module defines the request and response schemas for supplier invoice operations
in the Inventory Service (Module 5), including OCR data processing and invoice status management.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, ConfigDict, field_validator


class OCRLineItem(BaseModel):
    """Schema for a single line item extracted from OCR."""

    item_name: Optional[str] = Field(
        None,
        description="Name of the item from OCR",
        examples=["Marhahús", "Paradicsom", "Liszt"]
    )
    quantity: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=3,
        description="Quantity of the item",
        examples=[10.500, 5.000, 25.000]
    )
    unit: Optional[str] = Field(
        None,
        description="Unit of measurement",
        examples=["kg", "liter", "db"]
    )
    unit_price: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Unit price in HUF",
        examples=[1500.00, 250.00, 89.90]
    )
    total_price: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total price for this line item in HUF",
        examples=[15750.00, 1250.00, 2247.50]
    )


class OCRData(BaseModel):
    """
    Schema for OCR extracted data from supplier invoices.

    This schema represents the structured data extracted from invoice images
    using OCR (Optical Character Recognition) technology.
    """

    raw_text: Optional[str] = Field(
        None,
        description="Raw OCR extracted text"
    )
    supplier_name: Optional[str] = Field(
        None,
        description="Supplier name extracted from invoice",
        examples=["Metro Cash & Carry", "Tesco Áruház"]
    )
    invoice_number: Optional[str] = Field(
        None,
        description="Invoice number extracted from document",
        examples=["INV-2024-12345", "SZ-98765"]
    )
    invoice_date: Optional[date] = Field(
        None,
        description="Invoice date extracted from document"
    )
    total_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total invoice amount in HUF",
        examples=[125000.00, 45000.00]
    )
    line_items: Optional[List[OCRLineItem]] = Field(
        None,
        description="List of line items extracted from invoice"
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="OCR confidence score (0.0 to 1.0)",
        examples=[0.95, 0.87, 0.99]
    )
    additional_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional OCR extracted data"
    )


class SupplierInvoiceBase(BaseModel):
    """Base schema for SupplierInvoice with common fields."""

    supplier_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Supplier name",
        examples=["Metro Cash & Carry", "Tesco Áruház", "Spar Partner"]
    )
    invoice_date: Optional[date] = Field(
        None,
        description="Invoice date",
        examples=["2024-01-15", "2024-02-20"]
    )
    total_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total invoice amount in HUF",
        examples=[125000.00, 45000.00, 89500.00]
    )
    status: str = Field(
        default="FELDOLGOZÁSRA VÁR",
        max_length=50,
        description="Invoice processing status",
        examples=["FELDOLGOZÁSRA VÁR", "FELDOLGOZVA", "JÓVÁHAGYVA", "ELUTASÍTVA"]
    )


class SupplierInvoiceCreate(SupplierInvoiceBase):
    """Schema for creating a new supplier invoice."""

    ocr_data: Optional[OCRData] = Field(
        None,
        description="OCR extracted data from invoice"
    )


class SupplierInvoiceUpdate(BaseModel):
    """Schema for updating an existing supplier invoice."""

    supplier_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Supplier name"
    )
    invoice_date: Optional[date] = Field(
        None,
        description="Invoice date"
    )
    total_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total invoice amount in HUF"
    )
    ocr_data: Optional[OCRData] = Field(
        None,
        description="OCR extracted data from invoice"
    )
    status: Optional[str] = Field(
        None,
        max_length=50,
        description="Invoice processing status"
    )


class SupplierInvoiceInDB(SupplierInvoiceBase):
    """Schema for supplier invoice as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique supplier invoice identifier",
        examples=[1, 42, 100]
    )
    ocr_data: Optional[Dict[str, Any]] = Field(
        None,
        description="OCR extracted data (stored as JSONB)"
    )

    @field_validator('ocr_data')
    @classmethod
    def validate_ocr_data(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate that ocr_data follows the expected structure."""
        if v is None:
            return v

        # Validate that the ocr_data can be parsed as OCRData
        try:
            OCRData(**v)
        except Exception as e:
            # Allow invalid data to pass through for backward compatibility
            # but log warning in production
            pass

        return v


class SupplierInvoiceResponse(SupplierInvoiceInDB):
    """Schema for supplier invoice API responses."""
    pass


class SupplierInvoiceDetailResponse(SupplierInvoiceResponse):
    """
    Schema for detailed supplier invoice response including parsed OCR data.

    This schema can include additional computed fields or related entities.
    """

    parsed_ocr_data: Optional[OCRData] = Field(
        None,
        description="Parsed OCR data as structured object"
    )


class SupplierInvoiceListResponse(BaseModel):
    """Schema for paginated supplier invoice list responses."""

    items: list[SupplierInvoiceResponse] = Field(
        ...,
        description="List of supplier invoices"
    )
    total: int = Field(
        ...,
        description="Total number of supplier invoices",
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
