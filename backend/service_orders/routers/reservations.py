"""
Reservation API Router - RESTful endpoints for Reservation Management
Module 1: Rendeléskezelés és Asztalok

Ez a modul tartalmazza a foglalásokhoz kapcsolódó FastAPI route-okat.
Használja a ReservationService-t az üzleti logika végrehajtásához.
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.services.reservation_service import ReservationService
from backend.service_orders.schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
    ReservationListResponse,
)

# APIRouter létrehozása
router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
    responses={
        404: {"description": "Reservation not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Új foglalás létrehozása",
    description="""
    Új foglalás létrehozása a rendszerben.

    **Üzleti szabályok:**
    - Az asztalnak léteznie kell
    - A vendégszám nem haladhatja meg az asztal kapacitását
    - A státusz alapértelmezetten PENDING

    **Visszatérési értékek:**
    - 201: Foglalás sikeresen létrehozva
    - 400: Validációs hiba vagy üzleti szabály megsértése
    """,
    response_description="Újonnan létrehozott foglalás adatai",
)
def create_reservation(
    reservation_data: ReservationCreate,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    Új foglalás létrehozása.

    Args:
        reservation_data: Foglalás adatok
        db: Database session (dependency injection)

    Returns:
        ReservationResponse: Létrehozott foglalás adatai

    Raises:
        HTTPException 400: Ha validációs hiba történik
    """
    try:
        reservation = ReservationService.create_reservation(db=db, reservation_data=reservation_data)
        return ReservationResponse.model_validate(reservation)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=ReservationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Foglalások listázása",
    description="""
    Foglalások lekérdezése lapozással.

    **Lapozási paraméterek:**
    - page: Oldal száma (1-től kezdődik)
    - page_size: Oldalméret (max 100)

    **Visszatérési értékek:**
    - 200: Foglalások listája sikeresen lekérdezve
    - 400: Hibás lapozási paraméterek
    """,
    response_description="Foglalások listája lapozási információkkal",
)
def get_reservations(
    page: int = Query(1, ge=1, description="Oldal száma (1-től kezdődik)"),
    page_size: int = Query(20, ge=1, le=100, description="Oldalméret (max 100)"),
    db: Session = Depends(get_db),
) -> ReservationListResponse:
    """
    Foglalások listázása lapozással.

    Args:
        page: Oldal száma (1-től kezdődik)
        page_size: Oldalméret
        db: Database session (dependency injection)

    Returns:
        ReservationListResponse: Foglalások listája metaadatokkal
    """
    skip = (page - 1) * page_size
    reservations, total = ReservationService.list_reservations(db=db, skip=skip, limit=page_size)

    return ReservationListResponse(
        items=[ReservationResponse.model_validate(r) for r in reservations],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/by-date/{reservation_date}",
    response_model=list[ReservationResponse],
    status_code=status.HTTP_200_OK,
    summary="Foglalások lekérdezése dátum alapján",
    description="""
    Foglalások lekérdezése adott napon.

    **Használati esetek:**
    - Napi foglalások megjelenítése
    - Naptár nézet feltöltése
    - Kapacitás tervezés

    **Visszatérési értékek:**
    - 200: Foglalások listája az adott napra
    """,
    response_description="Foglalások listája",
)
def get_reservations_by_date(
    reservation_date: date,
    db: Session = Depends(get_db),
) -> list[ReservationResponse]:
    """
    Foglalások lekérdezése dátum alapján.

    Args:
        reservation_date: A foglalás dátuma (YYYY-MM-DD)
        db: Database session (dependency injection)

    Returns:
        list[ReservationResponse]: Foglalások listája
    """
    reservations = ReservationService.get_reservations_by_date(db=db, reservation_date=reservation_date)
    return [ReservationResponse.model_validate(r) for r in reservations]


