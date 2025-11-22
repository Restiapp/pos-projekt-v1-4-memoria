"""
Finance Models - SQLAlchemy ORM
Module 8: Adminisztráció - Pénzügyi Kezelés (V3.0)

Pénzmozgások és napi pénztárzárás kezelése.
Támogatja a készpénzes tranzakciók nyomon követését és a napi elszámolást.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, Text, Index, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.service_admin.models.database import Base


class CashMovementType(str, enum.Enum):
    """Pénzmozgás típusok"""
    OPENING_BALANCE = "OPENING_BALANCE"  # Nyitó egyenleg
    CASH_IN = "CASH_IN"  # Készpénz befizetés
    CASH_OUT = "CASH_OUT"  # Készpénz kivétel
    SALE = "SALE"  # Értékesítés
    REFUND = "REFUND"  # Visszatérítés
    CORRECTION = "CORRECTION"  # Korrekció


class CashMovement(Base):
    """
    CashMovement (Pénzmozgás) modell - Pénzügyi tranzakciók naplózása.

    Támogatja:
    - Készpénzes tranzakciók nyomon követését
    - Befizetések és kivételek kezelését
    - Értékesítési tranzakciók rögzítését
    - Audit trail minden pénzmozgáshoz
    """
    __tablename__ = 'cash_movements'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Mozgás típusa (nyitó egyenleg, befizetés, kivétel, értékesítés, stb.)
    movement_type = Column(
        SQLEnum(CashMovementType, native_enum=False),
        nullable=False,
        index=True
    )

    # Összeg (pozitív = befizetés, negatív = kivétel)
    amount = Column(DECIMAL(10, 2), nullable=False)

    # Leírás/megjegyzés
    description = Column(Text, nullable=True)

    # Kapcsolódó rendelés azonosító (opcionális)
    order_id = Column(Integer, nullable=True, index=True)

    # Munkatárs aki végrehajtotta
    employee_id = Column(Integer, ForeignKey('employees.id', ondelete='SET NULL'), nullable=True, index=True)

    # Napi záráshoz kapcsolás (opcionális, amikor lezárásra kerül)
    daily_closure_id = Column(Integer, ForeignKey('daily_closures.id', ondelete='SET NULL'), nullable=True, index=True)

    # Automatikus időbélyegek
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )

    # Relationships
    employee = relationship('Employee', foreign_keys=[employee_id], lazy='selectin')
    daily_closure = relationship('DailyClosure', back_populates='cash_movements', lazy='selectin')

    def __repr__(self):
        return (
            f"<CashMovement(id={self.id}, "
            f"type='{self.movement_type}', "
            f"amount={self.amount}, "
            f"created_at='{self.created_at}')>"
        )


class ClosureStatus(str, enum.Enum):
    """Zárás státuszok"""
    OPEN = "OPEN"  # Nyitott
    IN_PROGRESS = "IN_PROGRESS"  # Folyamatban
    CLOSED = "CLOSED"  # Lezárt
    RECONCILED = "RECONCILED"  # Egyeztetve


class DailyClosure(Base):
    """
    DailyClosure (Napi Pénztárzárás) modell - Napi pénzügyi zárás kezelése.

    Támogatja:
    - Napi pénztár egyeztetését
    - Nyitó és záró egyenlegek rögzítését
    - Eltérések kezelését
    - Munkatárs felelősség hozzárendelését
    """
    __tablename__ = 'daily_closures'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Zárás dátuma
    closure_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)

    # Státusz
    status = Column(
        SQLEnum(ClosureStatus, native_enum=False),
        nullable=False,
        default=ClosureStatus.OPEN,
        index=True
    )

    # Nyitó egyenleg (a nap kezdetén a pénztárban lévő összeg)
    opening_balance = Column(DECIMAL(10, 2), nullable=False, default=0.00)

    # Várható záró egyenleg (számított érték a tranzakciók alapján)
    expected_closing_balance = Column(DECIMAL(10, 2), nullable=True)

    # Tényleges záró egyenleg (ténylegesen megszámolt összeg)
    actual_closing_balance = Column(DECIMAL(10, 2), nullable=True)

    # Eltérés (actual - expected)
    difference = Column(DECIMAL(10, 2), nullable=True)

    # Fizetési módok szerinti összegzés (payment_summary)
    # Formátum: {"KESZPENZ": 10000.00, "KARTYA": 5000.00, "SZEP_KARTYA": 2000.00}
    payment_summary = Column(JSONB, nullable=True)

    # Megjegyzések/indoklás
    notes = Column(Text, nullable=True)

    # Munkatárs aki a zárást végrehajtotta
    closed_by_employee_id = Column(Integer, ForeignKey('employees.id', ondelete='SET NULL'), nullable=True, index=True)

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

    # Lezárás időpontja
    closed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    closed_by = relationship('Employee', foreign_keys=[closed_by_employee_id], lazy='selectin')
    cash_movements = relationship('CashMovement', back_populates='daily_closure', lazy='selectin')

    def __repr__(self):
        return (
            f"<DailyClosure(id={self.id}, "
            f"date='{self.closure_date}', "
            f"status='{self.status}', "
            f"difference={self.difference})>"
        )


# Indexek a gyakori lekérdezésekhez
Index('idx_cash_movement_type_date', CashMovement.movement_type, CashMovement.created_at.desc())
Index('idx_cash_movement_employee_date', CashMovement.employee_id, CashMovement.created_at.desc())
Index('idx_daily_closure_date_status', DailyClosure.closure_date.desc(), DailyClosure.status)
