"""
Customer Model - SQLAlchemy ORM
Module 5: Customer Relationship Management (CRM)

A customers tábla ügyféladatok tárolására.
Tartalmazza a személyes adatokat, kapcsolattartási információkat,
és a törzsvásárlói pontokat.
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_crm.models.database import Base


class Customer(Base):
    """
    Ügyfél modell a CRM rendszerhez.

    Támogatja:
    - Személyes adatok kezelését (név, email, telefon)
    - Törzsvásárlói pontrendszert (loyalty_points)
    - Opt-in/opt-out marketing kommunikációra
    - GDPR-kompatibilis adatkezelést (notes)
    """
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_uid = Column(String(50), unique=True, nullable=False, index=True)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True, index=True)

    # Loyalty Program
    loyalty_points = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_spent = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_orders = Column(Integer, nullable=False, default=0)

    # Marketing Preferences
    marketing_consent = Column(Boolean, nullable=False, default=False)
    sms_consent = Column(Boolean, nullable=False, default=False)

    # Additional Information
    birth_date = Column(TIMESTAMP(timezone=False), nullable=True)
    notes = Column(Text, nullable=True)

    # Account Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    addresses = relationship('Address', back_populates='customer', cascade='all, delete-orphan')
    coupons = relationship('Coupon', back_populates='customer', cascade='all, delete-orphan')
    gift_cards = relationship('GiftCard', back_populates='customer', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.email}', loyalty_points={self.loyalty_points})>"

    @property
    def full_name(self):
        """Teljes név property."""
        return f"{self.first_name} {self.last_name}"
