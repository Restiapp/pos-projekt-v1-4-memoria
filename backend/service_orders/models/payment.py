"""
Payment Model - SQLAlchemy ORM
Module 4: Fizetések

A fizetések táblája, amely tartalmazza a fizetési módot, összeget,
státuszát és tranzakció azonosítót.
"""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_orders.models.database import Base


class Payment(Base):
    """
    Fizetés modell a POS rendszerhez.

    Támogatja:
    - Többféle fizetési módot (payment_method: 'KESZPENZ', 'KARTYA', 'ATUTALAS', 'SZEP_KARTYA', 'VOUCHER')
    - Státusz kezelést (status: 'FELDOLGOZAS_ALATT', 'SIKERES', 'SIKERTELEN', 'VISSZAUTASITVA', 'VISSZAVONVA')
    - Split payment (egy rendeléshez több fizetés is tartozhat)
    - Tranzakció nyomon követést (transaction_id)
    """
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    payment_method = Column(String(50), nullable=False)  # 'KESZPENZ', 'KARTYA', 'ATUTALAS', 'SZEP_KARTYA', 'VOUCHER'
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False, default='FELDOLGOZAS_ALATT')  # 'FELDOLGOZAS_ALATT', 'SIKERES', 'SIKERTELEN', 'VISSZAUTASITVA', 'VISSZAVONVA'
    transaction_id = Column(String(255), nullable=True)  # Külső fizetési szolgáltató tranzakció azonosító
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship('Order', back_populates='payments')

    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, method='{self.payment_method}', amount={self.amount}, status='{self.status}')>"
