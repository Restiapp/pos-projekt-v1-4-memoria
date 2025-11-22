"""
Floorplan Router - Frontend API
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.service_orders.models.database import get_db
from backend.service_orders.services.floorplan_service import FloorplanService
from backend.service_orders.schemas.floorplan import FloorplanFullMapResponse
# Import RBAC dependencies
from backend.service_admin.dependencies import require_permission

floorplan_router = APIRouter(
    prefix="/floorplan",
    tags=["Floorplan"],
)

@floorplan_router.get(
    "/full-map",
    response_model=FloorplanFullMapResponse,
    summary="Get full floorplan structure",
    description="Returns aggregated Rooms and Tables for the floor plan editor.",
    dependencies=[Depends(require_permission("orders:view"))]
)
def get_full_map(
    db: Session = Depends(get_db)
) -> FloorplanFullMapResponse:
    """
    Get the full map (Rooms + Tables) for the frontend editor.
    """
    return FloorplanService.get_full_map(db)
