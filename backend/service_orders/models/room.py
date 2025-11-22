"""
Room Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

A helyiségek táblája, amely tartalmazza az étterem különböző tereit
(pl. Terasz, Belső terem) és azok méreteit a vizuális megjelenítéshez.
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from backend.service_orders.models.database import Base


class Room(Base):
    """
    Helyiség modell a POS rendszerhez.

    Támogatja:
    - Helyiség elnevezése (name)
    - Vizuális méretek (width, height) - Canvas mérete
    - Aktív státusz (is_active)
    """
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    width = Column(Integer, default=800, nullable=False)
    height = Column(Integer, default=600, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    tables = relationship('Table', back_populates='room', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}', size={self.width}x{self.height})>"
