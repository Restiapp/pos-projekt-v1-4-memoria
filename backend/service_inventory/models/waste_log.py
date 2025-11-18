"""
WasteLog Model - SQLAlchemy ORM
Module 5: Készletkezelés

A selejtezési napló táblája, amely rögzíti az elhasznált vagy megsemmisített
alapanyagok mennyiségét és okát.
"""

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_inventory.models.database import Base


class WasteLog(Base):
    """
    Selejtezési napló modell a készletkezelési rendszerhez.

    Támogatja:
    - Selejtezett/megsemmisített alapanyagok nyilvántartását
    - Selejtezés okának rögzítését (pl. 'lejárt', 'sérült', 'minőségi probléma')
    - Időbélyegzett audit trail vezetését
    - Kapcsolatot az inventory_items táblával

    A selejtezés automatikusan csökkenti a current_stock_perpetual értékét
    a perpetuális raktárkövetési rendszerben.
    """
    __tablename__ = 'waste_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)  # Selejtezett mennyiség
    reason = Column(String(100), nullable=False)  # 'lejárt', 'sérült', 'minőségi probléma', 'egyéb'
    waste_date = Column(Date, nullable=False)  # Selejtezés dátuma
    noted_by = Column(String(100), nullable=True)  # Ki rögzítette (pl. alkalmazott neve)
    notes = Column(String(500), nullable=True)  # További megjegyzések
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    inventory_item = relationship('InventoryItem', backref='waste_logs')

    def __repr__(self):
        return f"<WasteLog(id={self.id}, item_id={self.inventory_item_id}, quantity={self.quantity}, reason='{self.reason}', date={self.waste_date})>"
