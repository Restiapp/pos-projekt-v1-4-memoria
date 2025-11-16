"""
SupplierInvoice Model - SQLAlchemy ORM
Module 5: Készletkezelés

A beszállítói számlák táblája, amely tartalmazza az OCR (Document AI)
által beolvasott számla adatokat JSONB formátumban.
"""

from sqlalchemy import Column, Integer, String, Numeric, Date
from sqlalchemy.dialects.postgresql import JSONB

from backend.service_inventory.models.database import Base


class SupplierInvoice(Base):
    """
    Beszállítói számla modell a készletkezelési rendszerhez.

    Támogatja:
    - AI alapú számla beolvasást (OCR) - ocr_data JSONB mező
    - Számla státusz követést (status: 'FELDOLGOZÁSRA VÁR', 'JÓVÁHAGYVA', 'BEVÉTELEZVE')
    - Beszállító információk tárolását

    Az ocr_data mező a Google Document AI Invoice Parser által
    visszaadott strukturált JSON adatokat tartalmazza.
    """
    __tablename__ = 'supplier_invoices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_name = Column(String(255), nullable=True)
    invoice_date = Column(Date, nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=True)
    ocr_data = Column(JSONB, nullable=True)  # Google Document AI eredménye
    status = Column(String(50), nullable=False, default='FELDOLGOZÁSRA VÁR')  # 'FELDOLGOZÁSRA VÁR', 'JÓVÁHAGYVA', 'BEVÉTELEZVE'

    def __repr__(self):
        return f"<SupplierInvoice(id={self.id}, supplier='{self.supplier_name}', date={self.invoice_date}, status='{self.status}')>"
