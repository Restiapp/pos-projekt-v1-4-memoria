"""
Room Model - SQLAlchemy ORM
Module 1: Floor Plan Management

Helyiségek (pl. Terasz, Nagyterem) definíciója.
"""

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from backend.service_orders.models.database import Base

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), default='indoor') # indoor, outdoor
    width = Column(Integer, default=800) # Canvas width
    height = Column(Integer, default=600) # Canvas height
    background_image_url = Column(String(255), nullable=True)

    # Relationships
    tables = relationship('Table', back_populates='room', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}')>"
