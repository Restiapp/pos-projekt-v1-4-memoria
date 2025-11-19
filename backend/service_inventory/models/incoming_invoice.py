"""
IncomingInvoice Model - SQLAlchemy ORM
Module 5: Készletkezelés - NAV OSA Integration

A NAV Online Számla rendszeréből lekérdezett bejövő számlák táblája.
Ez a tábla tárolja az összes beszállítói számlát, amelyet a NAV OSA
API-ból letöltöttünk.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from backend.service_inventory.models.database import Base


class IncomingInvoice(Base):
    """
    Bejövő számla modell a NAV OSA integrációhoz.

    Támogatja:
    - NAV OSA API-ból lekérdezett számlák tárolását
    - Számla státusz követést (status: 'NEW', 'REVIEWED', 'SETTLED')
    - Beszállító információk tárolását
    - Teljes NAV API válasz tárolását JSONB formátumban

    A nav_data mező a NAV OSA API által visszaadott teljes
    strukturált JSON adatokat tartalmazza.
    """
    __tablename__ = 'incoming_invoices'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # NAV OSA specific fields
    invoice_number = Column(String(100), nullable=False, unique=True, index=True)
    supplier_tax_number = Column(String(50), nullable=True)
    supplier_name = Column(String(255), nullable=True)

    # Invoice details
    invoice_date = Column(Date, nullable=True)
    total_amount = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), nullable=False, default='HUF')

    # NAV integration data
    nav_data = Column(JSONB, nullable=True)  # Full NAV OSA API response

    # Status tracking
    status = Column(
        String(50),
        nullable=False,
        default='NEW',
        index=True
    )  # 'NEW', 'REVIEWED', 'SETTLED'

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return (
            f"<IncomingInvoice(id={self.id}, "
            f"invoice_number='{self.invoice_number}', "
            f"supplier='{self.supplier_name}', "
            f"date={self.invoice_date}, "
            f"status='{self.status}')>"
        )
