"""
ChannelVisibility Model - SQLAlchemy ORM
Module 0: Terméktörzs és Menü

Értékesítési csatornák szerinti láthatóság és ár felülírás.
Például: 'Pult', 'Kiszállítás', 'Helybeni'.
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.service_menu.models.base import Base


class ChannelVisibility(Base):
    """
    Csatorna láthatósági modell.

    Támogatja:
    - Termékek láthatóságának kezelését csatornánként
    - Ár felülírást csatornánként
    - Egyedi korlátozást (channel_name, product_id) kombinációra
    """
    __tablename__ = 'channel_visibility'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_name = Column(String(100), nullable=False)  # 'Pult', 'Kiszállítás', 'Helybeni'
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    price_override = Column(Numeric(10, 2), nullable=True)
    is_visible = Column(Boolean, default=True)

    # Unique constraint on (channel_name, product_id)
    __table_args__ = (
        UniqueConstraint('channel_name', 'product_id', name='uq_channel_product'),
    )

    # Relationships
    product = relationship('Product', back_populates='channel_visibilities')

    def __repr__(self):
        return f"<ChannelVisibility(id={self.id}, channel='{self.channel_name}', product_id={self.product_id})>"
