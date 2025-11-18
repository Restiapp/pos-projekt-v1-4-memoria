"""
Pydantic schemas for Vehicles (Járművek) entities.

This module defines the request and response schemas for vehicle management operations
in the Service Admin module, including vehicles, refuelings, and maintenances.
"""

from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Vehicle Schemas
# ============================================================================

class VehicleBase(BaseModel):
    """Base schema for Vehicle with common fields."""

    license_plate: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Rendszám (egyedi azonosító)",
        examples=["ABC-123", "XYZ-999"]
    )
    brand: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Márka",
        examples=["Toyota", "Ford", "Mercedes-Benz"]
    )
    model: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Modell",
        examples=["Corolla", "Transit", "Sprinter"]
    )
    year: Optional[int] = Field(
        None,
        ge=1900,
        le=2100,
        description="Gyártási év",
        examples=[2020, 2021, 2022]
    )
    vin: Optional[str] = Field(
        None,
        max_length=17,
        description="VIN (Vehicle Identification Number)",
        examples=["1HGBH41JXMN109186"]
    )
    fuel_type: str = Field(
        ...,
        description="Üzemanyag típusa",
        examples=["PETROL_95", "DIESEL", "ELECTRIC", "HYBRID"]
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
        examples=[5000000.00, 8000000.00]
    )
    current_value: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Jelenlegi érték (becsült)",
        examples=[4000000.00, 6000000.00]
    )
    current_mileage: Optional[int] = Field(
        None,
        ge=0,
        description="Aktuális kilométeróra állás",
        examples=[50000, 100000]
    )
    responsible_employee_id: Optional[int] = Field(
        None,
        description="Felelős munkatárs azonosító",
        examples=[1, 2, 3]
    )
    status: Optional[str] = Field(
        "ACTIVE",
        description="Státusz",
        examples=["ACTIVE", "MAINTENANCE", "OUT_OF_SERVICE", "SOLD", "RETIRED"]
    )
    insurance_expiry_date: Optional[date] = Field(
        None,
        description="Biztosítás lejárata",
        examples=["2025-12-31"]
    )
    mot_expiry_date: Optional[date] = Field(
        None,
        description="Műszaki vizsga lejárata",
        examples=["2025-06-30"]
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések",
        examples=["Cégautó, céges használatra"]
    )
    is_active: Optional[bool] = Field(
        True,
        description="Aktív státusz (logikai törlés)"
    )


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle."""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating an existing vehicle."""

    license_plate: Optional[str] = Field(
        None,
        min_length=1,
        max_length=20,
        description="Rendszám"
    )
    brand: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Márka"
    )
    model: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Modell"
    )
    year: Optional[int] = Field(
        None,
        ge=1900,
        le=2100,
        description="Gyártási év"
    )
    vin: Optional[str] = Field(
        None,
        max_length=17,
        description="VIN"
    )
    fuel_type: Optional[str] = Field(
        None,
        description="Üzemanyag típusa"
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
    current_mileage: Optional[int] = Field(
        None,
        ge=0,
        description="Aktuális kilométeróra állás"
    )
    responsible_employee_id: Optional[int] = Field(
        None,
        description="Felelős munkatárs azonosító"
    )
    status: Optional[str] = Field(
        None,
        description="Státusz"
    )
    insurance_expiry_date: Optional[date] = Field(
        None,
        description="Biztosítás lejárata"
    )
    mot_expiry_date: Optional[date] = Field(
        None,
        description="Műszaki vizsga lejárata"
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Aktív státusz"
    )


class VehicleResponse(BaseModel):
    """Schema for Vehicle response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Jármű azonosító",
        examples=[1, 2, 3]
    )
    license_plate: str = Field(
        ...,
        description="Rendszám"
    )
    brand: str = Field(
        ...,
        description="Márka"
    )
    model: str = Field(
        ...,
        description="Modell"
    )
    year: Optional[int] = Field(
        None,
        description="Gyártási év"
    )
    vin: Optional[str] = Field(
        None,
        description="VIN"
    )
    fuel_type: str = Field(
        ...,
        description="Üzemanyag típusa"
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
    current_mileage: Optional[int] = Field(
        None,
        description="Aktuális kilométeróra állás"
    )
    responsible_employee_id: Optional[int] = Field(
        None,
        description="Felelős munkatárs azonosító"
    )
    status: str = Field(
        ...,
        description="Státusz"
    )
    insurance_expiry_date: Optional[date] = Field(
        None,
        description="Biztosítás lejárata"
    )
    mot_expiry_date: Optional[date] = Field(
        None,
        description="Műszaki vizsga lejárata"
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
# Vehicle Refueling Schemas
# ============================================================================

class VehicleRefuelingBase(BaseModel):
    """Base schema for VehicleRefueling with common fields."""

    vehicle_id: int = Field(
        ...,
        description="Jármű azonosító",
        examples=[1, 2, 3]
    )
    refueling_date: date = Field(
        ...,
        description="Tankolás dátuma",
        examples=["2024-11-18"]
    )
    mileage: Optional[int] = Field(
        None,
        ge=0,
        description="Kilométeróra állás tankoláskor",
        examples=[50000, 100000]
    )
    fuel_type: str = Field(
        ...,
        description="Üzemanyag típusa",
        examples=["PETROL_95", "DIESEL", "ELECTRIC"]
    )
    quantity_liters: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Mennyiség (liter)",
        examples=[50.00, 75.50]
    )
    price_per_liter: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Egységár (Ft/liter)",
        examples=[600.00, 650.00]
    )
    total_cost: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Teljes költség",
        examples=[30000.00, 49075.00]
    )
    full_tank: Optional[bool] = Field(
        True,
        description="Tele tank (True = teletankolás, False = részleges)"
    )
    location: Optional[str] = Field(
        None,
        max_length=255,
        description="Benzinkút / helyszín",
        examples=["MOL Kútnál", "Shell Budapest"]
    )
    invoice_number: Optional[str] = Field(
        None,
        max_length=100,
        description="Számla szám",
        examples=["INV-2024-001"]
    )
    recorded_by_employee_id: Optional[int] = Field(
        None,
        description="Rögzítő munkatárs azonosító",
        examples=[1, 2, 3]
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések",
        examples=["Autópályán tankoltam"]
    )


class VehicleRefuelingCreate(VehicleRefuelingBase):
    """Schema for creating a new vehicle refueling record."""
    pass


class VehicleRefuelingUpdate(BaseModel):
    """Schema for updating an existing vehicle refueling record."""

    refueling_date: Optional[date] = Field(
        None,
        description="Tankolás dátuma"
    )
    mileage: Optional[int] = Field(
        None,
        ge=0,
        description="Kilométeróra állás tankoláskor"
    )
    fuel_type: Optional[str] = Field(
        None,
        description="Üzemanyag típusa"
    )
    quantity_liters: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Mennyiség (liter)"
    )
    price_per_liter: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Egységár (Ft/liter)"
    )
    total_cost: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Teljes költség"
    )
    full_tank: Optional[bool] = Field(
        None,
        description="Tele tank"
    )
    location: Optional[str] = Field(
        None,
        max_length=255,
        description="Benzinkút / helyszín"
    )
    invoice_number: Optional[str] = Field(
        None,
        max_length=100,
        description="Számla szám"
    )
    recorded_by_employee_id: Optional[int] = Field(
        None,
        description="Rögzítő munkatárs azonosító"
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések"
    )


class VehicleRefuelingResponse(BaseModel):
    """Schema for VehicleRefueling response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Tankolás azonosító",
        examples=[1, 2, 3]
    )
    vehicle_id: int = Field(
        ...,
        description="Jármű azonosító"
    )
    refueling_date: date = Field(
        ...,
        description="Tankolás dátuma"
    )
    mileage: Optional[int] = Field(
        None,
        description="Kilométeróra állás tankoláskor"
    )
    fuel_type: str = Field(
        ...,
        description="Üzemanyag típusa"
    )
    quantity_liters: Decimal = Field(
        ...,
        description="Mennyiség (liter)"
    )
    price_per_liter: Decimal = Field(
        ...,
        description="Egységár (Ft/liter)"
    )
    total_cost: Decimal = Field(
        ...,
        description="Teljes költség"
    )
    full_tank: bool = Field(
        ...,
        description="Tele tank"
    )
    location: Optional[str] = Field(
        None,
        description="Benzinkút / helyszín"
    )
    invoice_number: Optional[str] = Field(
        None,
        description="Számla szám"
    )
    recorded_by_employee_id: Optional[int] = Field(
        None,
        description="Rögzítő munkatárs azonosító"
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések"
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
# Vehicle Maintenance Schemas
# ============================================================================

class VehicleMaintenanceBase(BaseModel):
    """Base schema for VehicleMaintenance with common fields."""

    vehicle_id: int = Field(
        ...,
        description="Jármű azonosító",
        examples=[1, 2, 3]
    )
    maintenance_type: str = Field(
        ...,
        description="Karbantartás típusa",
        examples=["REGULAR_SERVICE", "REPAIR", "TIRE_CHANGE", "OIL_CHANGE", "BRAKE_SERVICE", "MOT", "OTHER"]
    )
    maintenance_date: date = Field(
        ...,
        description="Karbantartás dátuma",
        examples=["2024-11-18"]
    )
    mileage: Optional[int] = Field(
        None,
        ge=0,
        description="Kilométeróra állás karbantartáskor",
        examples=[50000, 100000]
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Leírás/munka részletei",
        examples=["Olajcsere és szűrőcsere", "Abroncs csere téli gumira"]
    )
    cost: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Költség",
        examples=[25000.00, 100000.00]
    )
    service_provider: Optional[str] = Field(
        None,
        max_length=255,
        description="Szerviz / javítóműhely",
        examples=["AutoSzerviz Kft.", "Belső szerelő"]
    )
    next_maintenance_date: Optional[date] = Field(
        None,
        description="Következő javasolt karbantartás dátuma",
        examples=["2025-11-18"]
    )
    next_maintenance_mileage: Optional[int] = Field(
        None,
        ge=0,
        description="Következő javasolt karbantartás kilométeróra állás",
        examples=[60000, 110000]
    )
    invoice_number: Optional[str] = Field(
        None,
        max_length=100,
        description="Számla szám",
        examples=["SRV-2024-001"]
    )
    recorded_by_employee_id: Optional[int] = Field(
        None,
        description="Rögzítő munkatárs azonosító",
        examples=[1, 2, 3]
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések",
        examples=["Következő szerviz 10,000 km múlva"]
    )


