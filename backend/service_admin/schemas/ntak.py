"""
Pydantic schemas for NTAK (Nemzeti Turizmus Adatszolgáltatási Központ) entities.

This module defines the request and response schemas for NTAK data submission
in the Service Admin module (Module 8), including order summary data and responses
for mandatory Hungarian tax authority reporting.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class NTAKLineItem(BaseModel):
    """
    Schema for a single line item in an NTAK order summary.

    Represents one product/item in the order that needs to be reported
    to the National Tourism Data Service Center (NTAK).
    """

    product_name: str = Field(
        ...,
        max_length=255,
        description="Name of the product/item",
        examples=["Margherita Pizza", "Coca Cola 0.5L", "Tiramisu"]
    )
    quantity: int = Field(
        ...,
        ge=1,
        description="Quantity of items ordered",
        examples=[1, 2, 3]
    )
    unit_price: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Unit price per item in HUF (excluding VAT)",
        examples=[1200.00, 350.00, 890.00]
    )
    vat_rate: Decimal = Field(
        ...,
        ge=0,
        le=100,
        decimal_places=2,
        description="VAT rate percentage applied to this item",
        examples=[27.00, 5.00, 18.00]
    )
    total_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total amount for this line item (quantity * unit_price, including VAT)",
        examples=[1524.00, 444.50, 1130.30]
    )
    product_id: Optional[int] = Field(
        None,
        description="Internal product identifier for reference",
        examples=[1, 42, 156]
    )


class NTAKPayment(BaseModel):
    """
    Schema for payment information in an NTAK order summary.

    Represents the payment method and amount used for an order
    that needs to be reported to NTAK.
    """

    payment_method: str = Field(
        ...,
        max_length=100,
        description="Payment method used (NTAK-compliant format)",
        examples=["Készpénz", "Bankkártya", "OTP SZÉP", "K&H SZÉP", "MKB SZÉP", "Átutalás"]
    )
    amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Payment amount in HUF",
        examples=[2500.00, 5000.00, 12890.00]
    )
    transaction_id: Optional[str] = Field(
        None,
        max_length=255,
        description="External payment provider transaction identifier (if applicable)",
        examples=["TXN-20240115-1234", "CARD-567890", None]
    )


class NTAKOrderSummaryData(BaseModel):
    """
    Schema for complete NTAK order summary data.

    This schema represents the complete order data package that must be
    submitted to the National Tourism Data Service Center (NTAK) when
    an order is closed. It includes all line items, payment information,
    and calculated totals required for compliance with Hungarian tax
    and tourism reporting regulations.
    """

    order_id: int = Field(
        ...,
        description="Internal order identifier",
        examples=[1, 42, 1234]
    )
    order_type: str = Field(
        ...,
        max_length=50,
        description="Type of order (dine-in, takeout, delivery)",
        examples=["Helyben", "Elvitel", "Kiszállítás"]
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp when the order was closed/completed",
        examples=["2024-01-15T14:30:00Z", "2024-02-20T18:45:00Z"]
    )
    line_items: List[NTAKLineItem] = Field(
        ...,
        min_length=1,
        description="List of all items in the order"
    )
    payments: List[NTAKPayment] = Field(
        ...,
        min_length=1,
        description="List of all payments made for this order"
    )
    subtotal: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Subtotal amount before VAT in HUF",
        examples=[8000.00, 12500.00, 5600.00]
    )
    vat_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total VAT amount in HUF",
        examples=[2160.00, 3375.00, 1512.00]
    )
    total_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total order amount including VAT in HUF",
        examples=[10160.00, 15875.00, 7112.00]
    )
    vat_rate: Decimal = Field(
        ...,
        ge=0,
        le=100,
        decimal_places=2,
        description="Final VAT rate applied to the order (NTAK-compliant: 27% or 5%)",
        examples=[27.00, 5.00]
    )
    table_number: Optional[int] = Field(
        None,
        description="Table number (for dine-in orders)",
        examples=[1, 5, 12, None]
    )
    is_cancellation: bool = Field(
        False,
        description="Flag indicating if this is a cancellation (storno) submission",
        examples=[False, True]
    )


class NTAKResponse(BaseModel):
    """
    Schema for NTAK API response.

    This schema represents the response received from the NTAK service
    after submitting order summary data. It indicates whether the submission
    was successful and provides tracking information.
    """

    success: bool = Field(
        ...,
        description="Indicates if the NTAK submission was successful",
        examples=[True, False]
    )
    message: str = Field(
        ...,
        max_length=500,
        description="Response message from NTAK service",
        examples=[
            "Rendelésösszesítő sikeresen elküldve",
            "NTAK submission successful",
            "Hiba történt az adatküldés során: Invalid VAT rate"
        ]
    )
    transaction_id: Optional[str] = Field(
        None,
        max_length=255,
        description="NTAK transaction/reference identifier for this submission",
        examples=["NTAK-2024-001234-5678", "REF-20240115143000", None]
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp when the NTAK response was received",
        examples=["2024-01-15T14:30:05Z", "2024-02-20T18:45:12Z"]
    )
    error_code: Optional[str] = Field(
        None,
        max_length=50,
        description="Error code from NTAK service (if submission failed)",
        examples=["INVALID_VAT", "MISSING_DATA", "TIMEOUT", None]
    )
    submitted_data: Optional[NTAKOrderSummaryData] = Field(
        None,
        description="Echo of the submitted order summary data (for verification)"
    )


class NTAKSendRequest(BaseModel):
    """
    Schema for manual NTAK send request.

    This schema is used when manually triggering an NTAK submission
    for a specific order (e.g., via the /ntak/send-summary/{orderId} endpoint).
    """

    force_resend: bool = Field(
        False,
        description="Force resending even if already submitted to NTAK",
        examples=[False, True]
    )
    is_test: bool = Field(
        False,
        description="Send to NTAK test environment instead of production",
        examples=[False, True]
    )


class NTAKStatusResponse(BaseModel):
    """
    Schema for NTAK submission status check response.

    This schema provides information about the current NTAK submission
    status for an order, including whether it has been submitted and
    the response received.
    """

    model_config = ConfigDict(from_attributes=True)

    order_id: int = Field(
        ...,
        description="Order identifier",
        examples=[1, 42, 1234]
    )
    has_been_submitted: bool = Field(
        ...,
        description="Indicates if the order has been submitted to NTAK",
        examples=[True, False]
    )
    submission_timestamp: Optional[datetime] = Field(
        None,
        description="Timestamp when the order was submitted to NTAK"
    )
    last_response: Optional[NTAKResponse] = Field(
        None,
        description="Last response received from NTAK service"
    )
    retry_count: int = Field(
        0,
        ge=0,
        description="Number of submission retry attempts",
        examples=[0, 1, 3]
    )
