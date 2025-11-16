"""
ImageAsset Model - SQLAlchemy ORM
Module 0: Terméktörzs és Menü

Képek tárolása termékekhez, GCS URL-ekkel.
Tartalmazza az eredeti és az átméretezett képek URL-jeit.
"""

from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_menu.models.base import Base


class ImageAsset(Base):
    """
    Kép tárolási modell a termékekhez.

    Támogatja:
    - Google Cloud Storage URL tárolást
    - Átméretezett képek URL-jeit JSONB formátumban
    - Automatikus timestamp kezelést
    """
    __tablename__ = 'image_assets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    gcs_url_original = Column(Text, nullable=False)
    gcs_urls_resized = Column(JSONB, nullable=True)  # {'thumbnail': 'url', 'medium': 'url'}
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    product = relationship('Product', back_populates='images')

    def __repr__(self):
        return f"<ImageAsset(id={self.id}, product_id={self.product_id}, url='{self.gcs_url_original}')>"
