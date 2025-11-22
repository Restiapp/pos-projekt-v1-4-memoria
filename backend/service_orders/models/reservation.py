"""
Reservation Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

Az asztalfoglalások táblája, amely tartalmazza a foglalás adatait,
vendég információkat, időpontokat és státuszokat.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.service_orders.models.database import Base


class ReservationStatus(str, enum.Enum):
    """Foglalás státuszok"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class ReservationSource(str, enum.Enum):
    """Foglalás forrása"""
    MANUAL = "MANUAL"  # Személyzet által rögzített
    AI = "AI"          # AI Chatbot által létrehozott
    WEB = "WEB"        # Webes felületen keresztül


class Reservation(Base):
    """
    Foglalás modell a POS rendszerhez.

    Támogatja:
    - Asztalfoglalások kezelését (table_id FK)
    - Vendég információk tárolását (név, telefon, email)
    - Időpont és időtartam kezelést
    - Státusz követést (PENDING, CONFIRMED, CANCELLED, COMPLETED)
    - Forrás azonosítást (MANUAL, AI, WEB)
    - Speciális kérések tárolását (notes)
    """
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=False, index=True)

    # Vendég információk
    customer_name = Column(String(200), nullable=False)
    customer_phone = Column(String(50), nullable=True, index=True)
    customer_email = Column(String(200), nullable=True, index=True)

    # Foglalás részletei
    start_time = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=120)  # Default 2 óra
    guest_count = Column(Integer, nullable=False)

    # Státusz és forrás
    status = Column(
        SQLEnum(ReservationStatus),
        nullable=False,
        default=ReservationStatus.PENDING,
        index=True
    )
    source = Column(
        SQLEnum(ReservationSource),
        nullable=False,
        default=ReservationSource.MANUAL,
        index=True
    )

    # További információk
    notes = Column(Text, nullable=True)

    # Időbélyegek
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    table = relationship('Table')

    def __repr__(self):
        return (
            f"<Reservation(id={self.id}, table_id={self.table_id}, "
            f"customer='{self.customer_name}', start_time={self.start_time}, "
            f"status='{self.status}')>"
        )
