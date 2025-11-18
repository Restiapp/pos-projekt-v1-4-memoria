"""
Address Model - SQLAlchemy ORM
Module 5: Customer Relationship Management (CRM)

Az addresses tábla az ügyfelek szállítási és számlázási címeinek tárolására.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_crm.models.database import Base


class Address(Base):
    """
    Cím modell a CRM rendszerhez.

    Támogatja:
    - Több cím tárolását ügyfelenként
    - Számlázási és szállítási címek megkülönböztetését
    - Alapértelmezett cím beállítását
    - Magyar címformátum (irányítószám, város, utca, házszám)
    """
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, index=True)

    # Address Type
    address_type = Column(String(20), nullable=False, default='SHIPPING')  # 'SHIPPING', 'BILLING', 'BOTH'
    is_default = Column(Boolean, nullable=False, default=False)

    # Hungarian Address Format
    country = Column(String(100), nullable=False, default='Magyarország')
    postal_code = Column(String(10), nullable=False)
    city = Column(String(100), nullable=False)
    street_address = Column(String(255), nullable=False)
    street_number = Column(String(20), nullable=False)
    building = Column(String(50), nullable=True)  # Épület (pl. "A épület")
    floor = Column(String(10), nullable=True)  # Emelet
    door = Column(String(10), nullable=True)  # Ajtó

    # Optional Additional Information
    company_name = Column(String(255), nullable=True)
    notes = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer = relationship('Customer', back_populates='addresses')

    def __repr__(self):
        return f"<Address(id={self.id}, customer_id={self.customer_id}, type='{self.address_type}', city='{self.city}')>"

    @property
    def full_address(self):
        """Teljes formázott cím property."""
        parts = [
            f"{self.postal_code} {self.city}",
            f"{self.street_address} {self.street_number}"
        ]
        if self.building:
            parts.append(f"{self.building}")
        if self.floor:
            parts.append(f"{self.floor}. emelet")
        if self.door:
            parts.append(f"{self.door}. ajtó")
        return ", ".join(parts)
