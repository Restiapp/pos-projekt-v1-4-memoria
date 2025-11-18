"""
Gift Card Model - SQLAlchemy ORM
Module 5: Customer Relationship Management (CRM)

A gift_cards tábla ajándékkártyák kezelésére.
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from backend.service_crm.models.database import Base


class GiftCard(Base):
    """
    Ajándékkártya modell a CRM rendszerhez.

    Támogatja:
    - Egyedi ajándékkártya kódok generálását
    - Egyenleg kezelését (initial_balance, current_balance)
    - Felhasználási előzmények nyomon követését
    - Érvényességi időszak kezelését
    - Tulajdonos hozzárendelését (opcionális)
    """
    __tablename__ = 'gift_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True, index=True)  # NULL = not yet assigned

    # Gift Card Information
    card_code = Column(String(50), unique=True, nullable=False, index=True)
    pin_code = Column(String(10), nullable=True)  # Optional PIN for security

    # Balance
    initial_balance = Column(Numeric(10, 2), nullable=False)
    current_balance = Column(Numeric(10, 2), nullable=False)

    # Validity Period
    issued_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    valid_until = Column(TIMESTAMP(timezone=True), nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Purchase Information (who bought it, optional)
    purchased_by_customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    purchase_order_id = Column(Integer, nullable=True)  # Reference to order where it was purchased

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    customer = relationship('Customer', back_populates='gift_cards', foreign_keys=[customer_id])

    def __repr__(self):
        return f"<GiftCard(id={self.id}, code='{self.card_code}', balance={self.current_balance}, active={self.is_active})>"

    @property
    def is_valid(self):
        """Ellenőrzi, hogy az ajándékkártya jelenleg érvényes-e."""
        if not self.is_active:
            return False

        # Check if there's remaining balance
        if self.current_balance <= 0:
            return False

        # Check validity period
        if self.valid_until:
            now = datetime.now()
            if self.valid_until < now:
                return False

        return True

    @property
    def is_assigned(self):
        """Megadja, hogy az ajándékkártya hozzá van-e rendelve egy ügyfélhez."""
        return self.customer_id is not None

    @property
    def usage_percentage(self):
        """Felhasználtság százalékos aránya."""
        if self.initial_balance == 0:
            return 100.0
        used = self.initial_balance - self.current_balance
        return float((used / self.initial_balance) * 100)
