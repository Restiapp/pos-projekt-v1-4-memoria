"""
Order Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

A rendelések táblája, amely tartalmazza a rendelés típusát, státuszát,
összegét, ÁFA kulcsát és NTAK adatokat.
"""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_orders.models.database import Base


class Order(Base):
    """
    Rendelés modell a POS rendszerhez.

    Támogatja:
    - Többcsatornás rendeléseket (order_type: 'Helyben', 'Elvitel', 'Kiszállítás')
    - Státusz kezelést (status: 'NYITOTT', 'FELDOLGOZVA', 'LEZART', 'SZTORNÓ')
    - NTAK-kompatibilis ÁFA váltást (final_vat_rate: 27.00 vagy 5.00)
    - NTAK adatszolgáltatás tárolást (ntak_data JSONB)
    - Ügyfél hivatkozást (customer_id) - V3.0
    - Megjegyzéseket (notes) - V3.0
    """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_type = Column(String(50), nullable=False)  # 'Helyben', 'Elvitel', 'Kiszállítás'
    status = Column(String(50), nullable=False, default='NYITOTT')  # 'NYITOTT', 'FELDOLGOZVA', 'LEZART', 'SZTORNÓ'
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=True)
    customer_id = Column(Integer, index=True, nullable=True)  # V3.0: Ügyfél hivatkozás
    courier_id = Column(Integer, index=True, nullable=True)  # V4.0: Futár hivatkozás (service_logistics)
    total_amount = Column(Numeric(10, 2), nullable=True)
    final_vat_rate = Column(Numeric(4, 2), nullable=False, default=27.00)  # NTAK: 27.00 vagy 5.00
    ntak_data = Column(JSONB, nullable=True)  # NTAK 'Rendelésösszesítő' adatai
    notes = Column(Text, nullable=True)  # V3.0: Megjegyzések a rendeléshez
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    table = relationship('Table', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    payments = relationship('Payment', back_populates='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Order(id={self.id}, type='{self.order_type}', status='{self.status}', total={self.total_amount})>"