@router.get(
    "/by-date-range",
    response_model=list[ReservationResponse],
    status_code=status.HTTP_200_OK,
    summary="Foglalások lekérdezése dátumtartomány alapján",
    description="""
    Foglalások lekérdezése megadott időszakban.

    **Használati esetek:**
    - Heti/havi naptár nézet
    - Foglaltsági elemzés
    - Jelentések készítése

    **Visszatérési értékek:**
    - 200: Foglalások listája a megadott időszakban
    """,
    response_description="Foglalások listája",
)
def get_reservations_by_date_range(
    start_date: date = Query(..., description="Kezdő dátum (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Záró dátum (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> list[ReservationResponse]:
    """
    Foglalások lekérdezése dátumtartomány alapján.

    Args:
        start_date: Kezdő dátum
        end_date: Záró dátum
        db: Database session (dependency injection)

    Returns:
        list[ReservationResponse]: Foglalások listája
    """
    reservations = ReservationService.get_reservations_by_date_range(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return [ReservationResponse.model_validate(r) for r in reservations]


@router.get(
    "/by-table/{table_id}",
    response_model=list[ReservationResponse],
    status_code=status.HTTP_200_OK,
    summary="Foglalások lekérdezése asztal alapján",
    description="""
    Foglalások lekérdezése adott asztalra.

    **Használati esetek:**
    - Asztal foglaltsági előzményeinek megtekintése
    - Asztal kiválasztása foglaláshoz

    **Visszatérési értékek:**
    - 200: Foglalások listája az adott asztalra
    """,
    response_description="Foglalások listája",
)
def get_reservations_by_table(
    table_id: int,
    db: Session = Depends(get_db),
) -> list[ReservationResponse]:
    """
    Foglalások lekérdezése asztal alapján.

    Args:
        table_id: Az asztal azonosítója
        db: Database session (dependency injection)

    Returns:
        list[ReservationResponse]: Foglalások listája
    """
    reservations = ReservationService.get_reservations_by_table(db=db, table_id=table_id)
    return [ReservationResponse.model_validate(r) for r in reservations]


@router.get(
    "/by-status/{status}",
    response_model=list[ReservationResponse],
    status_code=status.HTTP_200_OK,
    summary="Foglalások lekérdezése státusz alapján",
    description="""
    Foglalások lekérdezése státusz szerint.

    **Státuszok:**
    - PENDING: Függőben lévő
    - CONFIRMED: Megerősített
    - CANCELLED: Törölve
    - COMPLETED: Teljesítve
    - NO_SHOW: Nem jelent meg

    **Visszatérési értékek:**
    - 200: Foglalások listája a megadott státusszal
    """,
    response_description="Foglalások listája",
)
def get_reservations_by_status(
    status: str,
    db: Session = Depends(get_db),
) -> list[ReservationResponse]:
    """
    Foglalások lekérdezése státusz alapján.

    Args:
        status: Foglalás státusza
        db: Database session (dependency injection)

    Returns:
        list[ReservationResponse]: Foglalások listája
    """
    reservations = ReservationService.get_reservations_by_status(db=db, status=status)
    return [ReservationResponse.model_validate(r) for r in reservations]


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Egyedi foglalás lekérdezése",
    description="""
    Egyedi foglalás lekérdezése ID alapján.

    **Használati esetek:**
    - Foglalás részleteinek megjelenítése
    - Szerkesztési form előtöltése

    **Visszatérési értékek:**
    - 200: Foglalás sikeresen lekérdezve
    - 404: Foglalás nem található
    """,
    response_description="Foglalás adatai",
)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    Egyedi foglalás lekérdezése ID alapján.

    Args:
        reservation_id: Foglalás azonosító
        db: Database session (dependency injection)

    Returns:
        ReservationResponse: Foglalás adatai

    Raises:
        HTTPException 404: Ha a foglalás nem található
    """
    reservation = ReservationService.get_reservation(db=db, reservation_id=reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Foglalás (ID: {reservation_id}) nem található"
        )
    return ReservationResponse.model_validate(reservation)


@router.put(
    "/{reservation_id}",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Foglalás módosítása",
    description="""
    Meglévő foglalás módosítása ID alapján.

    **Üzleti szabályok:**
    - Az asztalnak léteznie kell
    - A vendégszám nem haladhatja meg az asztal kapacitását

    **Részleges módosítás:**
    - Csak a megadott mezők kerülnek módosításra

    **Visszatérési értékek:**
    - 200: Foglalás sikeresen módosítva
    - 404: Foglalás nem található
    - 400: Validációs hiba
    """,
    response_description="Módosított foglalás adatai",
)
def update_reservation(
    reservation_id: int,
    reservation_data: ReservationUpdate,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    Foglalás módosítása.

    Args:
        reservation_id: Módosítandó foglalás azonosítója
        reservation_data: Módosítandó mezők
        db: Database session (dependency injection)

    Returns:
        ReservationResponse: Módosított foglalás adatai

    Raises:
        HTTPException 404: Ha a foglalás nem található
        HTTPException 400: Ha validációs hiba történik
    """
    try:
        reservation = ReservationService.update_reservation(
            db=db,
            reservation_id=reservation_id,
            reservation_data=reservation_data
        )
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Foglalás (ID: {reservation_id}) nem található"
            )
        return ReservationResponse.model_validate(reservation)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{reservation_id}/status",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Foglalás státuszának módosítása",
    description="""
    Foglalás státuszának gyors módosítása.

    **Státuszok:**
    - PENDING: Függőben lévő
    - CONFIRMED: Megerősített
    - CANCELLED: Törölve
    - COMPLETED: Teljesítve
    - NO_SHOW: Nem jelent meg

    **Visszatérési értékek:**
    - 200: Státusz sikeresen módosítva
    - 404: Foglalás nem található
    """,
    response_description="Módosított foglalás adatai",
)
def update_reservation_status(
    reservation_id: int,
    status: str = Query(..., description="Új státusz"),
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    Foglalás státuszának módosítása.

    Args:
        reservation_id: Foglalás azonosítója
        status: Új státusz
        db: Database session (dependency injection)

    Returns:
        ReservationResponse: Módosított foglalás adatai

    Raises:
        HTTPException 404: Ha a foglalás nem található
    """
    reservation = ReservationService.update_reservation_status(
        db=db,
        reservation_id=reservation_id,
        status=status
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Foglalás (ID: {reservation_id}) nem található"
        )
    return ReservationResponse.model_validate(reservation)


@router.delete(
    "/{reservation_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Foglalás törlése",
    description="""
    Foglalás törlése ID alapján.

    **Visszatérési értékek:**
    - 200: Foglalás sikeresen törölve
    - 404: Foglalás nem található

    **Figyelem:**
    A foglalás törlése visszafordíthatatlan!
    """,
    response_description="Törlés megerősítése",
)
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """
    Foglalás törlése.

    Args:
        reservation_id: Törlendő foglalás azonosítója
        db: Database session (dependency injection)

    Returns:
        dict: Törlés megerősítő üzenet

    Raises:
        HTTPException 404: Ha a foglalás nem található
    """
    success = ReservationService.delete_reservation(db=db, reservation_id=reservation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Foglalás (ID: {reservation_id}) nem található"
        )

    return {
        "message": f"Foglalás (ID: {reservation_id}) sikeresen törölve",
        "deleted_id": reservation_id
    }
