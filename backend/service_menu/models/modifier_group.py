"""
ModifierGroup Model - SQLAlchemy ORM
Module 0: Terméktörzs és Menü

Módosító csoportok kezelése, például "Zsemle típus", "Extra feltétek".
Definiálja a választási szabályokat (min/max selection).
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_menu.models.base import Base


class ModifierGroup(Base):
    """
    Módosító csoport modell.

    Támogatja:
    - Különböző választási típusokat (SINGLE_CHOICE_REQUIRED, MULTIPLE_CHOICE_OPTIONAL)
    - Min/max kiválasztási szabályokat
    - Kapcsolatot módosítókhoz és termékekhez
    """
    __tablename__ = 'modifier_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    selection_type = Column(String(50), nullable=False)  # 'SINGLE_CHOICE_REQUIRED', 'MULTIPLE_CHOICE_OPTIONAL'
    min_selection = Column(Integer, default=0)
    max_selection = Column(Integer, default=1)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    modifiers = relationship('Modifier', back_populates='group', cascade='all, delete-orphan')
    products = relationship(
        'Product',
        secondary='product_modifier_group_associations',
        back_populates='modifier_groups'
    )

    def __repr__(self):
        return f"<ModifierGroup(id={self.id}, name='{self.name}', type='{self.selection_type}')>"
