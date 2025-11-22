"""
Pydantic schemas for Table entities.
Updated for Floor Plan Editor (Phase 1).
"""

from typing import Optional, Any, List

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
    room_id: Optional[int] = Field(None, description="ID of the room this table belongs to")

    # Geometry
    position_x: Optional[int] = Field(0, description="X coordinate")
    position_y: Optional[int] = Field(0, description="Y coordinate")
    width: Optional[int] = Field(80, description="Width in pixels")
    height: Optional[int] = Field(80, description="Height in pixels")
    rotation: Optional[float] = Field(0.0, description="Rotation in degrees")
    shape: Optional[str] = Field("rect", description="'rect' or 'round'")

    capacity: Optional[int] = Field(
        4,
        ge=1,
        description="Maximum seating capacity"
    )

    metadata_json: Optional[dict[str, Any]] = Field(None, description="Extra visual config")


class TableCreate(TableBase):
    """Schema for creating a new table."""
    pass


class TableMoveRequest(BaseModel):
    """Schema for moving a table to a new section."""
    new_section: str


class TableMergeRequest(BaseModel):
    """Schema for merging tables."""
    primary_table_id: int
    secondary_table_ids: List[int]


class TableUpdate(BaseModel):
    """Schema for updating an existing table."""

    table_number: Optional[str] = None
    room_id: Optional[int] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    rotation: Optional[float] = None
    shape: Optional[str] = None
    capacity: Optional[int] = None
    metadata_json: Optional[dict[str, Any]] = None


class TableInDB(TableBase):
    """Schema for table as stored in database."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique table identifier")


class TableResponse(TableInDB):
    """Schema for table API responses."""
    pass


class TableListResponse(BaseModel):
    """Schema for paginated table list response."""
    items: List[TableResponse]
    total: int
    page: int
    page_size: int
