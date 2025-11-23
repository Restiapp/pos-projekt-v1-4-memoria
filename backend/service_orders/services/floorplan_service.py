"""
Floorplan Service - Aggregation Logic
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.service_orders.models.table import Table
from backend.service_orders.schemas.floorplan import (
    FloorplanFullMapResponse,
    FloorplanRoomDTO,
    FloorplanTableDTO
)
from backend.core_domain.enums import RoomType, TableShape

class FloorplanService:
    @staticmethod
    def get_full_map(db: Session) -> FloorplanFullMapResponse:
        """
        Aggregates Tables into a virtual Room structure.
        Mocks missing data (Room entities, Table dimensions) for frontend compatibility.
        """
        tables = db.query(Table).all()

        # 1. Identify "Rooms" from distinct 'section' strings
        # Default config for known sections
        known_sections: Dict[str, Dict[str, Any]] = {
            "Belső terem": {"type": RoomType.INDOOR, "index": 0},
            "Terasz": {"type": RoomType.TERRACE_NONSMOKING, "index": 1},
            "Bár": {"type": RoomType.BAR, "index": 2},
            "VIP": {"type": RoomType.VIP, "index": 3}
        }

        # Group tables by section
        rooms_map: Dict[str, FloorplanRoomDTO] = {}
        table_dtos: List[FloorplanTableDTO] = []

        for t in tables:
            # Normalize section name (handle None)
            section_name = t.section if t.section else "Unassigned"

            # Create Room DTO if not exists
            if section_name not in rooms_map:
                config = known_sections.get(section_name, {"type": RoomType.INDOOR, "index": 99})
                rooms_map[section_name] = FloorplanRoomDTO(
                    id=section_name, # Use name as ID for now
                    name=section_name,
                    type=config["type"],
                    position_index=config["index"],
                    width=1000, # Default canvas size
                    height=800,
                    is_active=True
                )

            # Map Table to DTO
            # Default logic for missing fields:
            # - shape: RECTANGLE unless capacity < 3 (then ROUND?) - keep simple: RECTANGLE
            # - size: 80x80 default
            table_dtos.append(FloorplanTableDTO(
                id=t.id,
                room_id=section_name,
                name=f"Asztal {t.table_number}",
                number=t.table_number,
                capacity=t.capacity if t.capacity else 4,
                shape=TableShape.RECTANGLE, # Default
                x=t.position_x if t.position_x is not None else 0,
                y=t.position_y if t.position_y is not None else 0,
                width=80,  # Default
                height=80, # Default
                is_active=True,
                is_smoking=False # Default
            ))

        # Convert rooms map to sorted list
        room_list = sorted(rooms_map.values(), key=lambda r: r.position_index)

        return FloorplanFullMapResponse(
            rooms=room_list,
            tables=table_dtos
        )
