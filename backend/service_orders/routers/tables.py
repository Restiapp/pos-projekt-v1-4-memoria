"""
Table API Router - RESTful endpoints for Table Management
Module 1: Rendeléskezelés és Asztalok

Ez a modul tartalmazza az asztalokhoz kapcsolódó FastAPI route-okat.
Használja a TableService-t az üzleti logika végrehajtásához.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.services.table_service import TableService
from backend.service_orders.schemas.table import (
    TableCreate,
    TableUpdate,
    TableResponse,
    TableListResponse,
    TableMoveRequest,
    TableMergeRequest,
)

# APIRouter létrehozása
router = APIRouter(
    prefix="/tables",
    tags=["tables"],
    responses={
        404: {"description": "Table not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)


@router.post(
    "",
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Új asztal létrehozása",
    description="""
    Új asztal létrehozása a rendszerben.

    **Üzleti szabályok:**
    - Az asztal száma (table_number) egyedi kell legyen
    - A position_x, position_y koordináták opcionálisak (térképes megjelenítéshez)
    - A capacity opcionális, de ha meg van adva, minimum 1 kell legyen

    **Visszatérési értékek:**
    - 201: Asztal sikeresen létrehozva
    - 400: Validációs hiba vagy már létező asztalszám
    """,
    response_description="Újonnan létrehozott asztal adatai",
)
def create_table(
    table_data: TableCreate,
    db: Session = Depends(get_db),
) -> TableResponse:
    """
    Új asztal létrehozása.

    Args:
        table_data: Asztal adatok (table_number, pozíció, kapacitás)
        db: Database session (dependency injection)

    Returns:
        TableResponse: Létrehozott asztal adatai

    Raises:
        HTTPException 400: Ha az asztalszám már létezik
    """
    try:
        table = TableService.create_table(db=db, table_data=table_data)
        return TableResponse.model_validate(table)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=TableListResponse,
    status_code=status.HTTP_200_OK,
    summary="Asztalok listázása",
    description="""
    Asztalok lekérdezése lapozással.

    **Lapozási paraméterek:**
    - page: Oldal száma (1-től kezdődik)
    - page_size: Oldalméret (max 100)

    **Visszatérési értékek:**
    - 200: Asztal lista sikeresen lekérdezve
    - 400: Hibás lapozási paraméterek
    """,
    response_description="Asztalok listája lapozási információkkal",
)
def get_tables(
    page: int = Query(1, ge=1, description="Oldal száma (1-től kezdődik)"),
    page_size: int = Query(20, ge=1, le=100, description="Oldalméret (max 100)"),
    db: Session = Depends(get_db),
) -> TableListResponse:
    """
    Asztalok listázása lapozással.

    Args:
        page: Oldal száma (1-től kezdődik)
        page_size: Oldalméret
        db: Database session (dependency injection)

    Returns:
        TableListResponse: Asztal lista metaadatokkal (total, page, page_size)
    """
    # Számítsuk ki a skip értéket a page alapján
    skip = (page - 1) * page_size

    tables, total = TableService.list_tables(db=db, skip=skip, limit=page_size)

    return TableListResponse(
        items=[TableResponse.model_validate(t) for t in tables],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/by-number/{table_number}",
    response_model=TableResponse,
    status_code=status.HTTP_200_OK,
    summary="Asztal lekérdezése asztalszám alapján",
    description="""
    Asztal lekérdezése asztalszám (table_number) alapján.

    **Használati esetek:**
    - QR kód alapú rendelés (asztalszám a kódban)
    - Gyors asztal keresés száma alapján
    - Asztal azonosítás felhasználóbarát azonosítóval

    **Visszatérési értékek:**
    - 200: Asztal sikeresen lekérdezve
    - 404: Asztal nem található a megadott számmal
    """,
    response_description="Asztal adatai",
)
def get_table_by_number(
    table_number: str,
    db: Session = Depends(get_db),
) -> TableResponse:
    """
    Asztal lekérdezése asztalszám alapján.

    Args:
        table_number: Asztal száma/azonosítója
        db: Database session (dependency injection)

    Returns:
        TableResponse: Asztal adatai

    Raises:
        HTTPException 404: Ha az asztal nem található
    """
    table = TableService.get_table_by_number(db=db, table_number=table_number)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asztal '{table_number}' nem található"
        )
    return TableResponse.model_validate(table)


@router.get(
    "/capacity/{min_capacity}",
    response_model=list[TableResponse],
    status_code=status.HTTP_200_OK,
    summary="Asztalok lekérdezése minimum kapacitás alapján",
    description="""
    Asztalok lekérdezése minimum kapacitás alapján.

    **Használati esetek:**
    - Megfelelő méretű asztal keresése vendégszám alapján
    - Asztal ajánlás foglaláshoz

    **Visszatérési értékek:**
    - 200: Asztal lista sikeresen lekérdezve
    """,
    response_description="Asztalok listája, amelyek kapacitása >= min_capacity",
)
def get_tables_by_capacity(
    min_capacity: int,
    db: Session = Depends(get_db),
) -> list[TableResponse]:
    """
    Asztalok lekérdezése minimum kapacitás alapján.

    Args:
        min_capacity: Minimum ülőhely kapacitás
        db: Database session (dependency injection)

    Returns:
        list[TableResponse]: Asztalok listája
    """
    tables = TableService.get_tables_with_capacity(db=db, min_capacity=min_capacity)
    return [TableResponse.model_validate(t) for t in tables]


@router.get(
    "/{table_id}",
    response_model=TableResponse,
    status_code=status.HTTP_200_OK,
    summary="Egyedi asztal lekérdezése",
    description="""
    Egyedi asztal lekérdezése ID alapján.

    **Használati esetek:**
    - Asztal részleteinek megjelenítése
    - Szerkesztési form előtöltése
    - Asztal adatok validálása

    **Visszatérési értékek:**
    - 200: Asztal sikeresen lekérdezve
    - 404: Asztal nem található a megadott ID-val
    """,
    response_description="Asztal adatai",
)
def get_table(
    table_id: int,
    db: Session = Depends(get_db),
) -> TableResponse:
    """
    Egyedi asztal lekérdezése ID alapján.

    Args:
        table_id: Asztal azonosító
        db: Database session (dependency injection)

    Returns:
        TableResponse: Asztal adatai

    Raises:
        HTTPException 404: Ha az asztal nem található
    """
    table = TableService.get_table(db=db, table_id=table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asztal (ID: {table_id}) nem található"
        )
    return TableResponse.model_validate(table)


@router.put(
    "/{table_id}",
    response_model=TableResponse,
    status_code=status.HTTP_200_OK,
    summary="Asztal módosítása",
    description="""
    Meglévő asztal módosítása ID alapján.

    **Üzleti szabályok:**
    - Az asztal számának egyedinek kell lennie
    - Pozíció koordináták opcionálisak
    - Kapacitás minimum 1 kell legyen, ha meg van adva

    **Részleges módosítás (PATCH-szerű viselkedés):**
    - Csak a megadott mezők kerülnek módosításra
    - A nem megadott mezők értéke nem változik

    **Visszatérési értékek:**
    - 200: Asztal sikeresen módosítva
    - 404: Asztal nem található
    - 400: Validációs hiba vagy asztalszám ütközés
    """,
    response_description="Módosított asztal adatai",
)
def update_table(
    table_id: int,
    table_data: TableUpdate,
    db: Session = Depends(get_db),
) -> TableResponse:
    """
    Asztal módosítása.

    Args:
        table_id: Módosítandó asztal azonosítója
        table_data: Módosítandó mezők (csak a megadott mezők változnak)
        db: Database session (dependency injection)

    Returns:
        TableResponse: Módosított asztal adatai

    Raises:
        HTTPException 404: Ha az asztal nem található
        HTTPException 400: Ha validációs hiba történik
    """
    try:
        table = TableService.update_table(db=db, table_id=table_id, table_data=table_data)
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asztal (ID: {table_id}) nem található"
            )
        return TableResponse.model_validate(table)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{table_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Asztal törlése",
    description="""
    Asztal törlése ID alapján.

    **Törlési szabályok:**
    - Az asztalhoz tartozó ülőhelyek (seats) automatikusan törlődnek (cascade)
    - Ha az asztalhoz rendelések tartoznak, azok orphan maradhatnak vagy hiba történik
      (függ a kapcsolat konfigurációtól)

    **Visszatérési értékek:**
    - 200: Asztal sikeresen törölve
    - 404: Asztal nem található

    **Figyelem:**
    Az asztal törlése visszafordíthatatlan és törli a kapcsolódó ülőhelyeket is!
    """,
    response_description="Törlés megerősítése (message és deleted_id)",
)
def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """
    Asztal törlése.

    Args:
        table_id: Törlendő asztal azonosítója
        db: Database session (dependency injection)

    Returns:
        dict: Törlés megerősítő üzenet és a törölt ID

    Raises:
        HTTPException 404: Ha az asztal nem található
    """
    success = TableService.delete_table(db=db, table_id=table_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asztal (ID: {table_id}) nem található"
        )

    return {
        "message": f"Asztal (ID: {table_id}) sikeresen törölve",
        "deleted_id": table_id
    }


@router.patch(
    "/{table_id}/move",
    response_model=TableResponse,
    status_code=status.HTTP_200_OK,
    summary="Asztal áthelyezése új szekcióba",
    description="""
    Asztal áthelyezése új szekcióba (V3.0 - Fázis 1).

    **Használati esetek:**
    - Asztal áthelyezése egy új területre (pl. Terasz -> Belső terem)
    - Szekciók dinamikus átrendezése
    - Fizikai elrendezés változásának követése

    **Üzleti szabályok:**
    - A szekció neve nem lehet üres
    - Az asztalnak léteznie kell

    **Visszatérési értékek:**
    - 200: Asztal sikeresen áthelyezve
    - 404: Asztal nem található
    - 400: Hibás szekció név
    """,
    response_description="Áthelyezett asztal adatai az új szekcióval",
)
def move_table(
    table_id: int,
    move_request: TableMoveRequest,
    db: Session = Depends(get_db),
) -> TableResponse:
    """
    Asztal áthelyezése új szekcióba.

    Args:
        table_id: Az áthelyezendő asztal azonosítója
        move_request: Új szekció adatai
        db: Database session (dependency injection)

    Returns:
        TableResponse: Áthelyezett asztal adatai

    Raises:
        HTTPException 404: Ha az asztal nem található
        HTTPException 400: Ha a szekció név hibás
    """
    try:
        table = TableService.move_table(
            db=db,
            table_id=table_id,
            new_section=move_request.new_section
        )
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asztal (ID: {table_id}) nem található"
            )
        return TableResponse.model_validate(table)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/merge",
    response_model=TableResponse,
    status_code=status.HTTP_200_OK,
    summary="Asztalok összevonása",
    description="""
    Asztalok összevonása (V3.0 - Fázis 1).

    **Használati esetek:**
    - Nagy csoportok kiszolgálása több asztal összevonásával
    - Rugalmas asztal konfigurációk létrehozása
    - Különálló asztalok ideiglenes egyesítése

    **Üzleti szabályok:**
    - Az elsődleges asztalnak léteznie kell
    - Minden másodlagos asztalnak léteznie kell
    - Az elsődleges asztal nem szerepelhet a másodlagos asztalok között
    - A másodlagos asztalok parent_table_id-ja az elsődleges asztal ID-jára lesz állítva

    **Visszatérési értékek:**
    - 200: Asztalok sikeresen összevonva
    - 404: Egyik asztal nem található
    - 400: Hibás egyesítési kérés
    """,
    response_description="Elsődleges asztal adatai az összevonás után",
)
def merge_tables(
    merge_request: TableMergeRequest,
    db: Session = Depends(get_db),
) -> TableResponse:
    """
    Asztalok összevonása.

    Args:
        merge_request: Összevonási kérés adatai (primary és secondary table IDs)
        db: Database session (dependency injection)

    Returns:
        TableResponse: Elsődleges asztal adatai

    Raises:
        HTTPException 404: Ha valamelyik asztal nem található
        HTTPException 400: Ha az egyesítési kérés hibás
    """
    try:
        primary_table = TableService.merge_tables(
            db=db,
            primary_table_id=merge_request.primary_table_id,
            secondary_table_ids=merge_request.secondary_table_ids
        )
        return TableResponse.model_validate(primary_table)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
