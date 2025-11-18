"""
Table Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

Az asztalok táblája, amely tartalmazza az asztalok azonosítóját,
pozícióját és kapacitását.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from backend.service_orders.models.database import Base


class Table(Base):
    """
    Asztal modell a POS rendszerhez.

    Támogatja:
    - Egyedi asztal azonosítást (table_number)
    - Vizuális pozícionálást (position_x, position_y)
    - Kapacitás kezelést (capacity)
    - Szekciók (section) - V3.0
    - Asztal csoportosítást (parent_table_id) - V3.0
    """
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_number = Column(String(50), unique=True, nullable=False)
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    capacity = Column(Integer, nullable=True)
    section = Column(String(100), nullable=True)  # V3.0: Szekció (pl. 'Terasz', 'Belső terem')
    parent_table_id = Column(Integer, ForeignKey('tables.id'), nullable=True)  # V3.0: Asztal összekapcsolás

    # Relationships
    seats = relationship('Seat', back_populates='table', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='table')

    def __repr__(self):
        return f"<Table(id={self.id}, table_number='{self.table_number}', capacity={self.capacity})>"
