"""
Room Router - FastAPI Endpoints for Room Management
Module 1: Rendeléskezelés és Asztalok

Ez a router felelős a helyiségek REST API végpontjaiért.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.models.room import Room
from backend.service_orders.schemas.room import RoomCreate, RoomUpdate, RoomResponse

# Router létrehozása
rooms_router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
    responses={404: {"description": "Room not found"}}
)


@rooms_router.post(
    "/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new room",
    description="Creates a new room (dining area) in the system."
)
def create_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db)
) -> RoomResponse:
    """
    Create a new room.
    """
    # Check if name already exists
    existing_room = db.query(Room).filter(Room.name == room_data.name).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room with name '{room_data.name}' already exists"
        )

    new_room = Room(
        name=room_data.name,
        width=room_data.width,
        height=room_data.height,
        is_active=room_data.is_active
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room


@rooms_router.get(
    "/",
    response_model=List[RoomResponse],
    summary="List all rooms",
    description="Retrieve a list of all rooms."
)
def get_rooms(
    db: Session = Depends(get_db)
) -> List[RoomResponse]:
    """
    Get all rooms.
    """
    return db.query(Room).all()


@rooms_router.get(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Get room by ID",
    description="Retrieve a single room by its unique identifier."
)
def get_room(
    room_id: int,
    db: Session = Depends(get_db)
) -> RoomResponse:
    """
    Get a single room by ID.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    return room


@rooms_router.put(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Update a room",
    description="Update an existing room's details."
)
def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: Session = Depends(get_db)
) -> RoomResponse:
    """
    Update an existing room.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )

    # Update fields if provided
    if room_data.name is not None:
        # Check uniqueness if name changes
        if room_data.name != room.name:
            existing = db.query(Room).filter(Room.name == room_data.name).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Room with name '{room_data.name}' already exists"
                )
        room.name = room_data.name
    
    if room_data.width is not None:
        room.width = room_data.width
    if room_data.height is not None:
        room.height = room_data.height
    if room_data.is_active is not None:
        room.is_active = room_data.is_active

    db.commit()
    db.refresh(room)
    return room


@rooms_router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a room",
    description="Delete a room from the system."
)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a room.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )

    db.delete(room)
    db.commit()
    return None
