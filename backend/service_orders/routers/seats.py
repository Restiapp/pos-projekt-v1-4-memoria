"""
Seat API Router - RESTful endpoints for Seat Management
Module 1: Rendeléskezelés és Asztalok

Ez a modul tartalmazza az ülőhelyekhez kapcsolódó FastAPI route-okat.
Használja a SeatService-t az üzleti logika végrehajtásához.
Támogatja a split-check (számlák személyenkénti felosztását).
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.services.seat_service import SeatService
from backend.service_orders.schemas.seat import (
    SeatCreate,
    SeatUpdate,
    SeatResponse,
    SeatListResponse,
)

# APIRouter létrehozása
router = APIRouter(
    prefix="/seats",
    tags=["seats"],
    responses={
        404: {"description": "Seat not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)


@router.post(
    "",
    response_model=SeatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Új ülőhely létrehozása",
    description="""
    Új ülőhely létrehozása a rendszerben.

    **Üzleti szabályok:**
    - Az asztal (table_id) léteznie kell
    - A (table_id, seat_number) kombináció egyedi kell legyen
    - A seat_number minimum 1 kell legyen

    **Használati esetek:**
    - Új szék hozzáadása egy asztalhoz
    - Split-check támogatás (vendégenkénti rendelés követés)

    **Visszatérési értékek:**
    - 201: Ülőhely sikeresen létrehozva
    - 400: Validációs hiba, már létező kombináció vagy nem létező asztal
    """,
    response_description="Újonnan létrehozott ülőhely adatai",
)
def create_seat(
    seat_data: SeatCreate,
    db: Session = Depends(get_db),
) -> SeatResponse:
    """
    Új ülőhely létrehozása.

    Args:
        seat_data: Ülőhely adatok (table_id, seat_number)
        db: Database session (dependency injection)

    Returns:
        SeatResponse: Létrehozott ülőhely adatai

    Raises:
        HTTPException 400: Ha az asztal nem létezik vagy a kombináció már létezik
    """
    try:
        seat = SeatService.create_seat(db=db, seat_data=seat_data)
        return seat
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/bulk",
    response_model=list[SeatResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Több ülőhely egyidejű létrehozása",
    description="""
    Több ülőhely egyidejű létrehozása egy asztalhoz.

    **Üzleti szabályok:**
    - Az asztal (table_id) léteznie kell
    - A seat_count értékének pozitívnak kell lennie
    - Az ülőhelyek sorszáma 1-től indul és folyamatosan növekszik

    **Használati esetek:**
    - Új asztal beállítása több székkel
    - Asztal kapacitásának növelése

    **Visszatérési értékek:**
    - 201: Ülőhelyek sikeresen létrehozva
    - 400: Validációs hiba vagy nem létező asztal
    """,
    response_description="Újonnan létrehozott ülőhelyek listája",
)
def bulk_create_seats(
    table_id: int = Query(..., description="Asztal azonosító"),
    seat_count: int = Query(..., ge=1, description="Létrehozandó ülőhelyek száma"),
    db: Session = Depends(get_db),
) -> list[SeatResponse]:
    """
    Több ülőhely egyidejű létrehozása.

    Args:
        table_id: Asztal azonosító
        seat_count: Létrehozandó ülőhelyek száma
        db: Database session (dependency injection)

    Returns:
        list[SeatResponse]: Létrehozott ülőhelyek listája

    Raises:
        HTTPException 400: Ha az asztal nem létezik vagy a seat_count <= 0
    """
    try:
        seats = SeatService.bulk_create_seats(db=db, table_id=table_id, seat_count=seat_count)
        return seats
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=SeatListResponse,
    status_code=status.HTTP_200_OK,
    summary="Ülőhelyek listázása",
    description="""
    Ülőhelyek lekérdezése lapozással.

    **Lapozási paraméterek:**
    - page: Oldal száma (1-től kezdődik)
    - page_size: Oldalméret (max 100)

    **Visszatérési értékek:**
    - 200: Ülőhely lista sikeresen lekérdezve
    - 400: Hibás lapozási paraméterek
    """,
    response_description="Ülőhelyek listája lapozási információkkal",
)
def get_seats(
    page: int = Query(1, ge=1, description="Oldal száma (1-től kezdődik)"),
    page_size: int = Query(20, ge=1, le=100, description="Oldalméret (max 100)"),
    db: Session = Depends(get_db),
) -> SeatListResponse:
    """
    Ülőhelyek listázása lapozással.

    Args:
        page: Oldal száma (1-től kezdődik)
        page_size: Oldalméret
        db: Database session (dependency injection)

    Returns:
        SeatListResponse: Ülőhely lista metaadatokkal (total, page, page_size)
    """
    # Számítsuk ki a skip értéket a page alapján
    skip = (page - 1) * page_size

    seats, total = SeatService.list_seats(db=db, skip=skip, limit=page_size)

    return SeatListResponse(
        items=seats,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/by-table/{table_id}",
    response_model=list[SeatResponse],
    status_code=status.HTTP_200_OK,
    summary="Asztalhoz tartozó ülőhelyek listázása",
    description="""
    Egy adott asztalhoz tartozó összes ülőhely listázása.

    **Használati esetek:**
    - Asztal térképes megjelenítése
    - Rendelés hozzárendelése ülőhelyhez
    - Split-check számla generálás

    **Visszatérési értékek:**
    - 200: Ülőhely lista sikeresen lekérdezve (üres lista, ha nincs ülőhely)
    """,
    response_description="Asztalhoz tartozó ülőhelyek listája seat_number szerint rendezve",
)
def get_seats_by_table(
    table_id: int,
    db: Session = Depends(get_db),
) -> list[SeatResponse]:
    """
    Asztalhoz tartozó összes ülőhely listázása.

    Args:
        table_id: Asztal azonosító
        db: Database session (dependency injection)

    Returns:
        list[SeatResponse]: Ülőhelyek listája seat_number szerint rendezve
    """
    return SeatService.list_seats_by_table(db=db, table_id=table_id)


@router.get(
    "/by-table/{table_id}/seat/{seat_number}",
    response_model=SeatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ülőhely lekérdezése asztal és székszám alapján",
    description="""
    Ülőhely lekérdezése asztal ID és székszám alapján.

    **Használati esetek:**
    - Ülőhely azonosítás asztal térképről
    - QR kód alapú rendelés (asztal + szék száma)
    - Gyors ülőhely keresés

    **Visszatérési értékek:**
    - 200: Ülőhely sikeresen lekérdezve
    - 404: Ülőhely nem található a megadott kombinációval
    """,
    response_description="Ülőhely adatai",
)
def get_seat_by_table_and_number(
    table_id: int,
    seat_number: int,
    db: Session = Depends(get_db),
) -> SeatResponse:
    """
    Ülőhely lekérdezése asztal ID és székszám alapján.

    Args:
        table_id: Asztal azonosító
        seat_number: Szék száma az asztalon belül
        db: Database session (dependency injection)

    Returns:
        SeatResponse: Ülőhely adatai

    Raises:
        HTTPException 404: Ha az ülőhely nem található
    """
    seat = SeatService.get_seat_by_table_and_number(
        db=db,
        table_id=table_id,
        seat_number=seat_number
    )
    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ülőhely (Asztal ID: {table_id}, Szék szám: {seat_number}) nem található"
        )
    return seat


@router.get(
    "/{seat_id}",
    response_model=SeatResponse,
    status_code=status.HTTP_200_OK,
    summary="Egyedi ülőhely lekérdezése",
    description="""
    Egyedi ülőhely lekérdezése ID alapján.

    **Használati esetek:**
    - Ülőhely részleteinek megjelenítése
    - Szerkesztési form előtöltése
    - Ülőhely adatok validálása

    **Visszatérési értékek:**
    - 200: Ülőhely sikeresen lekérdezve
    - 404: Ülőhely nem található a megadott ID-val
    """,
    response_description="Ülőhely adatai",
)
def get_seat(
    seat_id: int,
    db: Session = Depends(get_db),
) -> SeatResponse:
    """
    Egyedi ülőhely lekérdezése ID alapján.

    Args:
        seat_id: Ülőhely azonosító
        db: Database session (dependency injection)

    Returns:
        SeatResponse: Ülőhely adatai

    Raises:
        HTTPException 404: Ha az ülőhely nem található
    """
    seat = SeatService.get_seat(db=db, seat_id=seat_id)
    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ülőhely (ID: {seat_id}) nem található"
        )
    return seat


@router.put(
    "/{seat_id}",
    response_model=SeatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ülőhely módosítása",
    description="""
    Meglévő ülőhely módosítása ID alapján.

    **Üzleti szabályok:**
    - Ha a table_id módosul, az új asztalnak léteznie kell
    - A (table_id, seat_number) kombinációnak egyedinek kell lennie
    - A seat_number minimum 1 kell legyen

    **Részleges módosítás (PATCH-szerű viselkedés):**
    - Csak a megadott mezők kerülnek módosításra
    - A nem megadott mezők értéke nem változik

    **Visszatérési értékek:**
    - 200: Ülőhely sikeresen módosítva
    - 404: Ülőhely nem található
    - 400: Validációs hiba, nem létező asztal vagy kombináció ütközés
    """,
    response_description="Módosított ülőhely adatai",
)
def update_seat(
    seat_id: int,
    seat_data: SeatUpdate,
    db: Session = Depends(get_db),
) -> SeatResponse:
    """
    Ülőhely módosítása.

    Args:
        seat_id: Módosítandó ülőhely azonosítója
        seat_data: Módosítandó mezők (csak a megadott mezők változnak)
        db: Database session (dependency injection)

    Returns:
        SeatResponse: Módosított ülőhely adatai

    Raises:
        HTTPException 404: Ha az ülőhely nem található
        HTTPException 400: Ha validációs hiba történik
    """
    try:
        seat = SeatService.update_seat(db=db, seat_id=seat_id, seat_data=seat_data)
        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ülőhely (ID: {seat_id}) nem található"
            )
        return seat
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{seat_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Ülőhely törlése",
    description="""
    Ülőhely törlése ID alapján.

    **Törlési szabályok:**
    - Ha az ülőhelyhez rendelés tételek tartoznak, azok is törlődnek vagy orphan maradnak
      (függ a kapcsolat konfigurációtól)

    **Visszatérési értékek:**
    - 200: Ülőhely sikeresen törölve
    - 404: Ülőhely nem található

    **Figyelem:**
    Az ülőhely törlése visszafordíthatatlan és hatással lehet a kapcsolódó rendelésekre!
    """,
    response_description="Törlés megerősítése (message és deleted_id)",
)
def delete_seat(
    seat_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """
    Ülőhely törlése.

    Args:
        seat_id: Törlendő ülőhely azonosítója
        db: Database session (dependency injection)

    Returns:
        dict: Törlés megerősítő üzenet és a törölt ID

    Raises:
        HTTPException 404: Ha az ülőhely nem található
    """
    success = SeatService.delete_seat(db=db, seat_id=seat_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ülőhely (ID: {seat_id}) nem található"
        )

    return {
        "message": f"Ülőhely (ID: {seat_id}) sikeresen törölve",
        "deleted_id": seat_id
    }
