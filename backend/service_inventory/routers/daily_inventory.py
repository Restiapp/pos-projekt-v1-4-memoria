"""
Daily Inventory API Router - RESTful endpoints for Daily Inventory Management
Module 5: Készletkezelés

Ez a modul tartalmazza a napi leltárhoz (daily inventory) kapcsolódó FastAPI route-okat.
Használja a DailyInventoryService-t az üzleti logika végrehajtásához.

Fő funkciók:
- Leltárívek (sheets/sablonok) kezelése (CRUD)
- Napi leltárszámlálások (counts) kezelése (CRUD)
- Listázás szűréssel és lapozással
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.service_inventory.models.database import get_db
from backend.service_inventory.services.daily_inventory_service import DailyInventoryService
from backend.service_inventory.schemas.daily_inventory import (
    DailyInventorySheetCreate,
    DailyInventorySheetUpdate,
    DailyInventorySheetResponse,
    DailyInventorySheetDetailResponse,
    DailyInventorySheetListResponse,
    DailyInventoryCountCreate,
    DailyInventoryCountUpdate,
    DailyInventoryCountResponse,
    DailyInventoryCountDetailResponse,
    DailyInventoryCountListResponse,
)

# APIRouter létrehozása a Daily Inventory Sheet-ekhez
sheet_router = APIRouter(
    prefix="/inventory/daily-sheets",
    tags=["daily-inventory-sheets"],
    responses={
        404: {"description": "Daily inventory sheet not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)

# APIRouter létrehozása a Daily Inventory Count-okhoz
count_router = APIRouter(
    prefix="/inventory/daily-counts",
    tags=["daily-inventory-counts"],
    responses={
        404: {"description": "Daily inventory count not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)


# ===== Daily Inventory Sheet Endpoints =====

@sheet_router.post(
    "",
    response_model=DailyInventorySheetDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Új leltárív (sablon) létrehozása",
    description="""
    Új napi leltárív (sablon/template) létrehozása.

    **Üzleti szabályok:**
    - A leltárív neve egyedi kell legyen
    - Opcionálisan megadhatók az inventory item ID-k, amelyek ebben a leltárban szerepelnek
    - Ha inventory_item_ids van megadva, minden ID-nek létező inventory item-nek kell lennie

    **Használati esetek:**
    - "Napi Karton - Reggel" sablon létrehozása a reggeli leltározáshoz
    - "Napi Karton - Este" sablon létrehozása az esti leltározáshoz
    - "Heti Raktárleltár" sablon létrehozása

    **Visszatérési értékek:**
    - 201: Leltárív sikeresen létrehozva
    - 400: Már létező név vagy hibás inventory_item_id
    - 404: Valamelyik inventory_item_id nem található
    """,
    response_description="Újonnan létrehozott leltárív adatai",
)
def create_daily_inventory_sheet(
    sheet_data: DailyInventorySheetCreate,
    db: Session = Depends(get_db),
) -> DailyInventorySheetDetailResponse:
    """
    Új leltárív (sablon) létrehozása.

    Args:
        sheet_data: Leltárív adatok (név, inventory item ID-k)
        db: Database session (dependency injection)

    Returns:
        DailyInventorySheetDetailResponse: Létrehozott leltárív adatai
    """
    return DailyInventoryService.create_sheet(db=db, sheet_data=sheet_data)


@sheet_router.get(
    "",
    response_model=DailyInventorySheetListResponse,
    status_code=status.HTTP_200_OK,
    summary="Leltárívek listázása",
    description="""
    Napi leltárívek (sablonok) lekérdezése lapozással.

    **Lapozási paraméterek:**
    - skip: Kihagyott elemek száma (offset)
    - limit: Maximális visszaadott elemek száma (max 100)

    **Visszatérési értékek:**
    - 200: Leltárívek listája sikeresen lekérdezve
    - 400: Hibás lapozási paraméterek
    """,
    response_description="Leltárívek listája lapozási információkkal",
)
def get_daily_inventory_sheets(
    skip: int = Query(0, ge=0, description="Kihagyott elemek száma (pagination offset)"),
    limit: int = Query(100, ge=1, le=100, description="Max. visszaadott elemek száma"),
    db: Session = Depends(get_db),
) -> DailyInventorySheetListResponse:
    """
    Leltárívek listázása lapozással.

    Args:
        skip: Pagination offset (kihagyott elemek száma)
        limit: Pagination limit (max elemszám)
        db: Database session (dependency injection)

    Returns:
        DailyInventorySheetListResponse: Leltárív lista metaadatokkal
    """
    return DailyInventoryService.get_sheets(db=db, skip=skip, limit=limit)


@sheet_router.get(
    "/{sheet_id}",
    response_model=DailyInventorySheetDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Egyedi leltárív lekérdezése",
    description="""
    Egyedi leltárív lekérdezése ID alapján.

    **Használati esetek:**
    - Leltárív részleteinek megjelenítése
    - Szerkesztési form előtöltése
    - Leltárív adatok és kapcsolódó inventory itemek lekérdezése

    **Visszatérési értékek:**
    - 200: Leltárív sikeresen lekérdezve
    - 404: Leltárív nem található a megadott ID-val
    """,
    response_description="Leltárív adatai a kapcsolódó inventory item ID-kkal",
)
def get_daily_inventory_sheet(
    sheet_id: int,
    include_items: bool = Query(
        True,
        description="Ha True, a válasz tartalmazza az inventory_item_ids listát",
    ),
    db: Session = Depends(get_db),
) -> DailyInventorySheetDetailResponse:
    """
    Egyedi leltárív lekérdezése ID alapján.

    Args:
        sheet_id: Leltárív azonosító
        include_items: Ha True, a response tartalmazza az inventory item ID-kat
        db: Database session (dependency injection)

    Returns:
        DailyInventorySheetDetailResponse: Leltárív adatai
    """
    return DailyInventoryService.get_sheet(
        db=db,
        sheet_id=sheet_id,
        include_items=include_items,
    )


@sheet_router.put(
    "/{sheet_id}",
    response_model=DailyInventorySheetDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Leltárív módosítása",
    description="""
    Meglévő leltárív módosítása ID alapján.

    **Üzleti szabályok:**
    - A leltárív névnek egyedinek kell lennie
    - Az inventory_item_ids frissítésekor minden ID-nek létező item-nek kell lennie

    **Részleges módosítás (PATCH-szerű viselkedés):**
    - Csak a megadott mezők kerülnek módosításra
    - A nem megadott mezők értéke nem változik

    **Visszatérési értékek:**
    - 200: Leltárív sikeresen módosítva
    - 404: Leltárív vagy inventory item nem található
    - 400: Validációs hiba vagy névütközés
    """,
    response_description="Módosított leltárív adatai",
)
def update_daily_inventory_sheet(
    sheet_id: int,
    sheet_data: DailyInventorySheetUpdate,
    db: Session = Depends(get_db),
) -> DailyInventorySheetDetailResponse:
    """
    Leltárív módosítása.

    Args:
        sheet_id: Módosítandó leltárív azonosítója
        sheet_data: Módosítandó mezők
        db: Database session (dependency injection)

    Returns:
        DailyInventorySheetDetailResponse: Módosított leltárív adatai
    """
    return DailyInventoryService.update_sheet(
        db=db,
        sheet_id=sheet_id,
        sheet_data=sheet_data,
    )


@sheet_router.delete(
    "/{sheet_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Leltárív törlése",
    description="""
    Leltárív törlése ID alapján.

    **Törlési szabályok:**
    - Alapértelmezetten (force=False): A leltárív csak akkor törölhető, ha nincs kapcsolódó count
    - Force mód (force=True): Cascade törli az összes kapcsolódó count rekordot is

    **Visszatérési értékek:**
    - 200: Leltárív sikeresen törölve
    - 404: Leltárív nem található
    - 400: Vannak kapcsolódó count-ok és force=False

    **Figyelem:**
    A force=True használata visszafordíthatatlan adatvesztést okozhat!
    """,
    response_description="Törlés megerősítése (message és deleted_id)",
)
def delete_daily_inventory_sheet(
    sheet_id: int,
    force: bool = Query(
        False,
        description="Ha True, törli a kapcsolódó count rekordokat is (cascade)",
    ),
    db: Session = Depends(get_db),
) -> dict:
    """
    Leltárív törlése.

    Args:
        sheet_id: Törlendő leltárív azonosítója
        force: Ha True, cascade törlés (count rekordok)
        db: Database session (dependency injection)

    Returns:
        dict: Törlés megerősítő üzenet és a törölt ID
    """
    return DailyInventoryService.delete_sheet(
        db=db,
        sheet_id=sheet_id,
        force=force,
    )


# ===== Daily Inventory Count Endpoints =====

@count_router.post(
    "",
    response_model=DailyInventoryCountDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Új leltárszámlálás rögzítése",
    description="""
    Új napi leltárszámlálás létrehozása.

    **Üzleti szabályok:**
    - A sheet_id-nak létező leltárívnek kell lennie
    - A count_items lista tartalmazza az egyes inventory itemek számlált mennyiségét
    - A counts mező automatikusan generálódik a count_items-ből (JSONB formátumban)

    **Használati esetek:**
    - Napi reggeli leltárszámlálás rögzítése
    - Napi esti leltárszámlálás rögzítése
    - Ad-hoc leltárszámlálás rögzítése

    **Visszatérési értékek:**
    - 201: Leltárszámlálás sikeresen rögzítve
    - 404: sheet_id nem található
    - 400: Validációs hiba
    """,
    response_description="Újonnan létrehozott leltárszámlálás adatai",
)
def create_daily_inventory_count(
    count_data: DailyInventoryCountCreate,
    db: Session = Depends(get_db),
) -> DailyInventoryCountDetailResponse:
    """
    Új leltárszámlálás rögzítése.

    Args:
        count_data: Leltárszámlálás adatok (sheet_id, dátum, employee_id, count_items)
        db: Database session (dependency injection)

    Returns:
        DailyInventoryCountDetailResponse: Létrehozott leltárszámlálás adatai
    """
    return DailyInventoryService.create_count(db=db, count_data=count_data)


@count_router.get(
    "",
    response_model=DailyInventoryCountListResponse,
    status_code=status.HTTP_200_OK,
    summary="Leltárszámlálások listázása",
    description="""
    Napi leltárszámlálások lekérdezése lapozással és szűréssel.

    **Lapozási paraméterek:**
    - skip: Kihagyott elemek száma (offset)
    - limit: Maximális visszaadott elemek száma (max 100)

    **Szűrési lehetőségek:**
    - sheet_id: Szűrés leltárív alapján
    - count_date: Szűrés dátum alapján

    **Rendezés:**
    - A leltárszámlálások dátum szerint csökkenő sorrendben (legújabb először)

    **Visszatérési értékek:**
    - 200: Leltárszámlálások listája sikeresen lekérdezve
    - 400: Hibás lapozási paraméterek
    """,
    response_description="Leltárszámlálások listája lapozási információkkal",
)
def get_daily_inventory_counts(
    skip: int = Query(0, ge=0, description="Kihagyott elemek száma (pagination offset)"),
    limit: int = Query(100, ge=1, le=100, description="Max. visszaadott elemek száma"),
    sheet_id: Optional[int] = Query(None, description="Szűrés sheet_id alapján"),
    count_date: Optional[date] = Query(None, description="Szűrés dátum alapján"),
    db: Session = Depends(get_db),
) -> DailyInventoryCountListResponse:
    """
    Leltárszámlálások listázása lapozással és szűréssel.

    Args:
        skip: Pagination offset (kihagyott elemek száma)
        limit: Pagination limit (max elemszám)
        sheet_id: Opcionális szűrés sheet_id alapján
        count_date: Opcionális szűrés dátum alapján
        db: Database session (dependency injection)

    Returns:
        DailyInventoryCountListResponse: Leltárszámlálás lista metaadatokkal
    """
    return DailyInventoryService.get_counts(
        db=db,
        skip=skip,
        limit=limit,
        sheet_id=sheet_id,
        count_date=count_date,
    )


@count_router.get(
    "/{count_id}",
    response_model=DailyInventoryCountDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Egyedi leltárszámlálás lekérdezése",
    description="""
    Egyedi leltárszámlálás lekérdezése ID alapján.

    **Használati esetek:**
    - Leltárszámlálás részleteinek megjelenítése
    - Szerkesztési form előtöltése
    - Számlált adatok lekérdezése (JSONB formátumban vagy strukturált listában)

    **Visszatérési értékek:**
    - 200: Leltárszámlálás sikeresen lekérdezve
    - 404: Leltárszámlálás nem található a megadott ID-val
    """,
    response_description="Leltárszámlálás adatai",
)
def get_daily_inventory_count(
    count_id: int,
    include_detail: bool = Query(
        True,
        description="Ha True, a válasz tartalmazza a count_items_detail strukturált listát",
    ),
    db: Session = Depends(get_db),
) -> DailyInventoryCountDetailResponse:
    """
    Egyedi leltárszámlálás lekérdezése ID alapján.

    Args:
        count_id: Leltárszámlálás azonosító
        include_detail: Ha True, a response tartalmazza a count_items_detail-t
        db: Database session (dependency injection)

    Returns:
        DailyInventoryCountDetailResponse: Leltárszámlálás adatai
    """
    return DailyInventoryService.get_count(
        db=db,
        count_id=count_id,
        include_detail=include_detail,
    )


@count_router.put(
    "/{count_id}",
    response_model=DailyInventoryCountDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Leltárszámlálás módosítása",
    description="""
    Meglévő leltárszámlálás módosítása ID alapján.

    **Üzleti szabályok:**
    - Ha sheet_id módosul, az új sheet_id-nak létező leltárívnek kell lennie
    - A count_items módosítása esetén az új adatok felülírják a meglévőket

    **Részleges módosítás (PATCH-szerű viselkedés):**
    - Csak a megadott mezők kerülnek módosításra
    - A nem megadott mezők értéke nem változik

    **Visszatérési értékek:**
    - 200: Leltárszámlálás sikeresen módosítva
    - 404: Leltárszámlálás vagy sheet nem található
    - 400: Validációs hiba
    """,
    response_description="Módosított leltárszámlálás adatai",
)
def update_daily_inventory_count(
    count_id: int,
    count_data: DailyInventoryCountUpdate,
    db: Session = Depends(get_db),
) -> DailyInventoryCountDetailResponse:
    """
    Leltárszámlálás módosítása.

    Args:
        count_id: Módosítandó leltárszámlálás azonosítója
        count_data: Módosítandó mezők
        db: Database session (dependency injection)

    Returns:
        DailyInventoryCountDetailResponse: Módosított leltárszámlálás adatai
    """
    return DailyInventoryService.update_count(
        db=db,
        count_id=count_id,
        count_data=count_data,
    )


@count_router.delete(
    "/{count_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Leltárszámlálás törlése",
    description="""
    Leltárszámlálás törlése ID alapján.

    **Törlési szabályok:**
    - A törlés egyszerű, nincs cascade törlés (a leltárszámlálásnak nincs további függősége)

    **Visszatérési értékek:**
    - 200: Leltárszámlálás sikeresen törölve
    - 404: Leltárszámlálás nem található
    - 400: Adatbázis integritási hiba
    """,
    response_description="Törlés megerősítése (message és deleted_id)",
)
def delete_daily_inventory_count(
    count_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """
    Leltárszámlálás törlése.

    Args:
        count_id: Törlendő leltárszámlálás azonosítója
        db: Database session (dependency injection)

    Returns:
        dict: Törlés megerősítő üzenet és a törölt ID
    """
    return DailyInventoryService.delete_count(db=db, count_id=count_id)


# Fő daily_inventory_router az összes endpoint-tal
# Ez kerül exportálásra a __init__.py-ban
daily_inventory_router = APIRouter()
daily_inventory_router.include_router(sheet_router)
daily_inventory_router.include_router(count_router)
