"""
Pydantic Schemas for Waste Management
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class WasteCreateRequest(BaseModel):
    """Schema for recording waste"""
    inventory_item_id: int = Field(..., description="ID of the inventory item")
    quantity: Decimal = Field(..., gt=0, description="Quantity to waste")
    reason: str = Field(..., min_length=1, max_length=100, description="Reason for waste")
    waste_date: date = Field(..., description="Date of waste")
    noted_by: Optional[str] = Field(None, max_length=100, description="Person reporting waste")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    employee_id: Optional[int] = Field(None, description="ID of employee recording waste")


class WasteResponse(BaseModel):
    """Response after recording waste"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_item_id: int
    quantity: Decimal
    reason: str
    waste_date: date
    noted_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    # Include stock movement info
    stock_movement_id: Optional[int] = None
    new_stock: Decimal = Field(..., description="Stock level after waste")


class WasteListResponse(BaseModel):
    """Paginated list of waste records"""
    waste_logs: List[WasteResponse]
    total: int
    page: int
    page_size: int
