"""
OrderItem Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

A rendeléstételek táblája, amely tartalmazza a rendeléshez tartozó
termékeket, mennyiségeket, árakat és a kiválasztott módosítókat.
"""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.service_orders.models.database import Base
from backend.service_orders.models.order import CompatibleJSON


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
    selected_modifiers = Column(CompatibleJSON, nullable=True)  # [{'group_name': 'Zsemle', 'modifier_name': 'Szezamos', 'price': 0.00}] (JSONB in PostgreSQL, JSON in SQLite)
    course = Column(String(50), nullable=True)  # V3.0: Fogás (pl. 'Előétel', 'Főétel', 'Desszert')
    notes = Column(Text, nullable=True)  # V3.0: Tétel szintű megjegyzések
    discount_details = Column(CompatibleJSON, nullable=True)  # V3.0: Kedvezmény részletek {'type': 'percentage', 'value': 10} (JSONB in PostgreSQL, JSON in SQLite)
    kds_station = Column(String(50), nullable=True)  # 'Konyha', 'Pizza', 'Pult'
    kds_status = Column(String(50), nullable=False, default='VÁRAKOZIK')  # 'VÁRAKOZIK', 'KÉSZÜL', 'KÉSZ'

    # Relationships
    order = relationship('Order', back_populates='order_items')
    seat = relationship('Seat', back_populates='order_items')

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"
