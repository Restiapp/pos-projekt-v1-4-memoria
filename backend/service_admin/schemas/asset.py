"""
Pydantic schemas for Assets (Tárgyi Eszközök) entities.

This module defines the request and response schemas for asset management operations
in the Service Admin module, including asset groups, assets, and asset services.
"""

from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Asset Group Schemas
# ============================================================================

class AssetGroupBase(BaseModel):
    """Base schema for AssetGroup with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Eszközcsoport neve",
        examples=["Konyhai berendezések", "IT eszközök", "Bútorok"]
    )
    description: Optional[str] = Field(
        None,
        description="Leírás",
        examples=["Konyhai eszközök és berendezések"]
    )
    depreciation_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        decimal_places=2,
        description="Amortizációs ráta (százalék/év)",
        examples=[10.00, 20.00, 33.33]
    )
    expected_lifetime_years: Optional[int] = Field(
        None,
        ge=1,
        description="Várható élettartam (év)",
        examples=[3, 5, 10]
    )
    is_active: Optional[bool] = Field(
        True,
        description="Aktív státusz"
    )


class AssetGroupCreate(AssetGroupBase):
    """Schema for creating a new asset group."""
    pass


class AssetGroupUpdate(BaseModel):
    """Schema for updating an existing asset group."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Eszközcsoport neve"
    )
    description: Optional[str] = Field(
        None,
        description="Leírás"
    )
    depreciation_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        decimal_places=2,
        description="Amortizációs ráta (százalék/év)"
    )
    expected_lifetime_years: Optional[int] = Field(
        None,
        ge=1,
        description="Várható élettartam (év)"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Aktív státusz"
    )


class AssetGroupResponse(BaseModel):
    """Schema for AssetGroup response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Eszközcsoport azonosító",
        examples=[1, 2, 3]
    )
    name: str = Field(
        ...,
        description="Eszközcsoport neve"
    )
    description: Optional[str] = Field(
        None,
        description="Leírás"
    )
    depreciation_rate: Optional[Decimal] = Field(
        None,
        description="Amortizációs ráta (százalék/év)"
    )
    expected_lifetime_years: Optional[int] = Field(
        None,
        description="Várható élettartam (év)"
    )
    is_active: bool = Field(
        ...,
        description="Aktív státusz"
    )
    created_at: datetime = Field(
        ...,
        description="Létrehozás időpontja"
    )
    updated_at: datetime = Field(
        ...,
        description="Módosítás időpontja"
    )


# ============================================================================
# Asset Schemas
# ============================================================================

class AssetBase(BaseModel):
    """Base schema for Asset with common fields."""

    asset_group_id: int = Field(
        ...,
        description="Eszközcsoport azonosító",
        examples=[1, 2, 3]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Eszköz neve/megnevezése",
        examples=["Ipari mikró", "Dell XPS 15 laptop", "Fa asztal"]
    )
    inventory_number: Optional[str] = Field(
        None,
        max_length=100,
        description="Leltári szám (egyedi azonosító)",
        examples=["INV-2024-001", "IT-LAPTOP-042"]
    )
    manufacturer: Optional[str] = Field(
        None,
        max_length=255,
        description="Gyártó",
        examples=["Samsung", "Dell", "IKEA"]
    )
    model: Optional[str] = Field(
        None,
        max_length=255,
        description="Modell",
        examples=["XPS 15 9520", "Kallax"]
    )
    serial_number: Optional[str] = Field(
        None,
        max_length=255,
        description="Sorozatszám",
        examples=["SN123456789"]
    )
    purchase_date: Optional[date] = Field(
        None,
        description="Beszerzési dátum",
        examples=["2024-01-15"]
    )
    purchase_price: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Beszerzési ár",
        examples=[150000.00, 500000.00]
    )
    current_value: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Jelenlegi érték (becsült)",
        examples=[100000.00, 300000.00]
    )
    location: Optional[str] = Field(
        None,
        max_length=255,
        description="Helyszín/lokáció",
        examples=["Konyha", "Iroda", "Raktár"]
    )
    responsible_employee_id: Optional[int] = Field(
        None,
        description="Felelős munkatárs azonosító",
        examples=[1, 2, 3]
    )
    status: Optional[str] = Field(
        "ACTIVE",
        description="Státusz",
        examples=["ACTIVE", "MAINTENANCE", "RETIRED", "SOLD", "DAMAGED"]
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések",
        examples=["Garancia: 2026-01-15-ig"]
    )
    is_active: Optional[bool] = Field(
        True,
        description="Aktív státusz (logikai törlés)"
    )


class AssetCreate(AssetBase):
    """Schema for creating a new asset."""
    pass


class AssetUpdate(BaseModel):
    """Schema for updating an existing asset."""

    asset_group_id: Optional[int] = Field(
        None,
        description="Eszközcsoport azonosító"
    )
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Eszköz neve/megnevezése"
    )
    inventory_number: Optional[str] = Field(
        None,
        max_length=100,
        description="Leltári szám"
    )
    manufacturer: Optional[str] = Field(
        None,
        max_length=255,
        description="Gyártó"
    )
    model: Optional[str] = Field(
        None,
        max_length=255,
        description="Modell"
    )
    serial_number: Optional[str] = Field(
        None,
        max_length=255,
        description="Sorozatszám"
    )
    purchase_date: Optional[date] = Field(
        None,
        description="Beszerzési dátum"
    )
    purchase_price: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Beszerzési ár"
    )
    current_value: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Jelenlegi érték"
    )
    location: Optional[str] = Field(
        None,
        max_length=255,
        description="Helyszín/lokáció"
    )
    responsible_employee_id: Optional[int] = Field(
        None,
        description="Felelős munkatárs azonosító"
    )
    status: Optional[str] = Field(
        None,
        description="Státusz"
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Aktív státusz"
    )


class AssetResponse(BaseModel):
    """Schema for Asset response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Eszköz azonosító",
        examples=[1, 2, 3]
    )
    asset_group_id: int = Field(
        ...,
        description="Eszközcsoport azonosító"
    )
    name: str = Field(
        ...,
        description="Eszköz neve"
    )
    inventory_number: Optional[str] = Field(
        None,
        description="Leltári szám"
    )
    manufacturer: Optional[str] = Field(
        None,
        description="Gyártó"
    )
    model: Optional[str] = Field(
        None,
        description="Modell"
    )
    serial_number: Optional[str] = Field(
        None,
        description="Sorozatszám"
    )
    purchase_date: Optional[date] = Field(
        None,
        description="Beszerzési dátum"
    )
    purchase_price: Optional[Decimal] = Field(
        None,
        description="Beszerzési ár"
    )
    current_value: Optional[Decimal] = Field(
        None,
        description="Jelenlegi érték"
    )
    location: Optional[str] = Field(
        None,
        description="Helyszín/lokáció"
    )
    responsible_employee_id: Optional[int] = Field(
        None,
        description="Felelős munkatárs azonosító"
    )
    status: str = Field(
        ...,
        description="Státusz"
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések"
    )
    is_active: bool = Field(
        ...,
        description="Aktív státusz"
    )
    created_at: datetime = Field(
        ...,
        description="Létrehozás időpontja"
    )
    updated_at: datetime = Field(
        ...,
        description="Módosítás időpontja"
    )


