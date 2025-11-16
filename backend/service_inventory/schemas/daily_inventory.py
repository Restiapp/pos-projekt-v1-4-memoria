"""
Pydantic schemas for Daily Inventory entities.

This module defines the request and response schemas for daily inventory operations
in the Inventory Service (Module 5). This includes daily inventory sheets (templates/definitions
of which items to count) and daily inventory counts (actual count records).
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, List

from pydantic import BaseModel, Field, ConfigDict, field_validator


# ===== Daily Inventory Sheet Schemas =====

class DailyInventorySheetBase(BaseModel):
    """Base schema for DailyInventorySheet with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the daily inventory sheet (template)",
        examples=["Napi Karton - Reggel", "Napi Karton - Este", "Raktár Heti Leltár"]
    )


class DailyInventorySheetCreate(DailyInventorySheetBase):
    """
    Schema for creating a new daily inventory sheet.

    Optionally includes the list of inventory items to be counted.
    """

    inventory_item_ids: Optional[List[int]] = Field(
        None,
        description="List of inventory item IDs to include in this sheet",
        examples=[[1, 2, 3, 5, 8], [10, 15, 20]]
    )


class DailyInventorySheetUpdate(BaseModel):
    """Schema for updating an existing daily inventory sheet."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name of the daily inventory sheet"
    )
    inventory_item_ids: Optional[List[int]] = Field(
        None,
        description="List of inventory item IDs to include in this sheet"
    )


class DailyInventorySheetInDB(DailyInventorySheetBase):
    """Schema for daily inventory sheet as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique daily inventory sheet identifier",
        examples=[1, 5, 10]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when sheet was created"
    )


class DailyInventorySheetResponse(DailyInventorySheetInDB):
    """Schema for daily inventory sheet API responses."""
    pass


class DailyInventorySheetDetailResponse(DailyInventorySheetResponse):
    """
    Schema for detailed daily inventory sheet response including item list.

    This can include the list of inventory items associated with this sheet.
    """

    inventory_item_ids: Optional[List[int]] = Field(
        None,
        description="List of inventory item IDs included in this sheet"
    )


class DailyInventorySheetListResponse(BaseModel):
    """Schema for paginated daily inventory sheet list responses."""

    items: list[DailyInventorySheetResponse] = Field(
        ...,
        description="List of daily inventory sheets"
    )
    total: int = Field(
        ...,
        description="Total number of daily inventory sheets",
        examples=[5, 10, 20]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
        examples=[1]
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page",
        examples=[20]
    )


# ===== Daily Inventory Count Schemas =====

class DailyInventoryCountBase(BaseModel):
    """Base schema for DailyInventoryCount with common fields."""

    sheet_id: int = Field(
        ...,
        description="Daily inventory sheet identifier (template used for this count)",
        examples=[1, 5, 10]
    )
    count_date: date = Field(
        ...,
        description="Date when the count was performed",
        examples=["2024-01-15", "2024-02-20"]
    )
    employee_id: Optional[int] = Field(
        None,
        description="Employee identifier (who performed the count)",
        examples=[1, 5, 10]
    )


class CountItem(BaseModel):
    """Schema for a single counted item."""

    inventory_item_id: int = Field(
        ...,
        description="Inventory item identifier",
        examples=[1, 5, 10]
    )
    counted_quantity: Decimal = Field(
        ...,
        ge=0,
        decimal_places=3,
        description="Counted quantity",
        examples=[10.500, 25.000, 100.250]
    )


class DailyInventoryCountCreate(DailyInventoryCountBase):
    """
    Schema for creating a new daily inventory count.

    Includes the count data as a structured list of items.
    """

    count_items: List[CountItem] = Field(
        ...,
        description="List of counted items with their quantities"
    )


class DailyInventoryCountUpdate(BaseModel):
    """Schema for updating an existing daily inventory count."""

    sheet_id: Optional[int] = Field(
        None,
        description="Daily inventory sheet identifier"
    )
    count_date: Optional[date] = Field(
        None,
        description="Date when the count was performed"
    )
    employee_id: Optional[int] = Field(
        None,
        description="Employee identifier"
    )
    count_items: Optional[List[CountItem]] = Field(
        None,
        description="List of counted items with their quantities"
    )


class DailyInventoryCountInDB(DailyInventoryCountBase):
    """Schema for daily inventory count as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique daily inventory count identifier",
        examples=[1, 42, 100]
    )
    counts: Dict[str, Decimal] = Field(
        ...,
        description="Count data stored as JSONB (item_id -> quantity)",
        examples=[
            {"1": 10.5, "2": 25.0, "5": 100.25},
            {"10": 5.0, "15": 50.0}
        ]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when count was created"
    )

    @field_validator('counts')
    @classmethod
    def validate_counts(cls, v: Dict[str, Decimal]) -> Dict[str, Decimal]:
        """Validate that counts follow the expected structure."""
        if not isinstance(v, dict):
            raise ValueError("Counts must be a dictionary")

        # Validate that all keys are numeric strings and values are valid decimals
        for item_id, quantity in v.items():
            try:
                int(item_id)  # Ensure key can be converted to int
            except ValueError:
                raise ValueError(f"Count key '{item_id}' must be a numeric string")

            if not isinstance(quantity, (Decimal, int, float)):
                raise ValueError(f"Count quantity for item {item_id} must be a number")

            if float(quantity) < 0:
                raise ValueError(f"Count quantity for item {item_id} must be non-negative")

        return v


class DailyInventoryCountResponse(DailyInventoryCountInDB):
    """Schema for daily inventory count API responses."""
    pass


class DailyInventoryCountDetailResponse(DailyInventoryCountResponse):
    """
    Schema for detailed daily inventory count response.

    This can include additional computed fields or related entities.
    """

    count_items_detail: Optional[List[CountItem]] = Field(
        None,
        description="Structured list of counted items (parsed from counts JSONB)"
    )


class DailyInventoryCountListResponse(BaseModel):
    """Schema for paginated daily inventory count list responses."""

    items: list[DailyInventoryCountResponse] = Field(
        ...,
        description="List of daily inventory counts"
    )
    total: int = Field(
        ...,
        description="Total number of daily inventory counts",
        examples=[50, 100, 200]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
        examples=[1]
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page",
        examples=[20]
    )
