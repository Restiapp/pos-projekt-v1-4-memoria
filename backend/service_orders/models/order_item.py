"""
OrderItem Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

A rendeléstételek táblája, amely tartalmazza a rendeléshez tartozó
termékeket, mennyiségeket, árakat és a kiválasztott módosítókat.
"""

import enum
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship

from backend.service_orders.models.database import Base, CompatibleJSON


class KDSStatus(str, enum.Enum):
    """Kitchen Display System status enumeration for order items."""
    WAITING = "WAITING"
    PREPARING = "PREPARING"
    READY = "READY"
    SERVED = "SERVED"


class OrderItem(Base):
    """
    Rendeléstétel modell a POS rendszerhez.

    Támogatja:
    - Rendeléshez tartozó tételek kezelését
    - Termék módosítók tárolását (selected_modifiers JSONB)
    - Személyenkénti számla felosztást (seat_id)
    - Konyhai kijelző integrációt (kds_station, kds_status)
    - Fogások kezelését (course) - V3.0
    - Tétel szintű megjegyzéseket (notes) - V3.0
    - Kedvezmények részletezését (discount_details) - V3.0
    """
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, nullable=False)  # Reference to service_menu.products.id
    seat_id = Column(Integer, ForeignKey('seats.id'), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    selected_modifiers = Column(CompatibleJSON, nullable=True)  # [{'group_name': 'Zsemle', 'modifier_name': 'Szezamos', 'price': 0.00}]
    course = Column(String(50), nullable=True)  # V3.0: Fogás (pl. 'Előétel', 'Főétel', 'Desszert')
    notes = Column(Text, nullable=True)  # V3.0: Tétel szintű megjegyzések
    discount_details = Column(CompatibleJSON, nullable=True)  # V3.0: Kedvezmény részletek {'type': 'percentage', 'value': 10}
    kds_station = Column(String(50), nullable=True)  # Kitchen station: 'GRILL', 'COLD', 'BAR', etc.
    kds_status = Column(SQLEnum(KDSStatus, native_enum=False), nullable=False, default=KDSStatus.WAITING, index=True)  # Kitchen Display System status
    is_urgent = Column(Boolean, nullable=False, default=False, index=True)  # Urgent flag for KDS priority items

    # Relationships
    order = relationship('Order', back_populates='order_items')
    seat = relationship('Seat', back_populates='order_items')

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"