# ============================================================================
# Asset Service Schemas
# ============================================================================

class AssetServiceBase(BaseModel):
    """Base schema for AssetService with common fields."""

    asset_id: int = Field(
        ...,
        description="Eszköz azonosító",
        examples=[1, 2, 3]
    )
    service_type: str = Field(
        ...,
        description="Szerviz típusa",
        examples=["MAINTENANCE", "REPAIR", "INSPECTION", "CALIBRATION", "CLEANING"]
    )
    service_date: date = Field(
        ...,
        description="Szerviz dátuma",
        examples=["2024-11-18"]
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Leírás/munka részletei",
        examples=["Éves karbantartás elvégezve", "Alkatrész csere"]
    )
    cost: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Költség",
        examples=[15000.00, 50000.00]
    )
    service_provider: Optional[str] = Field(
        None,
        max_length=255,
        description="Szervizes cég/személy",
        examples=["Szerviz Kft.", "János (belső)"]
    )
    next_service_date: Optional[date] = Field(
        None,
        description="Következő javasolt szerviz dátuma",
        examples=["2025-11-18"]
    )
    performed_by_employee_id: Optional[int] = Field(
        None,
        description="Végző munkatárs azonosító (belső szerviz esetén)",
        examples=[1, 2, 3]
    )
    documents_url: Optional[str] = Field(
        None,
        description="Dokumentumok/számlák URL-je",
        examples=["https://example.com/invoice.pdf"]
    )


class AssetServiceCreate(AssetServiceBase):
    """Schema for creating a new asset service record."""
    pass


class AssetServiceUpdate(BaseModel):
    """Schema for updating an existing asset service record."""

    service_type: Optional[str] = Field(
        None,
        description="Szerviz típusa"
    )
    service_date: Optional[date] = Field(
        None,
        description="Szerviz dátuma"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        description="Leírás/munka részletei"
    )
    cost: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Költség"
    )
    service_provider: Optional[str] = Field(
        None,
        max_length=255,
        description="Szervizes cég/személy"
    )
    next_service_date: Optional[date] = Field(
        None,
        description="Következő javasolt szerviz dátuma"
    )
    performed_by_employee_id: Optional[int] = Field(
        None,
        description="Végző munkatárs azonosító"
    )
    documents_url: Optional[str] = Field(
        None,
        description="Dokumentumok/számlák URL-je"
    )


class AssetServiceResponse(BaseModel):
    """Schema for AssetService response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Szerviz azonosító",
        examples=[1, 2, 3]
    )
    asset_id: int = Field(
        ...,
        description="Eszköz azonosító"
    )
    service_type: str = Field(
        ...,
        description="Szerviz típusa"
    )
    service_date: date = Field(
        ...,
        description="Szerviz dátuma"
    )
    description: str = Field(
        ...,
        description="Leírás/munka részletei"
    )
    cost: Optional[Decimal] = Field(
        None,
        description="Költség"
    )
    service_provider: Optional[str] = Field(
        None,
        description="Szervizes cég/személy"
    )
    next_service_date: Optional[date] = Field(
        None,
        description="Következő javasolt szerviz dátuma"
    )
    performed_by_employee_id: Optional[int] = Field(
        None,
        description="Végző munkatárs azonosító"
    )
    documents_url: Optional[str] = Field(
        None,
        description="Dokumentumok/számlák URL-je"
    )
    created_at: datetime = Field(
        ...,
        description="Létrehozás időpontja"
    )
    updated_at: datetime = Field(
        ...,
        description="Módosítás időpontja"
    )
