"""
Waste Management API Endpoints
Handles recording waste/spoilage with stock reduction
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from backend.service_inventory.models.database import get_db
from backend.service_inventory.models import InventoryItem, StockMovement
from backend.service_inventory.services.waste_service import WasteService
from backend.service_inventory.schemas.waste import (
    WasteCreateRequest,
    WasteResponse,
    WasteListResponse
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
    prefix="/api/v1/inventory/waste",
    tags=["Waste Management"]
)


@router.post(
    "",
    response_model=WasteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("inventory:manage"))]
)
def record_waste(
    waste_data: WasteCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Record waste/spoilage - reduces stock and creates movement log

    - **inventory_item_id**: ID of the inventory item
    - **quantity**: Quantity to waste
    - **reason**: Reason for waste (e.g., "lejárt", "sérült", "minőségi probléma")
    - **waste_date**: Date of waste
    - **noted_by**: Person reporting waste (optional)
    - **notes**: Additional notes (optional)
    - **employee_id**: Employee ID recording waste (optional)
    """
    try:
        waste_log, movement_id = WasteService.record_waste(db, waste_data)

        # Get the new stock level
        inv_item = db.query(InventoryItem).filter(
            InventoryItem.id == waste_data.inventory_item_id
        ).first()

        # Build response
        response_data = {
            "id": waste_log.id,
            "inventory_item_id": waste_log.inventory_item_id,
            "quantity": waste_log.quantity,
            "reason": waste_log.reason,
            "waste_date": waste_log.waste_date,
            "noted_by": waste_log.noted_by,
            "notes": waste_log.notes,
            "created_at": waste_log.created_at,
            "stock_movement_id": movement_id,
            "new_stock": inv_item.current_stock_perpetual if inv_item else 0
        }

        return WasteResponse(**response_data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "",
    response_model=WasteListResponse,
    dependencies=[Depends(require_permission("inventory:view"))]
)
def list_waste_logs(
    inventory_item_id: Optional[int] = None,
    waste_date_from: Optional[date] = None,
    waste_date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    """
    List waste logs with pagination and filters

    - **inventory_item_id**: Filter by inventory item ID
    - **waste_date_from**: Filter by waste date (from)
    - **waste_date_to**: Filter by waste date (to)
    - **page**: Page number (starts at 1)
    - **page_size**: Items per page
    """
    # Validate page parameters
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

    skip = (page - 1) * page_size

    try:
        waste_logs, total = WasteService.list_waste_logs(
            db=db,
            inventory_item_id=inventory_item_id,
            waste_date_from=waste_date_from,
            waste_date_to=waste_date_to,
            skip=skip,
            limit=page_size
        )

        # Build responses with stock movement info
        responses = []
        for log in waste_logs:
            # Get inventory item for new stock
            inv_item = db.query(InventoryItem).filter(
                InventoryItem.id == log.inventory_item_id
            ).first()

            # Get stock movement
            movement = db.query(StockMovement).filter(
                StockMovement.related_id == log.id,
                StockMovement.reason == "WASTE"
            ).first()

            response_data = {
                "id": log.id,
                "inventory_item_id": log.inventory_item_id,
                "quantity": log.quantity,
                "reason": log.reason,
                "waste_date": log.waste_date,
                "noted_by": log.noted_by,
                "notes": log.notes,
                "created_at": log.created_at,
                "stock_movement_id": movement.id if movement else None,
                "new_stock": inv_item.current_stock_perpetual if inv_item else 0
            }
            responses.append(WasteResponse(**response_data))

        return WasteListResponse(
            waste_logs=responses,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{waste_id}",
    response_model=WasteResponse,
    dependencies=[Depends(require_permission("inventory:view"))]
)
def get_waste_log(
    waste_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific waste log by ID"""
    waste_log = WasteService.get_waste_log(db, waste_id)
    if not waste_log:
        raise HTTPException(status_code=404, detail=f"Waste log with ID {waste_id} not found")

    # Get inventory item for new stock
    inv_item = db.query(InventoryItem).filter(
        InventoryItem.id == waste_log.inventory_item_id
    ).first()

    # Get stock movement
    movement = db.query(StockMovement).filter(
        StockMovement.related_id == waste_log.id,
        StockMovement.reason == "WASTE"
    ).first()

    response_data = {
        "id": waste_log.id,
        "inventory_item_id": waste_log.inventory_item_id,
        "quantity": waste_log.quantity,
        "reason": waste_log.reason,
        "waste_date": waste_log.waste_date,
        "noted_by": waste_log.noted_by,
        "notes": waste_log.notes,
        "created_at": waste_log.created_at,
        "stock_movement_id": movement.id if movement else None,
        "new_stock": inv_item.current_stock_perpetual if inv_item else 0
    }

    return WasteResponse(**response_data)
