"""
InventoryItem Model - SQLAlchemy ORM
Module 5: Készletkezelés

Az alapanyagok táblája, amely tartalmazza az automatikus (perpetuális)
raktár aktuális készletét és az utolsó beszerzési egységárat.
"""

from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from backend.service_inventory.models.database import Base


class InventoryItem(Base):
    """
    Alapanyag modell a készletkezelési rendszerhez.

    Támogatja:
    - Perpetuális (automatikus) raktárkövetést (current_stock_perpetual)
    - Különböző mértékegységeket (unit: 'kg', 'liter', 'db')
    - Utolsó beszerzési ár tárolását (last_cost_per_unit)
    """
    __tablename__ = 'inventory_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=False)  # 'kg', 'liter', 'db'
    current_stock_perpetual = Column(Numeric(10, 3), default=0.000)  # Automatikus raktár
    last_cost_per_unit = Column(Numeric(10, 2), nullable=True)

    # Relationships
    recipes = relationship('Recipe', back_populates='inventory_item', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<InventoryItem(id={self.id}, name='{self.name}', stock={self.current_stock_perpetual} {self.unit})>"
