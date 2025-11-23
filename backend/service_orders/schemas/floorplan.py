"""
Pydantic schemas for Floorplan entities.
"""

from typing import List, Optional
from pydantic import BaseModel
from backend.core_domain.enums import RoomType, TableShape

class FloorplanTableDTO(BaseModel):
    id: int
    room_id: str  # Using string ID for section names temporarily
    name: str
    number: str
    capacity: int
    shape: TableShape
    x: int
    y: int
    width: int
    height: int
    is_active: bool = True
    is_smoking: bool = False

class FloorplanRoomDTO(BaseModel):
    id: str  # Using string ID for section names temporarily
    name: str
    type: RoomType
    position_index: int
    width: int
    height: int
    is_active: bool = True

class FloorplanFullMapResponse(BaseModel):
    rooms: List[FloorplanRoomDTO]
    tables: List[FloorplanTableDTO]
