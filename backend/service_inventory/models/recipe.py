"""
Recipe Model - SQLAlchemy ORM
Module 5: Készletkezelés

A receptek táblája, amely összeköti a termékeket (products)
az alapanyagokkal (inventory_items) és meghatározza a felhasznált mennyiséget.
"""

from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from backend.service_inventory.models.database import Base


class Recipe(Base):
    """
    Recept modell a készletkezelési rendszerhez.

    Összekapcsolja a termékeket az alapanyagokkal és
    meghatározza, hogy egy termék elkészítéséhez milyen
    alapanyagokból mennyire van szükség.

    Példa: 1 db Hamburger = 0.200 kg marhahús + 0.050 kg saláta + 1 db zsemle
    """
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False, index=True)
    # CRITICAL FIX (C3.1): Add ondelete CASCADE for data integrity
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=False)
    quantity_used = Column(Numeric(10, 3), nullable=False)

    # Relationships
    inventory_item = relationship('InventoryItem', back_populates='recipes')

    def __repr__(self):
        return f"<Recipe(id={self.id}, product_id={self.product_id}, item_id={self.inventory_item_id}, qty={self.quantity_used})>"
