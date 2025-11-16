"""
Pydantic schemas for Table entities.

This module defines the request and response schemas for table operations
in the Service Orders module (Module 1).
"""

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TableBase(BaseModel):
    """Base schema for Table with common fields."""

    table_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique table identifier/number",
        examples=["1", "A1", "VIP-01", "Terasz-3"]
    )
    position_x: Optional[int] = Field(
        None,
        description="X coordinate for visual table map positioning",
        examples=[100, 250, 450]
    )
    position_y: Optional[int] = Field(
        None,
        description="Y coordinate for visual table map positioning",
        examples=[150, 200, 300]
    )
    capacity: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum seating capacity of the table",
        examples=[2, 4, 6, 8]
    )


class TableCreate(TableBase):
    """Schema for creating a new table."""
    pass


class TableUpdate(BaseModel):
    """Schema for updating an existing table."""

    table_number: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Table identifier/number"
    )
    position_x: Optional[int] = Field(
        None,
        description="X coordinate for visual positioning"
    )
    position_y: Optional[int] = Field(
        None,
        description="Y coordinate for visual positioning"
    )
    capacity: Optional[int] = Field(
        None,
        ge=1,
        description="Table seating capacity"
    )


class TableInDB(TableBase):
    """Schema for table as stored in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique table identifier",
        examples=[1, 42]
    )


class TableResponse(TableInDB):
    """Schema for table API responses."""
    pass


class TableListResponse(BaseModel):
    """Schema for paginated table list responses."""

    items: list[TableResponse] = Field(
        ...,
        description="List of tables"
    )
    total: int = Field(
        ...,
        description="Total number of tables",
        examples=[25]
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
