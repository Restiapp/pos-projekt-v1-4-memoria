"""
Courier Model - SQLAlchemy ORM
V3.0 Module: Logistics Service

A futárok táblája, amely tartalmazza a futárok adatait, beleértve
a nevüket, telefonszámukat, státuszukat és az aktív állapotukat.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum

from backend.service_logistics.models.database import Base


class CourierStatus(str, enum.Enum):
    """
    Futár státusz enumeration.

    - AVAILABLE: Elérhető, fogadhat új megrendeléseket
    - ON_DELIVERY: Kiszállítás alatt
    - OFFLINE: Offline, nem elérhető
    - BREAK: Szünetben
    """
    AVAILABLE = "available"
    ON_DELIVERY = "on_delivery"
    OFFLINE = "offline"
    BREAK = "break"


class Courier(Base):
    """
    Futár modell a POS rendszerhez.

    Támogatja:
    - Futár azonosítást (courier_name, phone)
    - Email címet (email)
    - Státusz követést (status)
    - Aktív/inaktív státusz kezelést (is_active)
    - Időbélyegeket (created_at, updated_at)
    """
    __tablename__ = 'couriers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    courier_name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)

    # Status tracking
    status = Column(
        Enum(CourierStatus),
        default=CourierStatus.OFFLINE,
        nullable=False,
        index=True
    )

    # Active/Inactive
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Courier(id={self.id}, name='{self.courier_name}', status='{self.status}', active={self.is_active})>"
