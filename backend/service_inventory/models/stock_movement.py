"""
Stock Movement Model for Inventory Audit Trail
Logs all stock changes for complete traceability
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .database import Base


class MovementReason(str, enum.Enum):
    """Reasons for stock movements"""
    INTAKE = "INTAKE"           # Incoming invoice finalized (stock increase)
    SALE = "SALE"              # Product sold (stock decrease)
    WASTE = "WASTE"            # Waste/spoilage (stock decrease)
    CORRECTION = "CORRECTION"  # Manual adjustment (increase or decrease)
    INITIAL = "INITIAL"        # Initial stock setup


class StockMovement(Base):
    """
    Complete audit trail for all inventory stock changes

    Every change to inventory_item.current_stock_perpetual must create
    a corresponding StockMovement record for traceability
    """
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(
        Integer,
        ForeignKey("inventory_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Positive for increase, negative for decrease
    change_amount = Column(Numeric(10, 3), nullable=False)

    # Stock level after this movement
    stock_after = Column(Numeric(10, 3), nullable=False)

    # Reason for the movement
    reason = Column(SQLEnum(MovementReason), nullable=False, index=True)

    # Related record ID (optional, for linking to source)
    # - For INTAKE: incoming_invoice_id
    # - For SALE: order_id (from orders service)
    # - For WASTE: waste_log_id
    # - For CORRECTION: null or adjustment_id
    related_id = Column(Integer, nullable=True, index=True)

    # Optional notes/description
    notes = Column(Text, nullable=True)

    # User/employee who triggered this movement (optional)
    employee_id = Column(Integer, nullable=True, index=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    inventory_item = relationship("InventoryItem")

    def __repr__(self):
        return (
            f"<StockMovement(id={self.id}, item_id={self.inventory_item_id}, "
            f"change={self.change_amount}, reason='{self.reason}')>"
        )

    @property
    def movement_type(self) -> str:
        """Human-readable movement type"""
        return "Increase" if self.change_amount > 0 else "Decrease"
