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
    - Helyiséghez rendelést (room_id)
    - Vizuális pozícionálást (x, y, rotation)
    - Vizuális megjelenést (shape, width, height)
    - Kapacitás kezelést (capacity)
    - Asztal csoportosítást (parent_table_id)
    """
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_number = Column(String(50), unique=True, nullable=False)
    
    # Geometry & Visuals
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)
    x = Column(Integer, default=0, nullable=False)
    y = Column(Integer, default=0, nullable=False)
    width = Column(Integer, default=80, nullable=False)
    height = Column(Integer, default=80, nullable=False)
    rotation = Column(Integer, default=0, nullable=False)
    shape = Column(String(20), default='RECTANGLE', nullable=False)  # RECTANGLE, CIRCLE
    
    capacity = Column(Integer, nullable=True)
    parent_table_id = Column(Integer, ForeignKey('tables.id'), nullable=True)

    # Relationships
    room = relationship('Room', back_populates='tables')
    seats = relationship('Seat', back_populates='table', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='table')
    reservations = relationship('Reservation', back_populates='table')

    def __repr__(self):
        return f"<Table(id={self.id}, number='{self.table_number}', room={self.room_id})>"
