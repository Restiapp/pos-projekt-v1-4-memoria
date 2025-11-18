"""
Vehicles Models - SQLAlchemy ORM
Module 8: Adminisztráció - Járműkezelés (V3.0)

Járművek, tankolások és karbantartások kezelése.
Támogatja a céges járművek nyilvántartását és költségeinek nyomon követését.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, Text, Boolean, Index, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.service_admin.models.database import Base


class VehicleStatus(str, enum.Enum):
    """Jármű státuszok"""
    ACTIVE = "ACTIVE"  # Használatban
    MAINTENANCE = "MAINTENANCE"  # Karbantartás alatt
    OUT_OF_SERVICE = "OUT_OF_SERVICE"  # Nem üzemképes
    SOLD = "SOLD"  # Eladva
    RETIRED = "RETIRED"  # Kivonva


class FuelType(str, enum.Enum):
    """Üzemanyag típusok"""
    PETROL_95 = "PETROL_95"  # 95-ös benzin
    PETROL_98 = "PETROL_98"  # 98-as benzin
    DIESEL = "DIESEL"  # Dízel
    ELECTRIC = "ELECTRIC"  # Elektromos
    HYBRID = "HYBRID"  # Hibrid
    LPG = "LPG"  # Gázolaj


class Vehicle(Base):
    """
    Vehicle (Jármű) modell - Céges járművek nyilvántartása.

    Támogatja:
    - Járművek alapadatainak tárolását
    - Státusz követést
    - Felelős hozzárendelését
    - Költségek nyomon követését
    """
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Rendszám (egyedi azonosító)
    license_plate = Column(String(20), nullable=False, unique=True, index=True)

    # Márka
    brand = Column(String(100), nullable=False)

    # Modell
    model = Column(String(100), nullable=False)

    # Gyártási év
    year = Column(Integer, nullable=True)

    # VIN (Vehicle Identification Number)
    vin = Column(String(17), nullable=True, unique=True, index=True)

    # Üzemanyag típusa
    fuel_type = Column(
        SQLEnum(FuelType, native_enum=False),
        nullable=False,
        index=True
    )

    # Beszerzési dátum
    purchase_date = Column(Date, nullable=True, index=True)

    # Beszerzési ár
    purchase_price = Column(DECIMAL(10, 2), nullable=True)

    # Jelenlegi érték (becsült)
    current_value = Column(DECIMAL(10, 2), nullable=True)

    # Aktuális kilométeróra állás
    current_mileage = Column(Integer, nullable=True)

    # Felelős munkatárs (aki használja)
    responsible_employee_id = Column(Integer, ForeignKey('employees.id', ondelete='SET NULL'), nullable=True, index=True)

    # Státusz
    status = Column(
        SQLEnum(VehicleStatus, native_enum=False),
        nullable=False,
        default=VehicleStatus.ACTIVE,
        index=True
    )

    # Biztosítás lejárata
    insurance_expiry_date = Column(Date, nullable=True, index=True)

    # Műszaki vizsga lejárata
    mot_expiry_date = Column(Date, nullable=True, index=True)

    # Megjegyzések
    notes = Column(Text, nullable=True)

    # Aktív státusz (logikai törlés)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    # Automatikus időbélyegek
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    responsible_employee = relationship('Employee', foreign_keys=[responsible_employee_id], lazy='selectin')
    refuelings = relationship('VehicleRefueling', back_populates='vehicle', lazy='selectin')
    maintenances = relationship('VehicleMaintenance', back_populates='vehicle', lazy='selectin')

    def __repr__(self):
        return (
            f"<Vehicle(id={self.id}, "
            f"license_plate='{self.license_plate}', "
            f"brand='{self.brand}', "
            f"model='{self.model}', "
            f"status='{self.status}')>"
        )


class VehicleRefueling(Base):
    """
    VehicleRefueling (Jármű Tankolás) modell - Tankolási előzmények.

    Támogatja:
    - Tankolások rögzítését
    - Üzemanyag költségek nyomon követését
    - Fogyasztás elemzését
    - Kilométeróra állás követését
    """
    __tablename__ = 'vehicle_refuelings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Jármű
    vehicle_id = Column(Integer, ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False, index=True)

    # Tankolás dátuma
    refueling_date = Column(Date, nullable=False, index=True)

    # Kilométeróra állás tankoláskor
    mileage = Column(Integer, nullable=True)

    # Üzemanyag típusa
    fuel_type = Column(
        SQLEnum(FuelType, native_enum=False),
        nullable=False
    )

    # Mennyiség (liter)
    quantity_liters = Column(DECIMAL(10, 2), nullable=False)

    # Egységár (Ft/liter)
    price_per_liter = Column(DECIMAL(10, 2), nullable=False)

    # Teljes költség
    total_cost = Column(DECIMAL(10, 2), nullable=False)

    # Tele tank (True = teletankolás, False = részleges)
    full_tank = Column(Boolean, nullable=False, default=True)

    # Benzinkút / helyszín
    location = Column(String(255), nullable=True)

    # Számla szám
    invoice_number = Column(String(100), nullable=True)

    # Rögzítő munkatárs
    recorded_by_employee_id = Column(Integer, ForeignKey('employees.id', ondelete='SET NULL'), nullable=True, index=True)

    # Megjegyzések
    notes = Column(Text, nullable=True)

    # Automatikus időbélyegek
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    vehicle = relationship('Vehicle', back_populates='refuelings', lazy='selectin')
    recorded_by = relationship('Employee', foreign_keys=[recorded_by_employee_id], lazy='selectin')

    def __repr__(self):
        return (
            f"<VehicleRefueling(id={self.id}, "
            f"vehicle_id={self.vehicle_id}, "
            f"date='{self.refueling_date}', "
            f"quantity={self.quantity_liters}L, "
            f"cost={self.total_cost})>"
        )


class MaintenanceType(str, enum.Enum):
    """Karbantartás típusok"""
    REGULAR_SERVICE = "REGULAR_SERVICE"  # Rendszeres szerviz
    REPAIR = "REPAIR"  # Javítás
    TIRE_CHANGE = "TIRE_CHANGE"  # Gumicsere
    OIL_CHANGE = "OIL_CHANGE"  # Olajcsere
    BRAKE_SERVICE = "BRAKE_SERVICE"  # Fékszerviz
    MOT = "MOT"  # Műszaki vizsga
    OTHER = "OTHER"  # Egyéb


class VehicleMaintenance(Base):
    """
    VehicleMaintenance (Jármű Karbantartás) modell - Karbantartási előzmények.

    Támogatja:
    - Karbantartások és javítások rögzítését
    - Költségek nyomon követését
    - Következő szerviz időpontjának tervezését
    - Kilométeróra állás követését
    """
    __tablename__ = 'vehicle_maintenances'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Jármű
    vehicle_id = Column(Integer, ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False, index=True)

    # Karbantartás típusa
    maintenance_type = Column(
        SQLEnum(MaintenanceType, native_enum=False),
        nullable=False,
        index=True
    )

    # Karbantartás dátuma
    maintenance_date = Column(Date, nullable=False, index=True)

    # Kilométeróra állás karbantartáskor
    mileage = Column(Integer, nullable=True)

    # Leírás/munka részletei
    description = Column(Text, nullable=False)

    # Költség
    cost = Column(DECIMAL(10, 2), nullable=True)

    # Szerviz / javítóműhely
    service_provider = Column(String(255), nullable=True)

    # Következő javasolt karbantartás dátuma
    next_maintenance_date = Column(Date, nullable=True, index=True)

    # Következő javasolt karbantartás kilométeróra állás
    next_maintenance_mileage = Column(Integer, nullable=True)

    # Számla szám
    invoice_number = Column(String(100), nullable=True)

    # Rögzítő munkatárs
    recorded_by_employee_id = Column(Integer, ForeignKey('employees.id', ondelete='SET NULL'), nullable=True, index=True)

    # Megjegyzések
    notes = Column(Text, nullable=True)

    # Automatikus időbélyegek
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    vehicle = relationship('Vehicle', back_populates='maintenances', lazy='selectin')
    recorded_by = relationship('Employee', foreign_keys=[recorded_by_employee_id], lazy='selectin')

    def __repr__(self):
        return (
            f"<VehicleMaintenance(id={self.id}, "
            f"vehicle_id={self.vehicle_id}, "
            f"type='{self.maintenance_type}', "
            f"date='{self.maintenance_date}')>"
        )


# Indexek a gyakori lekérdezésekhez
Index('idx_vehicle_status_active', Vehicle.status, Vehicle.is_active)
Index('idx_vehicle_insurance_expiry', Vehicle.insurance_expiry_date)
Index('idx_vehicle_mot_expiry', Vehicle.mot_expiry_date)
Index('idx_refueling_vehicle_date', VehicleRefueling.vehicle_id, VehicleRefueling.refueling_date.desc())
Index('idx_maintenance_vehicle_date', VehicleMaintenance.vehicle_id, VehicleMaintenance.maintenance_date.desc())
Index('idx_maintenance_next_date', VehicleMaintenance.next_maintenance_date)
