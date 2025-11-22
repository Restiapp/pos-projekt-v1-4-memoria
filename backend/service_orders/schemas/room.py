from typing import Optional
from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    name: str = Field(..., description="Helyiség neve (pl. Terasz)")
    width: int = Field(800, description="Helyiség szélessége pixelben")
    height: int = Field(600, description="Helyiség magassága pixelben")
    is_active: bool = Field(True, description="Aktív-e a helyiség")


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    is_active: Optional[bool] = None


class RoomResponse(RoomBase):
    id: int

    class Config:
        from_attributes = True
