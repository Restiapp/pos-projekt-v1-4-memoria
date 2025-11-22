"""
Stock Movement Service - Business logic for stock movement tracking
Provides centralized logging for all inventory stock changes
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from backend.service_inventory.models import StockMovement, InventoryItem, MovementReason
from backend.service_inventory.schemas.stock_movement import (
    StockMovementCreate,
    StockMovementResponse,
    StockMovementFilter
)


class StockMovementService:
    """Service for managing stock movement logs"""

    @staticmethod
    def create_movement(
        db: Session,
        inventory_item_id: int,
        change_amount: Decimal,
        reason: MovementReason,
        related_id: Optional[int] = None,
        notes: Optional[str] = None,
        employee_id: Optional[int] = None,
        commit: bool = True
    ) -> StockMovement:
        """
        Create a stock movement log entry

        Args:
            db: Database session
            inventory_item_id: ID of inventory item
            change_amount: Change in stock (positive=increase, negative=decrease)
            reason: Reason for movement (MovementReason enum)
            related_id: Optional related record ID (invoice_id, order_id, etc.)
            notes: Optional notes
            employee_id: Optional employee ID
            commit: Whether to commit the transaction (default True)

        Returns:
            Created StockMovement object

        Raises:
            ValueError: If inventory item not found or stock would go negative
        """
        # Get inventory item
        item = db.query(InventoryItem).filter(InventoryItem.id == inventory_item_id).first()
        if not item:
            raise ValueError(f"Inventory item with ID {inventory_item_id} not found")

        # Calculate new stock level
        current_stock = item.current_stock_perpetual or Decimal('0')
        new_stock = current_stock + change_amount

        # Validate stock doesn't go negative
        if new_stock < 0:
            raise ValueError(
                f"Insufficient stock for {item.name}. "
                f"Current: {current_stock} {item.unit}, "
                f"Requested change: {change_amount} {item.unit}"
            )

        # Create movement record
        movement = StockMovement(
            inventory_item_id=inventory_item_id,
            change_amount=change_amount,
            stock_after=new_stock,
            reason=reason,
            related_id=related_id,
            notes=notes,
            employee_id=employee_id
        )

        db.add(movement)

        # Update inventory item stock
        item.current_stock_perpetual = new_stock

        if commit:
            db.commit()
            db.refresh(movement)
            db.refresh(item)

        return movement

    @staticmethod
    def get_movement(db: Session, movement_id: int) -> Optional[StockMovement]:
        """Get a stock movement by ID"""
        return db.query(StockMovement).filter(StockMovement.id == movement_id).first()

    @staticmethod
    def list_movements(
        db: Session,
        inventory_item_id: Optional[int] = None,
        reason: Optional[MovementReason] = None,
        employee_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[StockMovement], int]:
        """
        List stock movements with filters and pagination

        Returns:
            Tuple of (movements_list, total_count)
        """
        query = db.query(StockMovement)

        # Apply filters
        if inventory_item_id:
            query = query.filter(StockMovement.inventory_item_id == inventory_item_id)
        if reason:
            query = query.filter(StockMovement.reason == reason)
        if employee_id:
            query = query.filter(StockMovement.employee_id == employee_id)
        if date_from:
            query = query.filter(StockMovement.created_at >= date_from)
        if date_to:
            query = query.filter(StockMovement.created_at <= date_to)

        # Get total count
        total = query.count()

        # Apply pagination and ordering (newest first)
        movements = query.order_by(desc(StockMovement.created_at)).offset(skip).limit(limit).all()

        return movements, total

    @staticmethod
    def get_item_movement_history(
        db: Session,
        inventory_item_id: int,
        limit: int = 50
    ) -> List[StockMovement]:
        """
        Get recent movement history for a specific inventory item

        Args:
            db: Database session
            inventory_item_id: ID of inventory item
            limit: Maximum number of records to return

        Returns:
            List of stock movements (newest first)
        """
        return (
            db.query(StockMovement)
            .filter(StockMovement.inventory_item_id == inventory_item_id)
            .order_by(desc(StockMovement.created_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_movements_by_reason(
        db: Session,
        reason: MovementReason,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[StockMovement], int]:
        """
        Get movements filtered by reason

        Returns:
            Tuple of (movements_list, total_count)
        """
        query = db.query(StockMovement).filter(StockMovement.reason == reason)
        total = query.count()
        movements = query.order_by(desc(StockMovement.created_at)).offset(skip).limit(limit).all()
        return movements, total

    @staticmethod
    def calculate_total_movement_by_reason(
        db: Session,
        inventory_item_id: int,
        reason: MovementReason,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Decimal:
        """
        Calculate total movement amount for an item by reason within a date range

        Useful for reports like:
        - Total waste in a period
        - Total intake in a period
        - Total sales in a period
        """
        from sqlalchemy import func

        query = db.query(func.sum(StockMovement.change_amount)).filter(
            StockMovement.inventory_item_id == inventory_item_id,
            StockMovement.reason == reason
        )

        if date_from:
            query = query.filter(StockMovement.created_at >= date_from)
        if date_to:
            query = query.filter(StockMovement.created_at <= date_to)

        result = query.scalar()
        return result or Decimal('0')
