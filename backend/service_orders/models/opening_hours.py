"""
Opening Hours Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

A nyitvatartási idők táblája, amely tartalmazza az étterem nyitvatartását
hétköznapokon és különleges napokon (ünnepek, zárva tartás).
"""

from sqlalchemy import Column, Integer, String, Time, Date, Boolean
from sqlalchemy.sql import func

from backend.service_orders.models.database import Base


class OpeningHours(Base):
    """
    Nyitvatartási idők modell a POS rendszerhez.

    Támogatja:
    - Hétköznapi nyitvatartás kezelést (day_of_week: 0=Hétfő, 6=Vasárnap)
    - Speciális napok kezelését (special_date)
    - Zárva tartás jelzést (is_closed)
    - Rugalmas nyitás/zárás időpontok (open_time, close_time)

    Prioritási sorrend:
    1. Ha van special_date megadva, azt használjuk
    2. Ha nincs special_date, akkor day_of_week-et használjuk
    """
    __tablename__ = 'opening_hours'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Hétköznapi nyitvatartás (0=Hétfő, 6=Vasárnap)
    # NULL esetén ez egy speciális napi bejegyzés
    day_of_week = Column(Integer, nullable=True, index=True)

    # Speciális dátum (pl. ünnepek, zárva tartás)
    # NULL esetén ez egy általános hétköznapi bejegyzés
    special_date = Column(Date, nullable=True, unique=True, index=True)

    # Nyitvatartási idők
    open_time = Column(Time, nullable=True)  # NULL ha is_closed=True
    close_time = Column(Time, nullable=True)  # NULL ha is_closed=True

    # Zárva tartás jelző
    is_closed = Column(Boolean, nullable=False, default=False)

    # Opcionális leírás (pl. "Karácsonyi szünet", "Teraszon rövidebb nyitva tartás")
    description = Column(String(200), nullable=True)

    def __repr__(self):
        if self.special_date:
            return (
                f"<OpeningHours(special_date={self.special_date}, "
                f"{'CLOSED' if self.is_closed else f'{self.open_time}-{self.close_time}'})>"
            )
        else:
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            day_name = days[self.day_of_week] if self.day_of_week is not None else 'Unknown'
            return (
                f"<OpeningHours(day={day_name}, "
                f"{'CLOSED' if self.is_closed else f'{self.open_time}-{self.close_time}'})>"
            )
