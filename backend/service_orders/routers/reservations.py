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
from backend.service_orders.models.reservation import ReservationStatus
from backend.service_orders.services.reservation_service import ReservationService
from backend.service_orders.schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
    ReservationListResponse,
    AvailabilityQuery,
    AvailabilityResponse,
    ReservationStatusUpdate,
    TimeSlot,
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


@router.get(
    "/availability",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Smart availability checking - Szabad időpontok keresése",
    description="""
    Intelligens elérhetőség vizsgálat - megkeresi az összes szabad időpontot
    egy adott dátumra és vendégszámra.

    **AI-Friendly Features:**
    - Automatikusan generál időpontokat 30 perces intervallumokkal
    - Figyelembe veszi a nyitvatartást
    - Ellenőrzi a meglévő foglalásokat
    - Visszaadja a szabad asztalok listáját minden időpontra

    **Használati esetek:**
    - AI Chatbot számára elérhető időpontok lekérdezése
    - Webes foglalási felület időpont választó
    - Telefonos foglalás segítése

    **Query paraméterek:**
    - date: Dátum (YYYY-MM-DD formátumban)
    - guests: Vendégek száma
    - duration_minutes: Foglalás időtartama percben (opcionális, alapértelmezett: 120)

    **Visszatérési értékek:**
    - 200: Szabad időpontok listája
    - 400: Hibás paraméterek

    **Példa válasz:**
    ```json
    {
      "date": "2025-01-20",
      "guests": 4,
      "available_slots": [
        {"time": "18:00:00", "available_tables": [1, 2, 5]},
        {"time": "18:30:00", "available_tables": [1, 3, 7]},
        {"time": "20:00:00", "available_tables": [2, 5, 8]}
      ],
      "message": null
    }
    ```
    """,
    response_description="Szabad időpontok listája asztal ID-kkal",
)
def check_availability(
    date: date = Query(..., description="Foglalás dátuma (YYYY-MM-DD)"),
    guests: int = Query(..., ge=1, le=50, description="Vendégek száma (1-50)"),
    duration_minutes: int = Query(120, ge=30, le=480, description="Időtartam percben (30-480)"),
    db: Session = Depends(get_db),
) -> AvailabilityResponse:
    """
    Szabad időpontok keresése smart availability logic-kal.

    Args:
        date: Foglalás dátuma
        guests: Vendégek száma
        duration_minutes: Foglalás időtartama percben
        db: Database session (dependency injection)

    Returns:
        AvailabilityResponse: Szabad időpontok listája
    """
    query = AvailabilityQuery(
        date=date,
        guests=guests,
        duration_minutes=duration_minutes
    )

    available_slots, message = ReservationService.get_available_slots(db=db, query=query)

    return AvailabilityResponse(
        date=query.date,
        guests=query.guests,
        available_slots=available_slots,
        message=message
    )


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Új foglalás létrehozása",
    description="""
    Új asztalfoglalás létrehozása a rendszerben.

    **Üzleti szabályok:**
    - Az asztalnak léteznie kell
    - A vendégszámnak kisebb vagy egyenlőnek kell lennie az asztal kapacitásával
    - Nem lehet dupla foglalás ugyanarra az asztalra átfedő időpontban
    - Automatikus ütközésellenőrzés

    **Foglalás forrása:**
    - MANUAL: Személyzet által rögzített
    - AI: AI Chatbot által létrehozott
    - WEB: Webes felületen keresztül

    **Visszatérési értékek:**
    - 201: Foglalás sikeresen létrehozva (status: PENDING)
    - 400: Validációs hiba, kapacitás probléma vagy ütközés
    - 404: Az asztal nem található

    **Példa request body:**
    ```json
    {
      "table_id": 5,
      "customer_name": "Kiss János",
      "customer_phone": "+36301234567",
      "customer_email": "janos.kiss@example.com",
      "start_time": "2025-01-20T18:00:00+01:00",
      "duration_minutes": 120,
      "guest_count": 4,
      "source": "AI",
      "notes": "Birthday celebration"
    }
    ```
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
        HTTPException 400: Validációs hiba vagy ütközés
        HTTPException 404: Asztal nem található
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
    summary="Foglalások listázása szűrőkkel",
    description="""
    Foglalások lekérdezése szűrési lehetőségekkel és lapozással.

    **Szűrési lehetőségek:**
    - table_id: Asztal ID alapján
    - status: Státusz alapján (PENDING, CONFIRMED, CANCELLED, COMPLETED)
    - date_from: Kezdő dátumtól
    - date_to: Záró dátumig
    - customer_phone: Telefonszám alapján (részleges egyezés)
    - customer_email: Email alapján (részleges egyezés)

    **Lapozási paraméterek:**
    - page: Oldal száma (1-től kezdődik)
    - page_size: Oldalméret (max 100)

    **Visszatérési értékek:**
    - 200: Foglalások listája sikeresen lekérdezve

    **Használati példák:**
    - `/reservations?status=PENDING&page=1&page_size=20` - Függő foglalások
    - `/reservations?table_id=5&date_from=2025-01-20` - Egy asztal foglalásai egy dátumtól
    - `/reservations?customer_phone=+3630` - Telefonszám alapján keresés
    """,
    response_description="Foglalások listája lapozási információkkal",
)
def get_reservations(
    page: int = Query(1, ge=1, description="Oldal száma (1-től kezdődik)"),
    page_size: int = Query(20, ge=1, le=100, description="Oldalméret (max 100)"),
    table_id: Optional[int] = Query(None, description="Szűrés asztal ID alapján"),
    status: Optional[ReservationStatus] = Query(None, description="Szűrés státusz alapján"),
    date_from: Optional[date] = Query(None, description="Szűrés kezdő dátum alapján"),
    date_to: Optional[date] = Query(None, description="Szűrés záró dátum alapján"),
    customer_phone: Optional[str] = Query(None, description="Szűrés telefonszám alapján"),
    customer_email: Optional[str] = Query(None, description="Szűrés email alapján"),
    db: Session = Depends(get_db),
) -> ReservationListResponse:
    """
    Foglalások listázása szűrőkkel és lapozással.

    Args:
        page: Oldal száma (1-től kezdődik)
        page_size: Oldalméret
        table_id: Opcionális szűrő - asztal ID
        status: Opcionális szűrő - foglalás státusz
        date_from: Opcionális szűrő - kezdő dátum
        date_to: Opcionális szűrő - záró dátum
        customer_phone: Opcionális szűrő - telefonszám
        customer_email: Opcionális szűrő - email
        db: Database session (dependency injection)

    Returns:
        ReservationListResponse: Foglalások listája metaadatokkal
    """
    skip = (page - 1) * page_size

    reservations, total = ReservationService.list_reservations(
        db=db,
        skip=skip,
        limit=page_size,
        table_id=table_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        customer_phone=customer_phone,
        customer_email=customer_email
    )

    return ReservationListResponse(
        items=[ReservationResponse.model_validate(r) for r in reservations],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Egyedi foglalás lekérdezése",
    description="""
    Egyedi foglalás lekérdezése ID alapján.

    **Használati esetek:**
    - Foglalás részleteinek megjelenítése
    - Foglalás szerkesztési form előtöltése
    - Foglalás állapotának ellenőrzése

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
    - Automatikus ütközésellenőrzés időpont vagy asztal módosításkor
    - Kapacitás ellenőrzés vendégszám vagy asztal módosításkor
    - Részleges módosítás támogatva (csak a megadott mezők változnak)

    **Módosítható mezők:**
    - table_id: Asztal megváltoztatása
    - customer_name, customer_phone, customer_email: Vendég adatok
    - start_time, duration_minutes: Időpont és időtartam
    - guest_count: Vendégszám
    - status: Foglalás státusza
    - notes: Megjegyzések

    **Visszatérési értékek:**
    - 200: Foglalás sikeresen módosítva
    - 404: Foglalás nem található
    - 400: Validációs hiba vagy ütközés
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
        HTTPException 400: Ha validációs hiba vagy ütközés történik
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


