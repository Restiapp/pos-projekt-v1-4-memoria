"""
Modifier Model - SQLAlchemy ORM
Module 0: Terméktörzs és Menü

Egyedi módosítók kezelése egy csoporton belül.
Például "Szezámos zsemle", "Extra sajt".
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_menu.models.base import Base


class Modifier(Base):
    """
    Módosító modell.

    Támogatja:
    - Ár módosítást (felár/kedvezmény)
    - Alapértelmezett kiválasztást
    - Kapcsolatot módosító csoportokhoz
    """
    __tablename__ = 'modifiers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('modifier_groups.id'), nullable=False)
    name = Column(String(255), nullable=False)
    price_modifier = Column(Numeric(10, 2), default=0.00)
    is_default = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    group = relationship('ModifierGroup', back_populates='modifiers')

    def __repr__(self):
        return f"<Modifier(id={self.id}, name='{self.name}', price_modifier={self.price_modifier})>"
