"""
Stock Movement API Endpoints
Provides audit trail and reporting for all stock changes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from backend.service_inventory.models.database import get_db
from backend.service_inventory.models import MovementReason, InventoryItem
from backend.service_inventory.services.stock_movement_service import StockMovementService
from backend.service_inventory.schemas.stock_movement import (
    StockMovementResponse,
    StockMovementListResponse,
    StockCorrectionRequest,
    StockCorrectionResponse
)

# Import RBAC dependency (assuming it exists)
try:
    from backend.shared.rbac_middleware import require_permission
except ImportError:
    # Fallback if RBAC not available (for testing)
    def require_permission(permission: str):
        def dependency():
            return True
        return dependency


router = APIRouter(
    prefix="/api/v1/inventory/stock-movements",
    tags=["Stock Movements"]
)


@router.get(
    "",
    response_model=StockMovementListResponse,
    dependencies=[Depends(require_permission("inventory:view"))]
)
def list_stock_movements(
    inventory_item_id: Optional[int] = None,
    reason: Optional[str] = None,
    employee_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    """
    List stock movements with pagination and filters

    - **inventory_item_id**: Filter by inventory item ID
    - **reason**: Filter by reason (INTAKE, SALE, WASTE, CORRECTION, INITIAL)
    - **employee_id**: Filter by employee ID
    - **date_from**: Filter by date (from)
    - **date_to**: Filter by date (to)
    - **page**: Page number (starts at 1)
    - **page_size**: Items per page
    """
    # Validate page parameters
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

    # Convert reason filter
    reason_enum = None
    if reason:
        try:
            reason_enum = MovementReason[reason.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid reason: {reason}")

    skip = (page - 1) * page_size

    try:
        movements, total = StockMovementService.list_movements(
            db=db,
            inventory_item_id=inventory_item_id,
            reason=reason_enum,
            employee_id=employee_id,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=page_size
        )

        # Enrich with inventory item details
        responses = []
        for movement in movements:
            inv_item = db.query(InventoryItem).filter(
                InventoryItem.id == movement.inventory_item_id
            ).first()

            response_data = {
                "id": movement.id,
                "inventory_item_id": movement.inventory_item_id,
                "change_amount": movement.change_amount,
                "stock_after": movement.stock_after,
                "reason": movement.reason.value,
                "related_id": movement.related_id,
                "notes": movement.notes,
                "employee_id": movement.employee_id,
                "movement_type": movement.movement_type,
                "created_at": movement.created_at,
                "inventory_item_name": inv_item.name if inv_item else None,
                "inventory_item_unit": inv_item.unit if inv_item else None
            }
            responses.append(StockMovementResponse(**response_data))

        return StockMovementListResponse(
            movements=responses,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{movement_id}",
    response_model=StockMovementResponse,
    dependencies=[Depends(require_permission("inventory:view"))]
)
def get_stock_movement(
    movement_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific stock movement by ID"""
    movement = StockMovementService.get_movement(db, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail=f"Stock movement with ID {movement_id} not found")

    # Get inventory item details
    inv_item = db.query(InventoryItem).filter(
        InventoryItem.id == movement.inventory_item_id
    ).first()

    response_data = {
        "id": movement.id,
        "inventory_item_id": movement.inventory_item_id,
        "change_amount": movement.change_amount,
        "stock_after": movement.stock_after,
        "reason": movement.reason.value,
        "related_id": movement.related_id,
        "notes": movement.notes,
        "employee_id": movement.employee_id,
        "movement_type": movement.movement_type,
        "created_at": movement.created_at,
        "inventory_item_name": inv_item.name if inv_item else None,
        "inventory_item_unit": inv_item.unit if inv_item else None
    }

    return StockMovementResponse(**response_data)


@router.get(
    "/item/{inventory_item_id}/history",
    response_model=StockMovementListResponse,
    dependencies=[Depends(require_permission("inventory:view"))]
)
def get_item_movement_history(
    inventory_item_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get movement history for a specific inventory item

    Returns recent movements (newest first)
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

    try:
        movements = StockMovementService.get_item_movement_history(
            db=db,
            inventory_item_id=inventory_item_id,
            limit=limit
        )

        # Get inventory item details
        inv_item = db.query(InventoryItem).filter(
            InventoryItem.id == inventory_item_id
        ).first()

        if not inv_item:
            raise HTTPException(status_code=404, detail=f"Inventory item with ID {inventory_item_id} not found")

        # Build responses
        responses = []
        for movement in movements:
            response_data = {
                "id": movement.id,
                "inventory_item_id": movement.inventory_item_id,
                "change_amount": movement.change_amount,
                "stock_after": movement.stock_after,
                "reason": movement.reason.value,
                "related_id": movement.related_id,
                "notes": movement.notes,
                "employee_id": movement.employee_id,
                "movement_type": movement.movement_type,
                "created_at": movement.created_at,
                "inventory_item_name": inv_item.name,
                "inventory_item_unit": inv_item.unit
            }
            responses.append(StockMovementResponse(**response_data))

        return StockMovementListResponse(
            movements=responses,
            total=len(responses),
            page=1,
            page_size=limit
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/correction",
    response_model=StockCorrectionResponse,
    dependencies=[Depends(require_permission("inventory:manage"))]
)
def create_stock_correction(
    correction: StockCorrectionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a manual stock correction

    Use this endpoint for manual stock adjustments (e.g., physical count discrepancies)

    - **inventory_item_id**: ID of the inventory item
    - **change_amount**: Change in stock (positive=increase, negative=decrease)
    - **notes**: Reason for correction (required)
    - **employee_id**: Employee making correction (optional)
    """
    try:
        # Get current stock
        inv_item = db.query(InventoryItem).filter(
            InventoryItem.id == correction.inventory_item_id
        ).first()
        if not inv_item:
            raise HTTPException(
                status_code=404,
                detail=f"Inventory item with ID {correction.inventory_item_id} not found"
            )

        old_stock = inv_item.current_stock_perpetual or 0

        # Create stock movement
        movement = StockMovementService.create_movement(
            db=db,
            inventory_item_id=correction.inventory_item_id,
            change_amount=correction.change_amount,
            reason=MovementReason.CORRECTION,
            notes=correction.notes,
            employee_id=correction.employee_id,
            commit=True
        )

        # Refresh to get new stock
        db.refresh(inv_item)

        # Build movement response
        movement_response = StockMovementResponse(
            id=movement.id,
            inventory_item_id=movement.inventory_item_id,
            change_amount=movement.change_amount,
            stock_after=movement.stock_after,
            reason=movement.reason.value,
            related_id=movement.related_id,
            notes=movement.notes,
            employee_id=movement.employee_id,
            movement_type=movement.movement_type,
            created_at=movement.created_at,
            inventory_item_name=inv_item.name,
            inventory_item_unit=inv_item.unit
        )

        return StockCorrectionResponse(
            movement=movement_response,
            old_stock=old_stock,
            new_stock=inv_item.current_stock_perpetual,
            message=f"Stock corrected successfully. Changed from {old_stock} to {inv_item.current_stock_perpetual} {inv_item.unit}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
