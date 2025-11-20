"""
Allergen API Router - RESTful endpoints for Allergen Management
Module 0: Terméktörzs és Menü

Ez a modul tartalmazza az allergénekhez kapcsolódó FastAPI route-okat.
Használja az AllergenService-t az üzleti logika végrehajtásához.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.orm import Session

from backend.service_menu.database import get_db_connection
from backend.service_menu.services.allergen_service import AllergenService
from backend.service_menu.schemas import (
    AllergenCreate,
    AllergenUpdate,
    AllergenResponse,
    AllergenListResponse,
    ProductAllergenAssignment,
)

# APIRouter létrehozása
router = APIRouter(
    prefix="/allergens",
    tags=["allergens"],
    responses={
        404: {"description": "Allergen not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)


@router.post(
    "",
    response_model=AllergenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Új allergén létrehozása",
    description="""
    Új allergén létrehozása a rendszerben.

    **Üzleti szabályok:**
    - Az allergén kódja egyedi kell legyen (automatikusan nagybetűvé konvertálódik)
    - Név és kód megadása kötelező
    - Ikon URL megadása opcionális

    **Visszatérési értékek:**
    - 201: Allergén sikeresen létrehozva
    - 400: Validációs hiba vagy már létező kód
    """,
    response_description="Újonnan létrehozott allergén adatai",
)
def create_allergen(
    allergen_data: AllergenCreate,
    db: Session = Depends(get_db_connection),
) -> AllergenResponse:
    """
    Új allergén létrehozása.

    Args:
        allergen_data: Allergén adatok (code, name, icon_url)
        db: Database session (dependency injection)

    Returns:
        AllergenResponse: Létrehozott allergén adatai
    """
    return AllergenService.create_allergen(db=db, allergen_data=allergen_data)


@router.get(
    "",
    response_model=AllergenListResponse,
    status_code=status.HTTP_200_OK,
    summary="Allergének listázása",
    description="""
    Allergének lekérdezése lapozással.

    **Lapozási paraméterek:**
    - page: Oldalszám (1-től kezdődik, alapértelmezett: 1)
    - page_size: Elemek száma oldalanként (1-100, alapértelmezett: 20)

    **Visszatérési értékek:**
    - 200: Allergén lista sikeresen lekérdezve
    - 400: Hibás lapozási paraméterek
    """,
    response_description="Allergének listája lapozási információkkal",
)
def get_allergens(
    page: int = Query(1, ge=1, description="Oldalszám (1-től kezdődik)"),
    page_size: int = Query(20, ge=1, le=100, description="Elemek száma oldalanként"),
    db: Session = Depends(get_db_connection),
) -> AllergenListResponse:
    """
    Allergének lekérdezése lapozással.

    Args:
        page: Oldalszám
        page_size: Elemek száma oldalanként
        db: Database session (dependency injection)

    Returns:
        AllergenListResponse: Allergének listája lapozási metaadatokkal
    """
    return AllergenService.get_allergens(db=db, page=page, page_size=page_size)


@router.get(
    "/{allergen_id}",
    response_model=AllergenResponse,
    status_code=status.HTTP_200_OK,
    summary="Allergén lekérdezése ID alapján",
    description="""
    Egy adott allergén adatainak lekérdezése.

    **Visszatérési értékek:**
    - 200: Allergén adatok sikeresen lekérdezve
    - 404: Allergén nem található
    """,
    response_description="Allergén adatai",
)
def get_allergen(
    allergen_id: int = Path(..., description="Allergén azonosító"),
    db: Session = Depends(get_db_connection),
) -> AllergenResponse:
    """
    Allergén lekérdezése ID alapján.

    Args:
        allergen_id: Allergén azonosító
        db: Database session (dependency injection)

    Returns:
        AllergenResponse: Allergén adatai
    """
    return AllergenService.get_allergen(db=db, allergen_id=allergen_id)


@router.put(
    "/{allergen_id}",
    response_model=AllergenResponse,
    status_code=status.HTTP_200_OK,
    summary="Allergén módosítása",
    description="""
    Meglévő allergén adatainak módosítása.

    **Üzleti szabályok:**
    - Csak a megadott mezők kerülnek módosításra
    - Kód módosítása esetén ellenőrzésre kerül az egyediség

    **Visszatérési értékek:**
    - 200: Allergén sikeresen módosítva
    - 404: Allergén nem található
    - 400: Validációs hiba vagy kód ütközés
    """,
    response_description="Módosított allergén adatai",
)
def update_allergen(
    allergen_id: int = Path(..., description="Allergén azonosító"),
    allergen_data: AllergenUpdate = ...,
    db: Session = Depends(get_db_connection),
) -> AllergenResponse:
    """
    Allergén módosítása.

    Args:
        allergen_id: Allergén azonosító
        allergen_data: Módosítandó adatok
        db: Database session (dependency injection)

    Returns:
        AllergenResponse: Módosított allergén adatai
    """
    return AllergenService.update_allergen(
        db=db,
        allergen_id=allergen_id,
        allergen_data=allergen_data
    )


@router.delete(
    "/{allergen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Allergén törlése",
    description="""
    Allergén törlése a rendszerből.

    **Figyelem:**
    - A törlés automatikusan eltávolítja az allergén hozzárendeléseket is a termékekről
    - CASCADE törlés van beállítva az adatbázisban

    **Visszatérési értékek:**
    - 204: Allergén sikeresen törölve
    - 404: Allergén nem található
    """,
)
def delete_allergen(
    allergen_id: int = Path(..., description="Allergén azonosító"),
    db: Session = Depends(get_db_connection),
) -> None:
    """
    Allergén törlése.

    Args:
        allergen_id: Allergén azonosító
        db: Database session (dependency injection)
    """
    AllergenService.delete_allergen(db=db, allergen_id=allergen_id)
