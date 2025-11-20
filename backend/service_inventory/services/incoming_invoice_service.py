"""
Incoming Invoice Service - Business logic for procurement/purchasing
Handles invoice creation, item management, and finalization with stock updates
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from backend.service_inventory.models import (
    IncomingInvoice,
    IncomingInvoiceItem,
    InvoiceStatus,
    InventoryItem,
    MovementReason
)
from backend.service_inventory.schemas.incoming_invoice import (
    IncomingInvoiceCreate,
    IncomingInvoiceUpdate,
    IncomingInvoiceItemCreate
)
from backend.service_inventory.services.stock_movement_service import StockMovementService


class IncomingInvoiceService:
    """Service for managing incoming invoices from suppliers"""

    @staticmethod
    def create_invoice(
        db: Session,
        invoice_data: IncomingInvoiceCreate
    ) -> IncomingInvoice:
        """
        Create a new incoming invoice in DRAFT status

        Args:
            db: Database session
            invoice_data: Invoice creation data

        Returns:
            Created IncomingInvoice object

        Raises:
            ValueError: If invoice_number already exists or validation fails
        """
        # Check if invoice_number already exists
        existing = db.query(IncomingInvoice).filter(
            IncomingInvoice.invoice_number == invoice_data.invoice_number
        ).first()

        if existing:
            raise ValueError(f"Invoice number '{invoice_data.invoice_number}' already exists")

        # Calculate total from items if not provided
        total_amount = invoice_data.total_amount or Decimal('0')
        if invoice_data.items:
            calculated_total = sum(
                item.quantity * item.unit_price
                for item in invoice_data.items
            )
            total_amount = calculated_total

        # Create invoice
        invoice = IncomingInvoice(
            supplier_name=invoice_data.supplier_name,
            invoice_number=invoice_data.invoice_number,
            invoice_date=invoice_data.invoice_date,
            total_amount=total_amount,
            status=InvoiceStatus.DRAFT
        )

        db.add(invoice)
        db.flush()  # Get invoice ID

        # Add items if provided
        if invoice_data.items:
            for item_data in invoice_data.items:
                # Validate inventory item exists
                inv_item = db.query(InventoryItem).filter(
                    InventoryItem.id == item_data.inventory_item_id
                ).first()
                if not inv_item:
                    raise ValueError(f"Inventory item with ID {item_data.inventory_item_id} not found")

                item = IncomingInvoiceItem(
                    invoice_id=invoice.id,
                    inventory_item_id=item_data.inventory_item_id,
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price
                )
                db.add(item)

        db.commit()
        db.refresh(invoice)

        return invoice

    @staticmethod
    def get_invoice(db: Session, invoice_id: int) -> Optional[IncomingInvoice]:
        """Get an invoice by ID with items"""
        return db.query(IncomingInvoice).filter(IncomingInvoice.id == invoice_id).first()

    @staticmethod
    def get_invoice_by_number(db: Session, invoice_number: str) -> Optional[IncomingInvoice]:
        """Get an invoice by invoice number"""
        return db.query(IncomingInvoice).filter(
            IncomingInvoice.invoice_number == invoice_number
        ).first()

    @staticmethod
    def list_invoices(
        db: Session,
        status: Optional[InvoiceStatus] = None,
        supplier_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[IncomingInvoice], int]:
        """
        List invoices with filters and pagination

        Returns:
            Tuple of (invoices_list, total_count)
        """
        query = db.query(IncomingInvoice)

        # Apply filters
        if status:
            query = query.filter(IncomingInvoice.status == status)
        if supplier_name:
            query = query.filter(IncomingInvoice.supplier_name.ilike(f"%{supplier_name}%"))

        # Get total count
        total = query.count()

        # Apply pagination and ordering (newest first)
        invoices = query.order_by(desc(IncomingInvoice.created_at)).offset(skip).limit(limit).all()

        return invoices, total

    @staticmethod
    def update_invoice(
        db: Session,
        invoice_id: int,
        update_data: IncomingInvoiceUpdate
    ) -> IncomingInvoice:
        """
        Update an invoice (only allowed in DRAFT status)

        Raises:
            ValueError: If invoice not found or already finalized
        """
        invoice = db.query(IncomingInvoice).filter(IncomingInvoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found")

        if invoice.status == InvoiceStatus.FINALIZED:
            raise ValueError("Cannot update finalized invoice")

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)

        # Check invoice_number uniqueness if being updated
        if "invoice_number" in update_dict:
            existing = db.query(IncomingInvoice).filter(
                IncomingInvoice.invoice_number == update_dict["invoice_number"],
                IncomingInvoice.id != invoice_id
            ).first()
            if existing:
                raise ValueError(f"Invoice number '{update_dict['invoice_number']}' already exists")

        for field, value in update_dict.items():
            setattr(invoice, field, value)

        db.commit()
        db.refresh(invoice)

        return invoice

    @staticmethod
    def delete_invoice(db: Session, invoice_id: int) -> bool:
        """
        Delete an invoice (only allowed in DRAFT status)

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If invoice is finalized
        """
        invoice = db.query(IncomingInvoice).filter(IncomingInvoice.id == invoice_id).first()
        if not invoice:
            return False

        if invoice.status == InvoiceStatus.FINALIZED:
            raise ValueError("Cannot delete finalized invoice")

        db.delete(invoice)
        db.commit()

        return True

    @staticmethod
    def add_items(
        db: Session,
        invoice_id: int,
        items: List[IncomingInvoiceItemCreate]
    ) -> IncomingInvoice:
        """
        Add items to an invoice (only in DRAFT status)

        Raises:
            ValueError: If invoice not found, finalized, or items invalid
        """
        invoice = db.query(IncomingInvoice).filter(IncomingInvoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found")

        if invoice.status == InvoiceStatus.FINALIZED:
            raise ValueError("Cannot add items to finalized invoice")

        # Add items
        for item_data in items:
            # Validate inventory item exists
            inv_item = db.query(InventoryItem).filter(
                InventoryItem.id == item_data.inventory_item_id
            ).first()
            if not inv_item:
                raise ValueError(f"Inventory item with ID {item_data.inventory_item_id} not found")

            item = IncomingInvoiceItem(
                invoice_id=invoice.id,
                inventory_item_id=item_data.inventory_item_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price
            )
            db.add(item)

        # Recalculate total
        db.flush()
        db.refresh(invoice)
        total = sum(item.total_price for item in invoice.items)
        invoice.total_amount = Decimal(str(total))

        db.commit()
        db.refresh(invoice)

        return invoice

    @staticmethod
    def finalize_invoice(
        db: Session,
        invoice_id: int,
        employee_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> tuple[IncomingInvoice, int]:
        """
        Finalize an invoice - updates stock and creates movement logs

        Args:
            db: Database session
            invoice_id: Invoice ID to finalize
            employee_id: Optional employee ID
            notes: Optional notes

        Returns:
            Tuple of (finalized_invoice, stock_movements_created_count)

        Raises:
            ValueError: If invoice not found, already finalized, or has no items
        """
        invoice = db.query(IncomingInvoice).filter(IncomingInvoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found")

        if invoice.status == InvoiceStatus.FINALIZED:
            raise ValueError("Invoice is already finalized")

        if not invoice.items:
            raise ValueError("Cannot finalize invoice with no items")

        # Create stock movements for each item
        movements_created = 0
        for item in invoice.items:
            # Update inventory item cost
            inv_item = db.query(InventoryItem).filter(
                InventoryItem.id == item.inventory_item_id
            ).first()
            if inv_item:
                inv_item.last_cost_per_unit = item.unit_price

            # Create stock movement (increases stock)
            movement_notes = notes or f"Incoming invoice: {invoice.invoice_number}"
            StockMovementService.create_movement(
                db=db,
                inventory_item_id=item.inventory_item_id,
                change_amount=item.quantity,  # Positive = increase
                reason=MovementReason.INTAKE,
                related_id=invoice.id,
                notes=movement_notes,
                employee_id=employee_id,
                commit=False  # We'll commit at the end
            )
            movements_created += 1

        # Mark invoice as finalized
        invoice.status = InvoiceStatus.FINALIZED
        invoice.finalized_at = datetime.utcnow()

        db.commit()
        db.refresh(invoice)

        return invoice, movements_created
