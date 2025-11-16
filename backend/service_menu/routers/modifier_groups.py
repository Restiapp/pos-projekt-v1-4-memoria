"""
Modifier Groups Router - API Endpoints
Module 0: Terméktörzs és Menü

Ez a router kezeli a ModifierGroup és Modifier entitásokkal kapcsolatos
API végpontokat, valamint a Product-ModifierGroup asszociációkat.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_menu.database import get_db_connection
from backend.service_menu.services.modifier_service import (
    ModifierService,
    ModifierServiceError,
    ModifierGroupNotFoundError,
    ModifierNotFoundError,
    ProductNotFoundError,
)
from backend.service_menu.schemas.modifier import (
    ModifierGroupCreate,
    ModifierGroupUpdate,
    ModifierGroupResponse,
    ModifierGroupWithModifiers,
    ModifierCreate,
    ModifierUpdate,
    ModifierResponse,
)


# ============================================================================
# Router Initialization
# ============================================================================

router = APIRouter(
    prefix="/api/v1",
    tags=["Modifier Groups & Modifiers"],
    responses={
        404: {"description": "Resource not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
)


# ============================================================================
# Exception Handlers
# ============================================================================

def handle_modifier_service_error(error: ModifierServiceError) -> HTTPException:
    """
    Centralizált exception handler a ModifierService hibákhoz.

    Args:
        error: ModifierServiceError vagy alosztályai

    Returns:
        HTTPException: Megfelelő HTTP státusz kóddal
    """
    if isinstance(error, ModifierGroupNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    elif isinstance(error, ModifierNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    elif isinstance(error, ProductNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    else:
        # Általános ModifierServiceError (pl. adatbázis hiba, duplikáció)
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# ============================================================================
# ModifierGroup CRUD Endpoints
# ============================================================================

@router.post(
    "/modifier-groups",
    response_model=ModifierGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new modifier group",
    description="""
    Új ModifierGroup létrehozása.

    **Példa**: "Zsemle típusa" csoport létrehozása kötelező egyválasztásos típussal.

    **Validáció**: max_selection >= min_selection
    """,
)
def create_modifier_group(
    modifier_group_data: ModifierGroupCreate,
    db: Session = Depends(get_db_connection),
):
    """
    Új ModifierGroup létrehozása.

    Args:
        modifier_group_data: ModifierGroup adatok
        db: Database session (injected)

    Returns:
        ModifierGroupResponse: Létrehozott modifier group

    Raises:
        HTTPException 400: Érvénytelen adatok vagy adatbázis hiba
    """
    try:
        return ModifierService.create_modifier_group(db, modifier_group_data)
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.get(
    "/modifier-groups",
    response_model=List[ModifierGroupResponse | ModifierGroupWithModifiers],
    summary="Get all modifier groups",
    description="""
    Összes ModifierGroup lekérdezése.

    **Pagination**: skip és limit paraméterekkel
    **include_modifiers**: Ha true, minden group összes modifier-ét is betölti
    """,
)
def get_all_modifier_groups(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to return"),
    include_modifiers: bool = Query(
        False,
        description="Include all modifiers in each group"
    ),
    db: Session = Depends(get_db_connection),
):
    """
    Összes ModifierGroup lekérdezése.

    Args:
        skip: Kihagyandó elemek száma (pagination)
        limit: Maximum visszaadott elemek száma
        include_modifiers: Ha True, betölti minden group összes modifier-ét
        db: Database session (injected)

    Returns:
        List[ModifierGroupResponse | ModifierGroupWithModifiers]
    """
    try:
        return ModifierService.get_all_modifier_groups(
            db,
            skip=skip,
            limit=limit,
            include_modifiers=include_modifiers
        )
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.get(
    "/modifier-groups/{group_id}",
    response_model=ModifierGroupResponse | ModifierGroupWithModifiers,
    summary="Get a modifier group by ID",
    description="""
    Egy adott ModifierGroup lekérdezése ID alapján.

    **include_modifiers**: Ha true, a group összes modifier-ét is betölti
    """,
)
def get_modifier_group(
    group_id: int,
    include_modifiers: bool = Query(
        False,
        description="Include all modifiers in the group"
    ),
    db: Session = Depends(get_db_connection),
):
    """
    ModifierGroup lekérdezése ID alapján.

    Args:
        group_id: Modifier group azonosító
        include_modifiers: Ha True, betölti a group összes modifier-ét
        db: Database session (injected)

    Returns:
        ModifierGroupResponse vagy ModifierGroupWithModifiers

    Raises:
        HTTPException 404: Ha nem található a group
    """
    try:
        return ModifierService.get_modifier_group_by_id(
            db,
            group_id,
            include_modifiers=include_modifiers
        )
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.put(
    "/modifier-groups/{group_id}",
    response_model=ModifierGroupResponse,
    summary="Update a modifier group",
    description="""
    ModifierGroup módosítása.

    **Részleges frissítés**: Csak a megadott mezőket frissíti
    """,
)
def update_modifier_group(
    group_id: int,
    update_data: ModifierGroupUpdate,
    db: Session = Depends(get_db_connection),
):
    """
    ModifierGroup módosítása.

    Args:
        group_id: Modifier group azonosító
        update_data: Módosítandó adatok
        db: Database session (injected)

    Returns:
        ModifierGroupResponse: Frissített modifier group

    Raises:
        HTTPException 404: Ha nem található a group
        HTTPException 400: Adatbázis hiba esetén
    """
    try:
        return ModifierService.update_modifier_group(db, group_id, update_data)
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.delete(
    "/modifier-groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a modifier group",
    description="""
    ModifierGroup törlése.

    **Cascade**: A group összes modifier-ét is törli
    """,
)
def delete_modifier_group(
    group_id: int,
    db: Session = Depends(get_db_connection),
):
    """
    ModifierGroup törlése.

    Args:
        group_id: Modifier group azonosító
        db: Database session (injected)

    Raises:
        HTTPException 404: Ha nem található a group
        HTTPException 400: Adatbázis hiba esetén
    """
    try:
        ModifierService.delete_modifier_group(db, group_id)
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


# ============================================================================
# Modifier CRUD Endpoints
# ============================================================================

@router.post(
    "/modifiers",
    response_model=ModifierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new modifier",
    description="""
    Új Modifier létrehozása egy ModifierGroup-ban.

    **Példa**: "Szezámos zsemle" modifier létrehozása a "Zsemle típusa" csoportban.

    **Validáció**: A parent ModifierGroup-nak léteznie kell
    """,
)
def create_modifier(
    modifier_data: ModifierCreate,
    db: Session = Depends(get_db_connection),
):
    """
    Új Modifier létrehozása.

    Args:
        modifier_data: Modifier adatok
        db: Database session (injected)

    Returns:
        ModifierResponse: Létrehozott modifier

    Raises:
        HTTPException 404: Ha nem található a parent group
        HTTPException 400: Adatbázis hiba esetén
    """
    try:
        return ModifierService.create_modifier(db, modifier_data)
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.get(
    "/modifiers/{modifier_id}",
    response_model=ModifierResponse,
    summary="Get a modifier by ID",
    description="Egy adott Modifier lekérdezése ID alapján.",
)
def get_modifier(
    modifier_id: int,
    db: Session = Depends(get_db_connection),
):
    """
    Modifier lekérdezése ID alapján.

    Args:
        modifier_id: Modifier azonosító
        db: Database session (injected)

    Returns:
        ModifierResponse: A keresett modifier

    Raises:
        HTTPException 404: Ha nem található a modifier
    """
    try:
        return ModifierService.get_modifier_by_id(db, modifier_id)
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.get(
    "/modifier-groups/{group_id}/modifiers",
    response_model=List[ModifierResponse],
    summary="Get all modifiers in a group",
    description="""
    Egy adott ModifierGroup összes Modifier-ének lekérdezése.

    **Pagination**: skip és limit paraméterekkel
    """,
)
def get_modifiers_by_group(
    group_id: int,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to return"),
    db: Session = Depends(get_db_connection),
):
    """
    Egy adott ModifierGroup összes Modifier-ének lekérdezése.

    Args:
        group_id: Modifier group azonosító
        skip: Kihagyandó elemek száma
        limit: Maximum visszaadott elemek száma
        db: Database session (injected)

    Returns:
        List[ModifierResponse]: Lista a modifierekkel

    Raises:
        HTTPException 404: Ha nem található a group
    """
    try:
        return ModifierService.get_modifiers_by_group(
            db,
            group_id,
            skip=skip,
            limit=limit
        )
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.put(
    "/modifiers/{modifier_id}",
    response_model=ModifierResponse,
    summary="Update a modifier",
    description="""
    Modifier módosítása.

    **Részleges frissítés**: Csak a megadott mezőket frissíti
    """,
)
def update_modifier(
    modifier_id: int,
    update_data: ModifierUpdate,
    db: Session = Depends(get_db_connection),
):
    """
    Modifier módosítása.

    Args:
        modifier_id: Modifier azonosító
        update_data: Módosítandó adatok
        db: Database session (injected)

    Returns:
        ModifierResponse: Frissített modifier

    Raises:
        HTTPException 404: Ha nem található a modifier vagy az új parent group
        HTTPException 400: Adatbázis hiba esetén
    """
    try:
        return ModifierService.update_modifier(db, modifier_id, update_data)
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.delete(
    "/modifiers/{modifier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a modifier",
    description="Modifier törlése.",
)
def delete_modifier(
    modifier_id: int,
    db: Session = Depends(get_db_connection),
):
    """
    Modifier törlése.

    Args:
        modifier_id: Modifier azonosító
        db: Database session (injected)

    Raises:
        HTTPException 404: Ha nem található a modifier
        HTTPException 400: Adatbázis hiba esetén
    """
    try:
        ModifierService.delete_modifier(db, modifier_id)
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


# ============================================================================
# Product-ModifierGroup Association Endpoints
# ============================================================================

@router.post(
    "/products/{product_id}/modifier-groups/{group_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Associate modifier group with product",
    description="""
    ModifierGroup hozzárendelése egy Product-hoz.

    **Példa**: A "Hamburger" termékhez hozzárendeljük a "Zsemle típusa" csoportot.

    **Validáció**:
    - A terméknek és a modifier group-nak léteznie kell
    - Az asszociáció nem lehet duplikált
    """,
    response_model=dict,
)
def associate_modifier_group_to_product(
    product_id: int,
    group_id: int,
    db: Session = Depends(get_db_connection),
):
    """
    ModifierGroup hozzárendelése egy Product-hoz.

    Args:
        product_id: Termék azonosító
        group_id: ModifierGroup azonosító
        db: Database session (injected)

    Returns:
        dict: Success message

    Raises:
        HTTPException 404: Ha nem található a termék vagy a modifier group
        HTTPException 400: Ha már létezik az asszociáció vagy adatbázis hiba
    """
    try:
        ModifierService.associate_modifier_group_to_product(
            db,
            product_id,
            group_id
        )
        return {
            "message": f"ModifierGroup {group_id} successfully associated with Product {product_id}"
        }
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.delete(
    "/products/{product_id}/modifier-groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove modifier group from product",
    description="""
    ModifierGroup eltávolítása egy Product-ból.

    **Validáció**: Az asszociációnak léteznie kell
    """,
)
def remove_modifier_group_from_product(
    product_id: int,
    group_id: int,
    db: Session = Depends(get_db_connection),
):
    """
    ModifierGroup eltávolítása egy Product-ból.

    Args:
        product_id: Termék azonosító
        group_id: ModifierGroup azonosító
        db: Database session (injected)

    Raises:
        HTTPException 404: Ha nem található a termék vagy a modifier group
        HTTPException 400: Ha nincs asszociáció vagy adatbázis hiba
    """
    try:
        ModifierService.remove_modifier_group_from_product(
            db,
            product_id,
            group_id
        )
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)


@router.get(
    "/products/{product_id}/modifier-groups",
    response_model=List[ModifierGroupResponse | ModifierGroupWithModifiers],
    summary="Get modifier groups for product",
    description="""
    Egy termékhez tartozó összes ModifierGroup lekérdezése.

    **include_modifiers**: Ha true, minden group összes modifier-ét is betölti.
    Ez hasznos rendelés összeállításához.
    """,
)
def get_modifier_groups_by_product(
    product_id: int,
    include_modifiers: bool = Query(
        False,
        description="Include all modifiers in each group"
    ),
    db: Session = Depends(get_db_connection),
):
    """
    Egy termékhez tartozó összes ModifierGroup lekérdezése.

    Args:
        product_id: Termék azonosító
        include_modifiers: Ha True, betölti minden group összes modifier-ét
        db: Database session (injected)

    Returns:
        List[ModifierGroupResponse | ModifierGroupWithModifiers]

    Raises:
        HTTPException 404: Ha nem található a termék
    """
    try:
        return ModifierService.get_modifier_groups_by_product(
            db,
            product_id,
            include_modifiers=include_modifiers
        )
    except ModifierServiceError as e:
        raise handle_modifier_service_error(e)