@router.delete(
    "/{reservation_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Foglalás törlése",
    description="""
    Foglalás törlése ID alapján.

    **Figyelem:**
    A törlés véglegesen eltávolítja a foglalást az adatbázisból.
    Ha csak le szeretnéd mondani a foglalást, használd a `/cancel` endpointot!

    **Visszatérési értékek:**
    - 200: Foglalás sikeresen törölve
    - 404: Foglalás nem található
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


@router.patch(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Foglalás lemondása",
    description="""
    Foglalás lemondása - státusz CANCELLED-re állítása.

    **Használat:**
    Ez a végpont nem törli a foglalást, csak lemondottá állítja.
    Így megmarad a foglalási előzmények között.

    **Visszatérési értékek:**
    - 200: Foglalás sikeresen lemondva
    - 404: Foglalás nem található
    """,
    response_description="Lemondott foglalás adatai",
)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    Foglalás lemondása.

    Args:
        reservation_id: Lemondandó foglalás azonosítója
        db: Database session (dependency injection)

    Returns:
        ReservationResponse: Lemondott foglalás adatai

    Raises:
        HTTPException 404: Ha a foglalás nem található
    """
    reservation = ReservationService.cancel_reservation(db=db, reservation_id=reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Foglalás (ID: {reservation_id}) nem található"
        )
    return ReservationResponse.model_validate(reservation)


@router.patch(
    "/{reservation_id}/status",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Foglalás státuszának módosítása",
    description="""
    Foglalás státuszának módosítása.

    **Lehetséges státuszok:**
    - PENDING: Függő (alapértelmezett új foglalásokhoz)
    - CONFIRMED: Megerősített
    - CANCELLED: Lemondott
    - COMPLETED: Teljesített

    **Használati esetek:**
    - Foglalás megerősítése (PENDING -> CONFIRMED)
    - Foglalás lezárása (CONFIRMED -> COMPLETED)
    - Foglalás lemondása (bármely státusz -> CANCELLED)

    **Visszatérési értékek:**
    - 200: Státusz sikeresen módosítva
    - 404: Foglalás nem található
    """,
    response_description="Módosított foglalás adatai",
)
def update_reservation_status(
    reservation_id: int,
    status_update: ReservationStatusUpdate,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """
    Foglalás státuszának módosítása.

    Args:
        reservation_id: Foglalás azonosítója
        status_update: Új státusz
        db: Database session (dependency injection)

    Returns:
        ReservationResponse: Módosított foglalás adatai

    Raises:
        HTTPException 404: Ha a foglalás nem található
    """
    reservation = ReservationService.get_reservation(db=db, reservation_id=reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Foglalás (ID: {reservation_id}) nem található"
        )

    reservation.status = status_update.status
    db.commit()
    db.refresh(reservation)

    return ReservationResponse.model_validate(reservation)
