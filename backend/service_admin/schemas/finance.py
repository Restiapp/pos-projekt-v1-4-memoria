"""
Pydantic schemas for Finance (Pénzügyi) entities.

This module defines the request and response schemas for finance operations
in the Service Admin module, including cash drawer operations and daily closures.
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Cash Movement Schemas
# ============================================================================

class CashMovementBase(BaseModel):
    """Base schema for CashMovement with common fields."""

    amount: Decimal = Field(
        ...,
        ge=0.01,
        decimal_places=2,
        description="Összeg (pozitív érték)",
        examples=[1000.00, 5000.50, 250.75]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Leírás/megjegyzés",
        examples=["Nyitó egyenleg", "Készpénz befizetés", "Kiadások"]
    )


class CashDepositRequest(CashMovementBase):
    """Schema for cash deposit (befizetés) request."""

    employee_id: Optional[int] = Field(
        None,
        description="Munkatárs azonosító aki végrehajtotta",
        examples=[1, 2, 3]
    )


class CashWithdrawRequest(CashMovementBase):
    """Schema for cash withdrawal (kivétel) request."""

    employee_id: Optional[int] = Field(
        None,
        description="Munkatárs azonosító aki végrehajtotta",
        examples=[1, 2, 3]
    )


class CashMovementResponse(BaseModel):
    """Schema for CashMovement response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Pénzmozgás azonosító",
        examples=[1, 2, 3]
    )
    movement_type: str = Field(
        ...,
        description="Mozgás típusa",
        examples=["CASH_IN", "CASH_OUT", "OPENING_BALANCE"]
    )
    amount: Decimal = Field(
        ...,
        description="Összeg",
        examples=[1000.00, 5000.50]
    )
    description: Optional[str] = Field(
        None,
        description="Leírás/megjegyzés"
    )
    order_id: Optional[int] = Field(
        None,
        description="Kapcsolódó rendelés azonosító"
    )
    employee_id: Optional[int] = Field(
        None,
        description="Munkatárs azonosító"
    )
    daily_closure_id: Optional[int] = Field(
        None,
        description="Napi zárás azonosító"
    )
    created_at: datetime = Field(
        ...,
        description="Létrehozás időpontja"
    )


# ============================================================================
# Daily Closure Schemas
# ============================================================================

class DailyClosureBase(BaseModel):
    """Base schema for DailyClosure with common fields."""

    opening_balance: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Nyitó egyenleg",
        examples=[10000.00, 5000.00, 0.00]
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Megjegyzések/indoklás",
        examples=["Minden rendben", "Kisebb eltérés készpénzhiány miatt"]
    )


class DailyClosureCreate(DailyClosureBase):
    """Schema for creating a new daily closure."""

    closed_by_employee_id: Optional[int] = Field(
        None,
        description="Munkatárs azonosító aki a zárást végrehajtotta",
        examples=[1, 2, 3]
    )


class DailyClosureUpdate(BaseModel):
    """Schema for updating an existing daily closure."""

    status: Optional[str] = Field(
        None,
        description="Zárás státusza",
        examples=["OPEN", "IN_PROGRESS", "CLOSED", "RECONCILED"]
    )
    actual_closing_balance: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Tényleges záró egyenleg"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Megjegyzések/indoklás"
    )


class DailyClosureResponse(BaseModel):
    """Schema for DailyClosure response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Napi zárás azonosító",
        examples=[1, 2, 3]
    )
    closure_date: datetime = Field(
        ...,
        description="Zárás dátuma"
    )
    status: str = Field(
        ...,
        description="Státusz",
        examples=["OPEN", "CLOSED", "RECONCILED"]
    )
    opening_balance: Decimal = Field(
        ...,
        description="Nyitó egyenleg"
    )
    expected_closing_balance: Optional[Decimal] = Field(
        None,
        description="Várható záró egyenleg"
    )
    actual_closing_balance: Optional[Decimal] = Field(
        None,
        description="Tényleges záró egyenleg"
    )
    difference: Optional[Decimal] = Field(
        None,
        description="Eltérés"
    )
    payment_summary: Optional[dict] = Field(
        None,
        description="Fizetési módok szerinti bontás",
        examples=[{"KESZPENZ": 10000.00, "KARTYA": 5000.00, "SZEP_KARTYA": 2000.00}]
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések"
    )
    closed_by_employee_id: Optional[int] = Field(
        None,
        description="Munkatárs azonosító"
    )
    created_at: datetime = Field(
        ...,
        description="Létrehozás időpontja"
    )
    updated_at: datetime = Field(
        ...,
        description="Módosítás időpontja"
    )
    closed_at: Optional[datetime] = Field(
        None,
        description="Lezárás időpontja"
    )


# ============================================================================
# Szamlazz.hu Integration Schemas
# ============================================================================

class SzamlazzHuInvoiceItem(BaseModel):
    """Schema for Számlázz.hu invoice item."""

    name: str = Field(
        ...,
        max_length=255,
        description="Tétel neve",
        examples=["Pizza Margherita", "Coca-Cola 0.5L"]
    )
    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Mennyiség",
        examples=[1, 2, 3]
    )
    unit: str = Field(
        "db",
        max_length=10,
        description="Mennyiségi egység",
        examples=["db", "kg", "l"]
    )
    unit_price: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Egységár (bruttó)",
        examples=[1500.00, 500.00]
    )
    vat_rate: Decimal = Field(
        27.0,
        ge=0,
        le=100,
        description="ÁFA kulcs (%)",
        examples=[27.0, 18.0, 5.0, 0.0]
    )


class SzamlazzHuInvoiceRequest(BaseModel):
    """Schema for Számlázz.hu invoice creation request."""

    order_id: int = Field(
        ...,
        description="Rendelés azonosító",
        examples=[1, 2, 3]
    )
    customer_name: str = Field(
        ...,
        max_length=255,
        description="Vásárló neve",
        examples=["Kovács János", "XY Kft."]
    )
    customer_email: Optional[str] = Field(
        None,
        description="Vásárló email címe",
        examples=["kovacs.janos@example.com"]
    )
    items: list[SzamlazzHuInvoiceItem] = Field(
        ...,
        min_length=1,
        description="Számla tételek listája"
    )
    payment_method: str = Field(
        "CASH",
        description="Fizetési mód",
        examples=["CASH", "CARD", "TRANSFER"]
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Megjegyzések"
    )


class SzamlazzHuInvoiceResponse(BaseModel):
    """Schema for Számlázz.hu invoice creation response."""

    success: bool = Field(
        ...,
        description="Sikeres volt-e a művelet",
        examples=[True, False]
    )
    invoice_number: Optional[str] = Field(
        None,
        description="Generált számla azonosító",
        examples=["SZ-2024-00001", "MOCK-INV-12345"]
    )
    pdf_url: Optional[str] = Field(
        None,
        description="Számla PDF URL-je",
        examples=["https://www.szamlazz.hu/invoices/12345.pdf"]
    )
    message: Optional[str] = Field(
        None,
        description="Üzenet/Hibaüzenet",
        examples=["Számla sikeresen létrehozva", "Hiba történt"]
    )
    order_id: int = Field(
        ...,
        description="Kapcsolódó rendelés azonosító",
        examples=[1, 2, 3]
    )
