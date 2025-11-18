"""
NAV OSA (Online Számlázó Alkalmazás) Invoice Schemas
Pydantic schemas for NAV invoice integration
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class NAVInvoiceLine(BaseModel):
    """Single line item in a NAV invoice"""
    line_number: int = Field(..., description="Sorszám")
    product_name: str = Field(..., max_length=255, description="Termék neve")
    quantity: Decimal = Field(..., gt=0, description="Mennyiség")
    unit: str = Field(..., max_length=50, description="Mértékegység")
    unit_price: Decimal = Field(..., ge=0, description="Egységár (nettó)")
    vat_rate: Decimal = Field(..., ge=0, le=100, description="ÁFA kulcs (%)")
    net_amount: Decimal = Field(..., ge=0, description="Nettó érték")
    vat_amount: Decimal = Field(..., ge=0, description="ÁFA összeg")
    gross_amount: Decimal = Field(..., ge=0, description="Bruttó érték")

    model_config = ConfigDict(from_attributes=True)


class NAVOSAInvoiceBase(BaseModel):
    """Base schema for NAV OSA invoice"""
    invoice_number: str = Field(..., max_length=100, description="Számla száma")
    invoice_date: datetime = Field(..., description="Számla kelte")
    completion_date: datetime = Field(..., description="Teljesítés időpontja")
    payment_method: str = Field(..., max_length=50, description="Fizetési mód (KÉSZPÉNZ, KÁRTYA, stb.)")
    currency: str = Field(default="HUF", max_length=3, description="Pénznem (ISO 4217)")

    customer_name: Optional[str] = Field(None, max_length=255, description="Vevő neve")
    customer_tax_number: Optional[str] = Field(None, max_length=20, description="Vevő adószáma")
    customer_address: Optional[str] = Field(None, max_length=500, description="Vevő címe")

    total_net_amount: Decimal = Field(..., ge=0, description="Teljes nettó összeg")
    total_vat_amount: Decimal = Field(..., ge=0, description="Teljes ÁFA összeg")
    total_gross_amount: Decimal = Field(..., ge=0, description="Teljes bruttó összeg")

    notes: Optional[str] = Field(None, description="Megjegyzések")


class NAVOSAInvoiceCreate(NAVOSAInvoiceBase):
    """Schema for creating a new NAV OSA invoice"""
    order_id: Optional[int] = Field(None, description="Kapcsolódó rendelés ID")
    invoice_lines: List[NAVInvoiceLine] = Field(..., min_length=1, description="Számla tételek")

    @field_validator('invoice_lines')
    @classmethod
    def validate_line_numbers(cls, lines: List[NAVInvoiceLine]) -> List[NAVInvoiceLine]:
        """Validate that line numbers are sequential starting from 1"""
        if not lines:
            raise ValueError("Invoice must have at least one line item")

        expected_numbers = set(range(1, len(lines) + 1))
        actual_numbers = {line.line_number for line in lines}

        if actual_numbers != expected_numbers:
            raise ValueError(f"Line numbers must be sequential from 1 to {len(lines)}")

        return lines


class NAVOSAInvoiceUpdate(BaseModel):
    """Schema for updating NAV invoice status"""
    status: Optional[str] = Field(None, max_length=50)
    nav_transaction_id: Optional[str] = Field(None, max_length=100)
    nav_response_data: Optional[Dict[str, Any]] = Field(None)
    error_message: Optional[str] = Field(None)

    model_config = ConfigDict(from_attributes=True)


class NAVOSAInvoiceResponse(NAVOSAInvoiceBase):
    """Schema for NAV OSA invoice response"""
    id: int
    order_id: Optional[int]
    status: str = Field(..., description="Státusz: PENDING, SENT, ACCEPTED, REJECTED")
    nav_transaction_id: Optional[str] = Field(None, description="NAV tranzakció azonosító")
    nav_response_data: Optional[Dict[str, Any]] = Field(None, description="NAV API válasz adatok")
    error_message: Optional[str] = Field(None, description="Hibaüzenet (ha van)")
    created_at: datetime
    updated_at: datetime
    invoice_lines: List[NAVInvoiceLine]

    model_config = ConfigDict(from_attributes=True)


class NAVOSAInvoiceListResponse(BaseModel):
    """Paginated list of NAV invoices"""
    items: List[NAVOSAInvoiceResponse]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)


class NAVSendInvoiceRequest(BaseModel):
    """Request schema for sending invoice to NAV"""
    invoice_id: int = Field(..., description="NAV számla ID a helyi adatbázisban")
    test_mode: bool = Field(default=True, description="Teszt mód (NAV teszt környezet)")


class NAVSendInvoiceResponse(BaseModel):
    """Response schema after sending invoice to NAV"""
    success: bool
    invoice_id: int
    nav_transaction_id: Optional[str] = Field(None)
    status: str
    message: str
    nav_response: Optional[Dict[str, Any]] = Field(None, description="Teljes NAV válasz")

    model_config = ConfigDict(from_attributes=True)
