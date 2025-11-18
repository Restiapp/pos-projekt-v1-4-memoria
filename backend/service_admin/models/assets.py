"""
Assets Models - SQLAlchemy ORM
Module 8: Adminisztráció - Eszközkezelés (V3.0)

Tárgyi eszközök, eszközcsoportok és szervizek kezelése.
Támogatja az üzleti eszközök nyilvántartását és karbantartási előzményeit.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, Text, Boolean, Index, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.service_admin.models.database import Base


class AssetStatus(str, enum.Enum):
    """Eszköz státuszok"""
    ACTIVE = "ACTIVE"  # Használatban
    MAINTENANCE = "MAINTENANCE"  # Karbantartás alatt
    RETIRED = "RETIRED"  # Kivonva
    SOLD = "SOLD"  # Eladva
    DAMAGED = "DAMAGED"  # Sérült


class AssetGroup(Base):
    """
    AssetGroup (Eszközcsoport) modell - Eszközök kategorizálása.

    Támogatja:
    - Eszközök hierarchikus csoportosítását
    - Csoportonkénti kezelést és riportolást
    - Amortizációs szabályok csoportosítását
    """
    __tablename__ = 'asset_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Csoport neve (pl. "Konyhai berendezések", "IT eszközök", "Bútorok")
    name = Column(String(255), nullable=False, unique=True, index=True)

    # Leírás
    description = Column(Text, nullable=True)

    # Amortizációs ráta (százalék/év) - opcionális
    depreciation_rate = Column(DECIMAL(5, 2), nullable=True)

    # Várható élettartam (év) - opcionális
    expected_lifetime_years = Column(Integer, nullable=True)

    # Aktív státusz
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
    assets = relationship('Asset', back_populates='asset_group', lazy='selectin')

    def __repr__(self):
        return (
            f"<AssetGroup(id={self.id}, "
            f"name='{self.name}', "
            f"is_active={self.is_active})>"
        )


class Asset(Base):
    """
    Asset (Eszköz) modell - Tárgyi eszközök nyilvántartása.

    Támogatja:
    - Eszközök részletes adatainak tárolását
    - Beszerzési információk rögzítését
    - Státusz követést
    - Helyszín és felelős hozzárendelését
    """
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Eszközcsoport
    asset_group_id = Column(Integer, ForeignKey('asset_groups.id', ondelete='RESTRICT'), nullable=False, index=True)

    # Eszköz neve/megnevezése
    name = Column(String(255), nullable=False)

    # Leltári szám (egyedi azonosító)
    inventory_number = Column(String(100), nullable=True, unique=True, index=True)

    # Gyártó
    manufacturer = Column(String(255), nullable=True)

    # Modell
    model = Column(String(255), nullable=True)

    # Sorozatszám
    serial_number = Column(String(255), nullable=True, index=True)

    # Beszerzési dátum
    purchase_date = Column(Date, nullable=True, index=True)

    # Beszerzési ár
    purchase_price = Column(DECIMAL(10, 2), nullable=True)

    # Jelenlegi érték (becsült)
    current_value = Column(DECIMAL(10, 2), nullable=True)

    # Helyszín/lokáció
    location = Column(String(255), nullable=True)

    # Felelős munkatárs
    responsible_employee_id = Column(Integer, ForeignKey('employees.id', ondelete='SET NULL'), nullable=True, index=True)

    # Státusz
    status = Column(
        SQLEnum(AssetStatus, native_enum=False),
        nullable=False,
        default=AssetStatus.ACTIVE,
        index=True
    )

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
    asset_group = relationship('AssetGroup', back_populates='assets', lazy='selectin')
    responsible_employee = relationship('Employee', foreign_keys=[responsible_employee_id], lazy='selectin')
    services = relationship('AssetService', back_populates='asset', lazy='selectin')

    def __repr__(self):
        return (
            f"<Asset(id={self.id}, "
            f"name='{self.name}', "
            f"inventory_number='{self.inventory_number}', "
            f"status='{self.status}')>"
        )


class ServiceType(str, enum.Enum):
    """Szerviz típusok"""
    MAINTENANCE = "MAINTENANCE"  # Karbantartás
    REPAIR = "REPAIR"  # Javítás
    INSPECTION = "INSPECTION"  # Felülvizsgálat
    CALIBRATION = "CALIBRATION"  # Kalibrálás
    CLEANING = "CLEANING"  # Tisztítás


class AssetService(Base):
    """
    AssetService (Eszköz Szerviz) modell - Eszközök karbantartási előzményei.

    Támogatja:
    - Karbantartási munkák rögzítését
    - Javítások dokumentálását
    - Költségek nyomon követését
    - Következő szerviz időpontjának tervezését
    """
    __tablename__ = 'asset_services'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Eszköz
    asset_id = Column(Integer, ForeignKey('assets.id', ondelete='CASCADE'), nullable=False, index=True)

    # Szerviz típusa
    service_type = Column(
        SQLEnum(ServiceType, native_enum=False),
        nullable=False,
        index=True
    )

    # Szerviz dátuma
    service_date = Column(Date, nullable=False, index=True)

    # Leírás/munka részletei
    description = Column(Text, nullable=False)

    # Költség
    cost = Column(DECIMAL(10, 2), nullable=True)

    # Szervizes cég/személy
    service_provider = Column(String(255), nullable=True)

    # Következő javasolt szerviz dátuma
    next_service_date = Column(Date, nullable=True, index=True)

    # Végző munkatárs (belső, ha nem külső szerviz)
    performed_by_employee_id = Column(Integer, ForeignKey('employees.id', ondelete='SET NULL'), nullable=True, index=True)

    # Dokumentumok/számlák (opcionális URL vagy fájl elérési út)
    documents_url = Column(Text, nullable=True)

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
    asset = relationship('Asset', back_populates='services', lazy='selectin')
    performed_by = relationship('Employee', foreign_keys=[performed_by_employee_id], lazy='selectin')

    def __repr__(self):
        return (
            f"<AssetService(id={self.id}, "
            f"asset_id={self.asset_id}, "
            f"type='{self.service_type}', "
            f"date='{self.service_date}')>"
        )


# Indexek a gyakori lekérdezésekhez
Index('idx_asset_group_status', Asset.asset_group_id, Asset.status)
Index('idx_asset_active_purchase', Asset.is_active, Asset.purchase_date.desc())
Index('idx_asset_service_date', AssetService.asset_id, AssetService.service_date.desc())
Index('idx_asset_service_next_date', AssetService.next_service_date)
