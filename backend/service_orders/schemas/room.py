"""
Pydantic schemas for Room entities.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class RoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: Optional[str] = "indoor"
    width: Optional[int] = 800
    height: Optional[int] = 600
    background_image_url: Optional[str] = None
    is_active: Optional[bool] = True
    display_order: Optional[int] = 0

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    background_image_url: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

class RoomResponse(RoomBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class RoomReorder(BaseModel):
    """Schema for reordering rooms"""
    room_ids: List[int] = Field(..., description="List of room IDs in the desired order")
