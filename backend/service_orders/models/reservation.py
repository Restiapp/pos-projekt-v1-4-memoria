"""
Reservation Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

Foglalások táblája, amely tartalmazza a vendégek asztalfoglalásait.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_orders.models.database import Base


class Reservation(Base):
    """
    Foglalás modell a POS rendszerhez.

    Támogatja:
    - Asztal foglalást (table_id)
    - Vendég információk (customer_id, guest_name, guest_phone)
    - Foglalás időpontja (reservation_date, reservation_time)
    - Vendégszám (guest_count)
    - Státusz kezelés (status: PENDING, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW)
    - Speciális kérések (special_requests)
    """
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=False)
    customer_id = Column(Integer, nullable=True)  # CRM customer ID (optional)
    guest_name = Column(String(100), nullable=False)
    guest_phone = Column(String(20), nullable=True)
    guest_email = Column(String(100), nullable=True)
    reservation_date = Column(Date, nullable=False)
    reservation_time = Column(Time, nullable=False)
    guest_count = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, default=120)  # Default 2 hours
    status = Column(String(50), default='PENDING', nullable=False)  # PENDING, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW
    special_requests = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    table = relationship('Table', back_populates='reservations')

    def __repr__(self):
        return f"<Reservation(id={self.id}, guest_name='{self.guest_name}', date={self.reservation_date}, time={self.reservation_time}, status='{self.status}')>"
