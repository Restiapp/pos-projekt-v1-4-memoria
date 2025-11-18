"""
DeliveryZone Model - SQLAlchemy ORM
V3.0 Module: Logistics Service

A kiszállítási zónák táblája, amely tartalmazza a különböző kiszállítási
területek adatait, beleértve a zóna nevét, leírását, kiszállítási díját
és az aktív státuszt.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func

from backend.service_logistics.models.database import Base


class DeliveryZone(Base):
    """
    Kiszállítási zóna modell a POS rendszerhez.

    Támogatja:
    - Egyedi zóna azonosítást (zone_name)
    - Részletes leírást (description)
    - Kiszállítási díj kezelést (delivery_fee)
    - Minimális rendelési értéket (min_order_value)
    - Becsült szállítási időt (estimated_delivery_time_minutes)
    - Aktív/inaktív státusz kezelést (is_active)
    - Időbélyegeket (created_at, updated_at)
    """
    __tablename__ = 'delivery_zones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    # Pricing and limits
    delivery_fee = Column(Float, nullable=False, default=0.0)
    min_order_value = Column(Float, nullable=False, default=0.0)

    # Delivery time estimation
    estimated_delivery_time_minutes = Column(Integer, nullable=False, default=30)

    # V3.0 / Phase 3.B: ZIP code coverage
    zip_codes = Column(JSON, nullable=True, default=list)

    # V3.0 / Phase 4.2: GeoJSON polygon for Point-in-Polygon lookup
    polygon = Column(JSON, nullable=True, default=None)

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<DeliveryZone(id={self.id}, zone_name='{self.zone_name}', fee={self.delivery_fee}, active={self.is_active})>"
