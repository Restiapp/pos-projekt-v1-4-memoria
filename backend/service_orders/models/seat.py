"""
Seat Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

Az ülőhelyek táblája, amely az asztalokhoz tartozó egyedi helyeket reprezentálja.
Fontos a számlák személyenkénti felosztásához (split-check).
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.service_orders.models.database import Base


class Seat(Base):
    """
    Ülőhely modell a POS rendszerhez.

    Támogatja:
    - Asztalonkénti egyedi ülőhelyek azonosítását
    - Rendeléstételek személyenkénti hozzárendelését
    """
    __tablename__ = 'seats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=False)
    seat_number = Column(Integer, nullable=False)

    # Unique constraint for table_id and seat_number combination
    __table_args__ = (
        UniqueConstraint('table_id', 'seat_number', name='uq_table_seat'),
    )

    # Relationships
    table = relationship('Table', back_populates='seats')
    order_items = relationship('OrderItem', back_populates='seat')

    def __repr__(self):
        return f"<Seat(id={self.id}, table_id={self.table_id}, seat_number={self.seat_number})>"
