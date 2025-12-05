"""
LEGACY: Product Model - SQLAlchemy ORM
Module 0: Terméktörzs és Menü

LEGACY MODEL - DO NOT USE FOR NEW FEATURES
Use backend/service_menu/models/menu.py for Menu Model V1

A termékek táblázata, amely tartalmazza az alap termék információkat,
AI fordítást (translations JSONB), és kapcsolatokat a kategóriákhoz és képekhez.
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_menu.models.base import Base


class Product(Base):
    """
    Termék modell a POS rendszerhez.

    Támogatja:
    - Kategorizálást (category_id)
    - Többnyelvűséget (translations JSONB)
    - SKU kezelést
    - Aktív/inaktív státusz kezelést
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    # CRITICAL FIX (C1.3): Add ondelete behavior for data integrity
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    sku = Column(String(100), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    translations = Column(JSONB, nullable=True)  # {'en': {'name': '..', 'desc': '..'}, 'de': {...}}
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship('Category', back_populates='products')
    images = relationship('ImageAsset', back_populates='product', cascade='all, delete-orphan')
    modifier_groups = relationship(
        'ModifierGroup',
        secondary='product_modifier_group_associations',
        back_populates='products'
    )
    allergens = relationship(
        'Allergen',
        secondary='product_allergen_associations',
        back_populates='products'
    )
    channel_visibilities = relationship('ChannelVisibility', back_populates='product', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}', price={self.base_price})>"