class VehicleMaintenanceCreate(VehicleMaintenanceBase):
    """Schema for creating a new vehicle maintenance record."""
    pass


class VehicleMaintenanceUpdate(BaseModel):
    """Schema for updating an existing vehicle maintenance record."""

    maintenance_type: Optional[str] = Field(
        None,
        description="Karbantartás típusa"
    )
    maintenance_date: Optional[date] = Field(
        None,
        description="Karbantartás dátuma"
    )
    mileage: Optional[int] = Field(
        None,
        ge=0,
        description="Kilométeróra állás karbantartáskor"
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
        description="Szerviz / javítóműhely"
    )
    next_maintenance_date: Optional[date] = Field(
        None,
        description="Következő javasolt karbantartás dátuma"
    )
    next_maintenance_mileage: Optional[int] = Field(
        None,
        ge=0,
        description="Következő javasolt karbantartás kilométeróra állás"
    )
    invoice_number: Optional[str] = Field(
        None,
        max_length=100,
        description="Számla szám"
    )
    recorded_by_employee_id: Optional[int] = Field(
        None,
        description="Rögzítő munkatárs azonosító"
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések"
    )


class VehicleMaintenanceResponse(BaseModel):
    """Schema for VehicleMaintenance response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Karbantartás azonosító",
        examples=[1, 2, 3]
    )
    vehicle_id: int = Field(
        ...,
        description="Jármű azonosító"
    )
    maintenance_type: str = Field(
        ...,
        description="Karbantartás típusa"
    )
    maintenance_date: date = Field(
        ...,
        description="Karbantartás dátuma"
    )
    mileage: Optional[int] = Field(
        None,
        description="Kilométeróra állás karbantartáskor"
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
        description="Szerviz / javítóműhely"
    )
    next_maintenance_date: Optional[date] = Field(
        None,
        description="Következő javasolt karbantartás dátuma"
    )
    next_maintenance_mileage: Optional[int] = Field(
        None,
        description="Következő javasolt karbantartás kilométeróra állás"
    )
    invoice_number: Optional[str] = Field(
        None,
        description="Számla szám"
    )
    recorded_by_employee_id: Optional[int] = Field(
        None,
        description="Rögzítő munkatárs azonosító"
    )
    notes: Optional[str] = Field(
        None,
        description="Megjegyzések"
    )
    created_at: datetime = Field(
        ...,
        description="Létrehozás időpontja"
    )
    updated_at: datetime = Field(
        ...,
        description="Módosítás időpontja"
    )
