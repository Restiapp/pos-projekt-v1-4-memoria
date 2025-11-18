"""
Coupon Model - SQLAlchemy ORM
Module 5: Customer Relationship Management (CRM)

A coupons tábla kuponok és kedvezménykódok tárolására.
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from backend.service_crm.models.database import Base


class Coupon(Base):
    """
    Kupon modell a CRM rendszerhez.

    Támogatja:
    - Százalékos és fix összegű kedvezményeket
    - Személyre szabott kuponokat (customer-specific)
    - Általános kuponokat (public)
    - Érvényességi időszak kezelését
    - Használati limit meghatározását
    """
    __tablename__ = 'coupons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True, index=True)  # NULL = public coupon

    # Coupon Information
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)

    # Discount Type and Value
    discount_type = Column(String(20), nullable=False)  # 'PERCENTAGE', 'FIXED_AMOUNT'
    discount_value = Column(Numeric(10, 2), nullable=False)  # Percentage (0-100) or fixed HUF amount

    # Minimum Purchase Requirements
    min_purchase_amount = Column(Numeric(10, 2), nullable=True)  # Minimum order value to apply coupon

    # Usage Limits
    usage_limit = Column(Integer, nullable=True)  # Max number of times this coupon can be used (NULL = unlimited)
    usage_count = Column(Integer, nullable=False, default=0)  # Current usage count

    # Validity Period
    valid_from = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    valid_until = Column(TIMESTAMP(timezone=True), nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer = relationship('Customer', back_populates='coupons')

    def __repr__(self):
        return f"<Coupon(id={self.id}, code='{self.code}', type='{self.discount_type}', value={self.discount_value}, active={self.is_active})>"

    @property
    def is_valid(self):
        """Ellenőrzi, hogy a kupon jelenleg érvényes-e."""
        if not self.is_active:
            return False

        now = datetime.now()

        # Check valid_from
        if self.valid_from and self.valid_from > now:
            return False

        # Check valid_until
        if self.valid_until and self.valid_until < now:
            return False

        # Check usage limit
        if self.usage_limit is not None and self.usage_count >= self.usage_limit:
            return False

        return True

    @property
    def is_public(self):
        """Megadja, hogy a kupon publikus-e (nem ügyfél-specifikus)."""
        return self.customer_id is None
