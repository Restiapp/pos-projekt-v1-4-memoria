"""
Table Model - SQLAlchemy ORM
Module 1: Rendeléskezelés és Asztalok

Az asztalok táblája, amely tartalmazza az asztalok azonosítóját,
pozícióját és kapacitását.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from backend.service_orders.models.database import Base


class Table(Base):
    """
    Asztal modell a POS rendszerhez.
    Updated for Professional Floor Plan (Konva).
    """
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_number = Column(String(50), unique=True, nullable=False)

    # Geometry & Layout
    position_x = Column(Integer, nullable=True, default=0)
    position_y = Column(Integer, nullable=True, default=0)
    width = Column(Integer, nullable=True, default=80)
    height = Column(Integer, nullable=True, default=80)
    rotation = Column(Float, default=0.0)
    shape = Column(String(20), default='rect') # 'rect', 'round'

    capacity = Column(Integer, nullable=True, default=4)

    # Relationships
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)
    room = relationship('Room', back_populates='tables')

    seats = relationship('Seat', back_populates='table', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='table')

    # Extra visual config (colors, chair positions override)
    metadata_json = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<Table(id={self.id}, table_number='{self.table_number}', capacity={self.capacity})>"
