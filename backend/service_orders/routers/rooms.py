"""
Room Router - API Endpoints
Module 1: Floor Plan Management
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.models.room import Room
from backend.service_orders.schemas.room import RoomCreate, RoomResponse, RoomUpdate

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
    responses={404: {"description": "Room not found"}},
)

@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    db_room = Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.get("/", response_model=List[RoomResponse])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Room).offset(skip).limit(limit).all()

@router.get("/{room_id}", response_model=RoomResponse)
def read_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

@router.put("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, room: RoomUpdate, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    update_data = room.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_room, key, value)

    db.commit()
    db.refresh(db_room)
    return db_room

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    db.delete(db_room)
    db.commit()
    return None
