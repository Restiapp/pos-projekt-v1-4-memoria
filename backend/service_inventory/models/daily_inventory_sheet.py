"""
DailyInventorySheet and DailyInventoryCount Models - SQLAlchemy ORM
Module 5: Készletkezelés

A napi leltárívek és leltárszámlálások táblái.
Támogatja a kettős raktárkezelési modell manuális (karton) részét.
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_inventory.models.database import Base


# Association table a DailyInventorySheet és InventoryItem között
daily_inventory_sheet_items = Table(
    'daily_inventory_sheet_items',
    Base.metadata,
    Column('sheet_id', Integer, ForeignKey('daily_inventory_sheets.id'), primary_key=True),
    Column('inventory_item_id', Integer, ForeignKey('inventory_items.id'), primary_key=True)
)


class DailyInventorySheet(Base):
    """
    Napi leltárív modell a készletkezelési rendszerhez.

    Ez a modell definiálja a 'napi karton' sablonját,
    amely meghatározza, hogy mely alapanyagokat kell naponta leltározni.

    Példa: "Reggeli Leltárív" tartalmazza: tojás, tej, kenyér, stb.
    """
    __tablename__ = 'daily_inventory_sheets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    inventory_items = relationship(
        'InventoryItem',
        secondary=daily_inventory_sheet_items,
        backref='daily_sheets'
    )
    daily_counts = relationship('DailyInventoryCount', back_populates='sheet', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<DailyInventorySheet(id={self.id}, name='{self.name}')>"


class DailyInventoryCount(Base):
    """
    Napi leltárszámlálás modell a készletkezelési rendszerhez.

    Ez a modell tárolja a tényleges napi leltárokat,
    ahol a felhasználó rögzíti a fizikai darabszámot/mennyiséget.

    A counts JSONB mező formátuma: {'item_id_1': 10.5, 'item_id_2': 100}
    """
    __tablename__ = 'daily_inventory_counts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sheet_id = Column(Integer, ForeignKey('daily_inventory_sheets.id'), nullable=False)
    count_date = Column(Date, nullable=False)
    employee_id = Column(Integer, nullable=True)  # REFERENCES employees(id) - később
    counts = Column(JSONB, nullable=True)  # {'item_id_1': 10.5, 'item_id_2': 100}
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    sheet = relationship('DailyInventorySheet', back_populates='daily_counts')

    def __repr__(self):
        return f"<DailyInventoryCount(id={self.id}, sheet_id={self.sheet_id}, date={self.count_date})>"
