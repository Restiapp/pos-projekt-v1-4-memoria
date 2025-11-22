"""
Waste Log API Routes
Module 5: Készletkezelés

Ez a modul tartalmazza a selejtezési naplókhoz kapcsolódó FastAPI végpontokat.
Implementálja a selejt rögzítését és lekérdezését.
"""

from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.service_inventory.models.database import get_db
from backend.service_inventory.models.waste_log import WasteLog
from backend.service_inventory.models.inventory_item import InventoryItem
from backend.service_inventory.schemas.waste_log import (
    WasteLogCreate,
    WasteLogResponse,
)


# Router létrehozása
router = APIRouter(
    prefix="/inventory/waste",
    tags=["waste"]
)


@router.post(
    "",
    response_model=WasteLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new waste log entry",
    description="""
    Új selejt bejegyzés rögzítése az adatbázisban.

    A szolgáltatás a következőket végzi:
    1. Validálja a bemeneti adatokat
    2. Ellenőrzi, hogy létezik-e a megadott inventory_item_id
    3. Rögzíti a selejtet az adatbázisban
    4. Opcionálisan csökkentheti a készletet (jelenleg nem automatikus)

    **Selejt okok:**
    - expired: Lejárt
    - damaged: Sérült
    - quality_issue: Minőségi probléma
    - other: Egyéb

    **Visszatérési értékek:**
    - 201: Sikeresen rögzített selejt
    - 400: Hibás bemeneti adatok
    - 404: Nem létező inventory_item_id
    - 500: Adatbázis hiba
    """,
)
async def create_waste_log(
    waste_log: WasteLogCreate,
    db: Session = Depends(get_db)
):
    """
    Új selejt bejegyzés létrehozása.

    Args:
        waste_log (WasteLogCreate): Selejt adatok
        db (Session): SQLAlchemy adatbázis session (dependency injection)

    Returns:
        WasteLogResponse: A rögzített selejt adatai

    Raises:
        HTTPException 404: Nem létező inventory_item_id
        HTTPException 500: Adatbázis hiba
    """
    try:
        # Ellenőrizzük, hogy létezik-e az inventory item
        inventory_item = db.query(InventoryItem).filter(
            InventoryItem.id == waste_log.inventory_item_id
        ).first()

        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory item with ID {waste_log.inventory_item_id} not found"
            )

        # Új WasteLog rekord létrehozása
        db_waste_log = WasteLog(
            inventory_item_id=waste_log.inventory_item_id,
            quantity=waste_log.quantity,
            reason=waste_log.reason,
            waste_date=waste_log.waste_date,
            noted_by=waste_log.noted_by,
            notes=waste_log.notes
        )

        # Mentés az adatbázisba
        db.add(db_waste_log)
        db.commit()
        db.refresh(db_waste_log)

        return db_waste_log

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating waste log: {str(e)}"
        )


@router.get(
    "",
    response_model=list[WasteLogResponse],
    summary="Get waste logs",
    description="""
    Selejt naplók lekérdezése szűrési feltételekkel.

    Támogatott szűrők:
    - inventory_item_id: Szűrés tétel szerint
    - start_date: Kezdő dátum (ezen vagy után)
    - end_date: Záró dátum (ezen vagy előtt)
    - limit: Maximális találatok száma (alapértelmezett: 100)
    - offset: Eltolás (alapértelmezett: 0)

    **Visszatérési értékek:**
    - 200: Sikeres lekérdezés (lista, akár üres is lehet)
    - 500: Adatbázis hiba
    """,
)
async def get_waste_logs(
    inventory_item_id: Optional[int] = Query(None, description="Filter by inventory item ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (inclusive)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Selejt naplók listázása szűrési feltételekkel.

    Args:
        inventory_item_id (Optional[int]): Szűrés tétel szerint
        start_date (Optional[date]): Kezdő dátum
        end_date (Optional[date]): Záró dátum
        limit (int): Maximális találatok száma
        offset (int): Eltolás
        db (Session): SQLAlchemy adatbázis session (dependency injection)

    Returns:
        list[WasteLogResponse]: Selejt naplók listája

    Raises:
        HTTPException 500: Adatbázis hiba
    """
    try:
        # Query építése
        query = db.query(WasteLog)

        # Szűrők alkalmazása
        filters = []

        if inventory_item_id is not None:
            filters.append(WasteLog.inventory_item_id == inventory_item_id)

        if start_date is not None:
            filters.append(WasteLog.waste_date >= start_date)

        if end_date is not None:
            filters.append(WasteLog.waste_date <= end_date)

        if filters:
            query = query.filter(and_(*filters))

        # Sorrendezés (legújabb először)
        query = query.order_by(WasteLog.created_at.desc())

        # Pagination
        waste_logs = query.limit(limit).offset(offset).all()

        return waste_logs

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching waste logs: {str(e)}"
        )
