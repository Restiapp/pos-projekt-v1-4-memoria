"""
Waste Service - Business logic for waste/spoilage management
Handles recording waste with stock reduction and movement logging
"""
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import date

from backend.service_inventory.models import WasteLog, InventoryItem, MovementReason
from backend.service_inventory.schemas.waste import WasteCreateRequest
from backend.service_inventory.services.stock_movement_service import StockMovementService


class WasteService:
    """Service for managing waste/spoilage"""

    @staticmethod
    def record_waste(
        db: Session,
        waste_data: WasteCreateRequest
    ) -> tuple[WasteLog, int]:
        """
        Record waste - reduces stock and creates movement log

        Args:
            db: Database session
            waste_data: Waste recording data

        Returns:
            Tuple of (waste_log, stock_movement_id)

        Raises:
            ValueError: If inventory item not found or insufficient stock
        """
        # Validate inventory item exists
        inv_item = db.query(InventoryItem).filter(
            InventoryItem.id == waste_data.inventory_item_id
        ).first()
        if not inv_item:
            raise ValueError(f"Inventory item with ID {waste_data.inventory_item_id} not found")

        # Check sufficient stock
        current_stock = inv_item.current_stock_perpetual or Decimal('0')
        if current_stock < waste_data.quantity:
            raise ValueError(
                f"Insufficient stock for {inv_item.name}. "
                f"Current: {current_stock} {inv_item.unit}, "
                f"Requested waste: {waste_data.quantity} {inv_item.unit}"
            )

        # Create waste log
        waste_log = WasteLog(
            inventory_item_id=waste_data.inventory_item_id,
            quantity=waste_data.quantity,
            reason=waste_data.reason,
            waste_date=waste_data.waste_date,
            noted_by=waste_data.noted_by,
            notes=waste_data.notes
        )

        db.add(waste_log)
        db.flush()  # Get waste_log ID

        # Create stock movement (negative = decrease)
        movement_notes = f"Waste: {waste_data.reason}"
        if waste_data.notes:
            movement_notes += f" - {waste_data.notes}"

        movement = StockMovementService.create_movement(
            db=db,
            inventory_item_id=waste_data.inventory_item_id,
            change_amount=-waste_data.quantity,  # Negative = decrease
            reason=MovementReason.WASTE,
            related_id=waste_log.id,
            notes=movement_notes,
            employee_id=waste_data.employee_id,
            commit=False  # We'll commit at the end
        )

        db.commit()
        db.refresh(waste_log)

        return waste_log, movement.id

    @staticmethod
    def get_waste_log(db: Session, waste_id: int) -> Optional[WasteLog]:
        """Get a waste log by ID"""
        return db.query(WasteLog).filter(WasteLog.id == waste_id).first()

    @staticmethod
    def list_waste_logs(
        db: Session,
        inventory_item_id: Optional[int] = None,
        waste_date_from: Optional[date] = None,
        waste_date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[WasteLog], int]:
        """
        List waste logs with filters and pagination

        Returns:
            Tuple of (waste_logs_list, total_count)
        """
        from sqlalchemy import desc

        query = db.query(WasteLog)

        # Apply filters
        if inventory_item_id:
            query = query.filter(WasteLog.inventory_item_id == inventory_item_id)
        if waste_date_from:
            query = query.filter(WasteLog.waste_date >= waste_date_from)
        if waste_date_to:
            query = query.filter(WasteLog.waste_date <= waste_date_to)

        # Get total count
        total = query.count()

        # Apply pagination and ordering (newest first)
        waste_logs = query.order_by(desc(WasteLog.created_at)).offset(skip).limit(limit).all()

        return waste_logs, total
