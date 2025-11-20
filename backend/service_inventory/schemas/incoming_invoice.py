"""
Pydantic Schemas for Incoming Invoice Management
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal


# Enums
class InvoiceStatusEnum(str):
    """Invoice status enumeration for API"""
    DRAFT = "DRAFT"
    FINALIZED = "FINALIZED"


# Invoice Item Schemas
class IncomingInvoiceItemBase(BaseModel):
    """Base schema for invoice items"""
    inventory_item_id: int = Field(..., description="ID of the inventory item")
    quantity: Decimal = Field(..., gt=0, description="Quantity received")
    unit_price: Decimal = Field(..., ge=0, description="Price per unit")

    @field_validator('quantity', 'unit_price')
    @classmethod
    def validate_decimals(cls, v):
        """Ensure proper decimal places"""
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v


class IncomingInvoiceItemCreate(IncomingInvoiceItemBase):
    """Schema for creating invoice items"""
    pass


class IncomingInvoiceItemUpdate(BaseModel):
    """Schema for updating invoice items (all fields optional)"""
    inventory_item_id: Optional[int] = Field(None, description="ID of the inventory item")
    quantity: Optional[Decimal] = Field(None, gt=0, description="Quantity received")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="Price per unit")


class IncomingInvoiceItemResponse(IncomingInvoiceItemBase):
    """Schema for invoice item responses"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    total_price: Decimal = Field(..., description="Calculated as quantity * unit_price")
    created_at: datetime

    # Optional: Include inventory item details
    inventory_item_name: Optional[str] = None
    inventory_item_unit: Optional[str] = None


# Invoice Schemas
class IncomingInvoiceBase(BaseModel):
    """Base schema for incoming invoices"""
    supplier_name: str = Field(..., min_length=1, max_length=255, description="Supplier name")
    invoice_number: str = Field(..., min_length=1, max_length=100, description="Unique invoice number")
    invoice_date: date = Field(..., description="Invoice date")
    total_amount: Optional[Decimal] = Field(None, ge=0, description="Total invoice amount")


class IncomingInvoiceCreate(IncomingInvoiceBase):
    """Schema for creating a new invoice"""
    items: Optional[List[IncomingInvoiceItemCreate]] = Field(
        default=[],
        description="Invoice line items (can be added later)"
    )


class IncomingInvoiceUpdate(BaseModel):
    """Schema for updating an invoice (all fields optional)"""
    supplier_name: Optional[str] = Field(None, min_length=1, max_length=255)
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=100)
    invoice_date: Optional[date] = None
    total_amount: Optional[Decimal] = Field(None, ge=0)


class IncomingInvoiceResponse(IncomingInvoiceBase):
    """Schema for invoice responses"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str = Field(..., description="DRAFT or FINALIZED")
    created_at: datetime
    finalized_at: Optional[datetime] = None
    items: List[IncomingInvoiceItemResponse] = []


class IncomingInvoiceListResponse(BaseModel):
    """Paginated list of invoices"""
    invoices: List[IncomingInvoiceResponse]
    total: int
    page: int
    page_size: int


class IncomingInvoiceFinalizeRequest(BaseModel):
    """Schema for finalizing an invoice"""
    employee_id: Optional[int] = Field(None, description="ID of employee finalizing the invoice")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class IncomingInvoiceFinalizeResponse(BaseModel):
    """Response after finalizing an invoice"""
    invoice: IncomingInvoiceResponse
    stock_movements_created: int = Field(..., description="Number of stock movements created")
    message: str = "Invoice finalized successfully"


# Add Item to Existing Invoice
class AddInvoiceItemRequest(BaseModel):
    """Schema for adding items to an existing invoice"""
    items: List[IncomingInvoiceItemCreate] = Field(..., min_length=1)
