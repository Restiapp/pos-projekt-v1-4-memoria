"""
Pydantic Schemas for Stock Movement Logging
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Enums
class MovementReasonEnum(str):
    """Movement reason enumeration for API"""
    INTAKE = "INTAKE"
    SALE = "SALE"
    WASTE = "WASTE"
    CORRECTION = "CORRECTION"
    INITIAL = "INITIAL"


# Stock Movement Schemas
class StockMovementBase(BaseModel):
    """Base schema for stock movements"""
    inventory_item_id: int = Field(..., description="ID of the inventory item")
    change_amount: Decimal = Field(..., description="Change in stock (positive=increase, negative=decrease)")
    reason: str = Field(..., description="Reason for movement: INTAKE, SALE, WASTE, CORRECTION, INITIAL")
    related_id: Optional[int] = Field(None, description="Related record ID (invoice_id, order_id, etc.)")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")
    employee_id: Optional[int] = Field(None, description="ID of employee who triggered movement")

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        """Validate reason is a valid enum value"""
        valid_reasons = ['INTAKE', 'SALE', 'WASTE', 'CORRECTION', 'INITIAL']
        if v not in valid_reasons:
            raise ValueError(f"Reason must be one of: {', '.join(valid_reasons)}")
        return v


class StockMovementCreate(StockMovementBase):
    """Schema for creating a stock movement (internal use)"""
    stock_after: Decimal = Field(..., description="Stock level after this movement")


class StockMovementResponse(StockMovementBase):
    """Schema for stock movement responses"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_after: Decimal = Field(..., description="Stock level after this movement")
    movement_type: str = Field(..., description="Increase or Decrease")
    created_at: datetime

    # Optional: Include inventory item details
    inventory_item_name: Optional[str] = None
    inventory_item_unit: Optional[str] = None


class StockMovementListResponse(BaseModel):
    """Paginated list of stock movements"""
    movements: List[StockMovementResponse]
    total: int
    page: int
    page_size: int


class StockMovementFilter(BaseModel):
    """Filters for querying stock movements"""
    inventory_item_id: Optional[int] = None
    reason: Optional[str] = None
    employee_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Manual Stock Correction Schema
class StockCorrectionRequest(BaseModel):
    """Schema for manual stock corrections"""
    inventory_item_id: int = Field(..., description="ID of the inventory item")
    change_amount: Decimal = Field(..., description="Change in stock (positive=increase, negative=decrease)")
    notes: str = Field(..., min_length=1, max_length=500, description="Reason for correction (required)")
    employee_id: Optional[int] = Field(None, description="ID of employee making correction")

    @field_validator('change_amount')
    @classmethod
    def validate_non_zero(cls, v):
        """Ensure correction is not zero"""
        if v == 0:
            raise ValueError("Correction amount cannot be zero")
        return v


class StockCorrectionResponse(BaseModel):
    """Response after stock correction"""
    movement: StockMovementResponse
    old_stock: Decimal
    new_stock: Decimal
    message: str = "Stock corrected successfully"
