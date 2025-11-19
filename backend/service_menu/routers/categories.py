"""
Category API Router - RESTful endpoints for Category Management
Module 0: Terméktörzs és Menü

Ez a modul tartalmazza a kategóriákhoz kapcsolódó FastAPI route-okat.
Használja a CategoryService-t az üzleti logika végrehajtásához.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.service_menu.database import get_db_connection
from backend.service_menu.models import Category
from backend.service_menu.services.category_service import CategoryService
from backend.service_menu.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)

# APIRouter létrehozása
router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={
        404: {"description": "Category not found"},
        400: {"description": "Bad request - validation or business logic error"},
    },
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Új kategória létrehozása",
    description="""
    Új kategória létrehozása a rendszerben.

    **Üzleti szabályok:**
    - A kategória neve egyedi kell legyen ugyanazon parent kategórián belül
    - Ha parent_id meg van adva, akkor a parent kategóriának léteznie kell
    - Root kategória esetén a parent_id None vagy null értékű

    **Visszatérési értékek:**
    - 201: Kategória sikeresen létrehozva
    - 404: Parent kategória nem található
    - 400: Validációs hiba vagy már létező név
    """,
    response_description="Újonnan létrehozott kategória adatai",
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db_connection),
) -> CategoryResponse:
    """
    Új kategória létrehozása.

    Args:
        category_data: Kategória adatok (név, leírás, parent_id, stb.)
        db: Database session (dependency injection)

    Returns:
        CategoryResponse: Létrehozott kategória adatai
    """
    return CategoryService.create_category(db=db, category_data=category_data)


@router.get(
    "",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Kategóriák listázása",
    description="""
    Kategóriák lekérdezése lapozással és opcionális szűréssel.

    **Lapozási paraméterek:**
    - skip: Kihagyott elemek száma (offset)
    - limit: Maximális visszaadott elemek száma (max 100)

    **Szűrési lehetőségek:**
    - parent_id: Ha nincs megadva, minden kategória visszaadásra kerül
    - parent_id = 0: Csak root kategóriák (amelyeknek nincs szülője)
    - parent_id = N: Csak az N azonosítójú kategória gyerekei

    **Visszatérési értékek:**
    - 200: Kategória lista sikeresen lekérdezve
    - 400: Hibás lapozási paraméterek
    """,
    response_description="Kategóriák listája lapozási információkkal",
)
def get_categories(
    skip: int = Query(0, ge=0, description="Kihagyott elemek száma (pagination offset)"),
    limit: int = Query(100, ge=1, le=100, description="Max. visszaadott elemek száma"),
    parent_id: Optional[int] = Query(
        None,
        description="Szűrés parent_id alapján. 0 = root kategóriák, None = összes kategória",
    ),
    db: Session = Depends(get_db_connection),
) -> CategoryListResponse:
    """
    Kategóriák listázása lapozással és szűréssel.

    Args:
        skip: Pagination offset (kihagyott elemek száma)
        limit: Pagination limit (max elemszám)
        parent_id: Opcionális szűrés parent_id alapján
        db: Database session (dependency injection)

    Returns:
        CategoryListResponse: Kategória lista metaadatokkal (total, page, page_size)
    """
    # Build query
    query = db.query(Category)

    # Szűrés parent_id alapján
    if parent_id is not None:
        if parent_id == 0:
            # Root kategóriák (nincs szülő)
            query = query.filter(Category.parent_id.is_(None))
        else:
            # Adott parent alatt lévő kategóriák
            query = query.filter(Category.parent_id == parent_id)

    # Összes elem száma a szűrés után
    total = query.count()

    # Lapozás és lekérdezés
    categories = query.offset(skip).limit(limit).all()

    # Explicit Pydantic konverzió a router szinten
    return CategoryListResponse(
        items=[CategoryResponse.model_validate(cat) for cat in categories],
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get(
    "/tree",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Kategória hierarchia fa struktúra",
    description="""
    Kategóriák hierarchikus fa struktúrában történő lekérdezése.

    **Használati esetek:**
    - Navigációs menü generálása
    - Hierarchikus kategória választó megjelenítése
    - Teljes kategória struktúra áttekintése

    **Paraméterek:**
    - root_id: Ha nincs megadva, minden root kategória és leszármazottai visszaadásra kerülnek
    - root_id = N: Az N azonosítójú kategória és annak leszármazottai

    **Visszatérési értékek:**
    - 200: Hierarchikus fa struktúra sikeresen lekérdezve
    """,
    response_description="Hierarchikus kategória fa (minden kategória tartalmazza a 'children' listát)",
)
def get_category_tree(
    root_id: Optional[int] = Query(
        None,
        description="Gyökér kategória ID (None = összes root kategória)",
    ),
    db: Session = Depends(get_db_connection),
) -> List[dict]:
    """
    Kategória hierarchia lekérdezése fa struktúrában.

    Args:
        root_id: Opcionális gyökér kategória ID
        db: Database session (dependency injection)

    Returns:
        List[dict]: Hierarchikus kategória fa ('children' mezőkkel)
    """
    return CategoryService.get_category_tree(db=db, root_id=root_id)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Egyedi kategória lekérdezése",
    description="""
    Egyedi kategória lekérdezése ID alapján.

    **Használati esetek:**
    - Kategória részleteinek megjelenítése
    - Szerkesztési form előtöltése
    - Kategória adatok validálása

    **Visszatérési értékek:**
    - 200: Kategória sikeresen lekérdezve
    - 404: Kategória nem található a megadott ID-val
    """,
    response_description="Kategória adatai",
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db_connection),
) -> CategoryResponse:
    """
    Egyedi kategória lekérdezése ID alapján.

    Args:
        category_id: Kategória azonosító
        db: Database session (dependency injection)

    Returns:
        CategoryResponse: Kategória adatai
    """
    return CategoryService.get_category(db=db, category_id=category_id)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Kategória módosítása",
    description="""
    Meglévő kategória módosítása ID alapján.

    **Üzleti szabályok:**
    - A kategória névnek egyedinek kell lennie az adott parent alatt
    - Parent kategória módosítása nem eredményezhet ciklikus hivatkozást
    - Nem lehet egy kategóriát saját magának vagy leszármazottjának beállítani parent-nek

    **Részleges módosítás (PATCH-szerű viselkedés):**
    - Csak a megadott mezők kerülnek módosításra
    - A nem megadott mezők értéke nem változik

    **Visszatérési értékek:**
    - 200: Kategória sikeresen módosítva
    - 404: Kategória vagy új parent nem található
    - 400: Validációs hiba, névütközés vagy ciklikus hivatkozás
    """,
    response_description="Módosított kategória adatai",
)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db_connection),
) -> CategoryResponse:
    """
    Kategória módosítása.

    Args:
        category_id: Módosítandó kategória azonosítója
        category_data: Módosítandó mezők (csak a megadott mezők változnak)
        db: Database session (dependency injection)

    Returns:
        CategoryResponse: Módosított kategória adatai
    """
    return CategoryService.update_category(
        db=db,
        category_id=category_id,
        category_data=category_data,
    )


@router.delete(
    "/{category_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Kategória törlése",
    description="""
    Kategória törlése ID alapján.

    **Törlési szabályok:**
    - Alapértelmezetten (force=False): A kategória csak akkor törölhető, ha nincs alkategóriája és terméke
    - Force mód (force=True): Rekurzívan törli az összes alkategóriát és NULL-ra állítja a kapcsolódó termékek kategóriáját

    **Visszatérési értékek:**
    - 200: Kategória sikeresen törölve
    - 404: Kategória nem található
    - 400: Vannak kapcsolódó elemek és force=False

    **Figyelem:**
    A force=True használata visszafordíthatatlan adatvesztést okozhat!
    """,
    response_description="Törlés megerősítése (message és deleted_id)",
)
def delete_category(
    category_id: int,
    force: bool = Query(
        False,
        description="Ha True, rekurzívan törli az alkategóriákat és NULL-ra állítja a termékek kategóriáját",
    ),
    db: Session = Depends(get_db_connection),
) -> dict:
    """
    Kategória törlése.

    Args:
        category_id: Törlendő kategória azonosítója
        force: Ha True, cascade törlés (alkategóriák + termék kapcsolatok)
        db: Database session (dependency injection)

    Returns:
        dict: Törlés megerősítő üzenet és a törölt ID
    """
    return CategoryService.delete_category(
        db=db,
        category_id=category_id,
        force=force,
    )
