"""
LEGACY: Category Model - SQLAlchemy ORM
Module 0: Terméktörzs és Menü

LEGACY MODEL - DO NOT USE FOR NEW FEATURES
Use backend/service_menu/models/menu.py for Menu Model V1

A kategóriák hierarchikus struktúrát támogatnak (parent_id).
"""

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_menu.models.base import Base


class Category(Base):
    """
    Kategória modell a termékek osztályozásához.
    Támogatja a hierarchikus kategória-struktúrát.
    """
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    parent = relationship('Category', remote_side=[id], backref='subcategories')
    products = relationship('Product', back_populates='category')

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"
