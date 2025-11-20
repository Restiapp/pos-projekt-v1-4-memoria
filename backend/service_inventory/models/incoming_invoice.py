"""
Incoming Invoice Models for Inventory Management
Handles procurement/purchasing workflow with DRAFT/FINALIZED status
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date, datetime
import enum

from .database import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice status enumeration"""
    DRAFT = "DRAFT"
    FINALIZED = "FINALIZED"


class IncomingInvoice(Base):
    """
    Incoming invoices from suppliers for procurement tracking

    Workflow:
    1. Create invoice in DRAFT status
    2. Add items to invoice
    3. Finalize invoice -> increases stock + creates stock movement log
    """
    __tablename__ = "incoming_invoices"

    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(255), nullable=False, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, default=date.today)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finalized_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    items = relationship("IncomingInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<IncomingInvoice(id={self.id}, invoice_number='{self.invoice_number}', status='{self.status}')>"


class IncomingInvoiceItem(Base):
    """
    Line items for incoming invoices
    Links to inventory items with quantity and unit price
    """
    __tablename__ = "incoming_invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("incoming_invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id", ondelete="RESTRICT"), nullable=False, index=True)

    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    # Computed field (not stored, calculated as quantity * unit_price)
    # total_price = quantity * unit_price

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    invoice = relationship("IncomingInvoice", back_populates="items")
    inventory_item = relationship("InventoryItem")

    def __repr__(self):
        return f"<IncomingInvoiceItem(id={self.id}, invoice_id={self.invoice_id}, quantity={self.quantity})>"

    @property
    def total_price(self) -> float:
        """Calculate total price for this line item"""
        return float(self.quantity * self.unit_price)
