"""
Allergen Model - SQLAlchemy ORM
Module 0: Terméktörzs és Menü

Allergének táblázata az éttermi megfelelőség biztosításához.
Támogatja az allergének kódját, nevét és ikonját.
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_menu.models.base import Base


class Allergen(Base):
    """
    Allergén modell a POS rendszerhez.

    Támogatja:
    - Kód (code) pl. "GL" a gluténhoz
    - Név (name) pl. "Glutén"
    - Ikon URL (icon_url) az allergén vizuális megjelenítéséhez
    """
    __tablename__ = 'allergens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # pl. "GL", "MILK", "NUTS"
    name = Column(String(100), nullable=False)  # pl. "Glutén", "Tej", "Mogyoró"
    icon_url = Column(String(500), nullable=True)  # URL az allergén ikonjához
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    products = relationship(
        'Product',
        secondary='product_allergen_associations',
        back_populates='allergens'
    )

    def __repr__(self):
        return f"<Allergen(id={self.id}, code='{self.code}', name='{self.name}')>"
