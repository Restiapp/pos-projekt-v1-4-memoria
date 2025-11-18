"""
Asset Router - Tárgyi Eszközök API végpontok
Module 8: Admin - Asset Management (V3.0 Phase 3.2)

Ez a router felelős a tárgyi eszközök kezeléséért:
- Eszközcsoportok (AssetGroup) CRUD műveletek
- Eszközök (Asset) CRUD műveletek
- Eszköz szervizek (AssetService) kezelése
"""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.service_admin.models.database import get_db
from backend.service_admin.models.employee import Employee
from backend.service_admin.services.asset_service import AssetManagementService
from backend.service_admin.schemas.asset import (
    AssetGroupCreate,
    AssetGroupUpdate,
    AssetGroupResponse,
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetServiceCreate,
    AssetServiceUpdate,
    AssetServiceResponse
)
from backend.service_admin.dependencies import require_permission, get_current_user


# ============================================================================
# Router Initialization
# ============================================================================

asset_router = APIRouter(
    prefix="/assets",
    tags=["Assets"]
)


# ============================================================================
# Dependencies
# ============================================================================

def get_asset_service(db: Session = Depends(get_db)) -> AssetManagementService:
    """
    Dependency injection az AssetManagementService-hez.

    Args:
        db: SQLAlchemy Session dependency

    Returns:
        AssetManagementService: Inicializált service instance
    """
    return AssetManagementService(db)


# ============================================================================
# Asset Group Endpoints (Eszközcsoportok)
# ============================================================================

@asset_router.post(
    "/groups",
    response_model=AssetGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Eszközcsoport létrehozása",
    description="Új eszközcsoport létrehozása.",
    dependencies=[Depends(require_permission("assets:manage"))]
)
async def create_asset_group(
    request: AssetGroupCreate,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> AssetGroupResponse:
    """
    Új eszközcsoport létrehozása.

    **Jogosultság:** `assets:manage`

    Args:
        request: Eszközcsoport adatok (AssetGroupCreate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        AssetGroupResponse: Létrehozott eszközcsoport adatai

    Raises:
        HTTPException 400: Ha a név már létezik
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset_group = service.create_asset_group(
            name=request.name,
            description=request.description,
            depreciation_rate=request.depreciation_rate,
            expected_lifetime_years=request.expected_lifetime_years,
            is_active=request.is_active or True
        )

        return AssetGroupResponse.model_validate(asset_group)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszközcsoport létrehozása során: {str(e)}"
        )


@asset_router.get(
    "/groups",
    response_model=List[AssetGroupResponse],
    summary="Eszközcsoportok listázása",
    description="Eszközcsoportok lekérdezése szűrési feltételekkel.",
    dependencies=[Depends(require_permission("assets:view"))]
)
async def list_asset_groups(
    is_active: Optional[bool] = Query(None, description="Aktív státusz szűrő"),
    limit: int = Query(100, ge=1, le=500, description="Maximum eredmények száma"),
    offset: int = Query(0, ge=0, description="Lapozási eltolás"),
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> List[AssetGroupResponse]:
    """
    Eszközcsoportok listázása.

    **Jogosultság:** `assets:view`

    Args:
        is_active: Aktív státusz szűrő (opcionális)
        limit: Maximum eredmények száma
        offset: Lapozási eltolás
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        List[AssetGroupResponse]: Eszközcsoportok listája

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset_groups = service.get_asset_groups(
            is_active=is_active,
            limit=limit,
            offset=offset
        )

        return [AssetGroupResponse.model_validate(g) for g in asset_groups]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszközcsoportok lekérdezése során: {str(e)}"
        )


@asset_router.get(
    "/groups/{group_id}",
    response_model=AssetGroupResponse,
    summary="Eszközcsoport részletei",
    description="Egy adott eszközcsoport részletes adatainak lekérdezése.",
    dependencies=[Depends(require_permission("assets:view"))]
)
async def get_asset_group(
    group_id: int,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> AssetGroupResponse:
    """
    Eszközcsoport részleteinek lekérdezése.

    **Jogosultság:** `assets:view`

    Args:
        group_id: Eszközcsoport azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        AssetGroupResponse: Eszközcsoport adatai

    Raises:
        HTTPException 404: Ha az eszközcsoport nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset_group = service.get_asset_group_by_id(group_id)

        if not asset_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Eszközcsoport nem található: {group_id}"
            )

        return AssetGroupResponse.model_validate(asset_group)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszközcsoport lekérdezése során: {str(e)}"
        )


@asset_router.patch(
    "/groups/{group_id}",
    response_model=AssetGroupResponse,
    summary="Eszközcsoport frissítése",
    description="Meglévő eszközcsoport adatainak frissítése.",
    dependencies=[Depends(require_permission("assets:manage"))]
)
async def update_asset_group(
    group_id: int,
    request: AssetGroupUpdate,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> AssetGroupResponse:
    """
    Eszközcsoport frissítése.

    **Jogosultság:** `assets:manage`

    Args:
        group_id: Eszközcsoport azonosító
        request: Frissítési adatok (AssetGroupUpdate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        AssetGroupResponse: Frissített eszközcsoport adatai

    Raises:
        HTTPException 400: Ha a név már létezik vagy az eszközcsoport nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset_group = service.update_asset_group(
            group_id=group_id,
            name=request.name,
            description=request.description,
            depreciation_rate=request.depreciation_rate,
            expected_lifetime_years=request.expected_lifetime_years,
            is_active=request.is_active
        )

        return AssetGroupResponse.model_validate(asset_group)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszközcsoport frissítése során: {str(e)}"
        )


@asset_router.delete(
    "/groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eszközcsoport törlése",
    description="Eszközcsoport törlése (soft delete).",
    dependencies=[Depends(require_permission("assets:manage"))]
)
async def delete_asset_group(
    group_id: int,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
):
    """
    Eszközcsoport törlése (soft delete).

    **Jogosultság:** `assets:manage`

    Args:
        group_id: Eszközcsoport azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Raises:
        HTTPException 400: Ha az eszközcsoport nem törölhető (van hozzá eszköz)
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        service.delete_asset_group(group_id)
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszközcsoport törlése során: {str(e)}"
        )


# ============================================================================
# Asset Endpoints (Eszközök)
# ============================================================================

@asset_router.post(
    "",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Eszköz létrehozása",
    description="Új eszköz létrehozása.",
    dependencies=[Depends(require_permission("assets:manage"))]
)
async def create_asset(
    request: AssetCreate,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> AssetResponse:
    """
    Új eszköz létrehozása.

    **Jogosultság:** `assets:manage`

    Args:
        request: Eszköz adatok (AssetCreate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        AssetResponse: Létrehozott eszköz adatai

    Raises:
        HTTPException 400: Ha az eszközcsoport nem található vagy a leltári szám már létezik
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset = service.create_asset(
            asset_group_id=request.asset_group_id,
            name=request.name,
            inventory_number=request.inventory_number,
            manufacturer=request.manufacturer,
            model=request.model,
            serial_number=request.serial_number,
            purchase_date=request.purchase_date,
            purchase_price=request.purchase_price,
            current_value=request.current_value,
            location=request.location,
            responsible_employee_id=request.responsible_employee_id,
            status=request.status or "ACTIVE",
            notes=request.notes,
            is_active=request.is_active or True
        )

        return AssetResponse.model_validate(asset)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszköz létrehozása során: {str(e)}"
        )


@asset_router.get(
    "",
    response_model=List[AssetResponse],
    summary="Eszközök listázása",
    description="Eszközök lekérdezése szűrési feltételekkel.",
    dependencies=[Depends(require_permission("assets:view"))]
)
async def list_assets(
    asset_group_id: Optional[int] = Query(None, description="Eszközcsoport szűrő"),
    status_filter: Optional[str] = Query(None, alias="status", description="Státusz szűrő"),
    responsible_employee_id: Optional[int] = Query(None, description="Felelős munkatárs szűrő"),
    is_active: Optional[bool] = Query(None, description="Aktív státusz szűrő"),
    limit: int = Query(100, ge=1, le=500, description="Maximum eredmények száma"),
    offset: int = Query(0, ge=0, description="Lapozási eltolás"),
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> List[AssetResponse]:
    """
    Eszközök listázása.

    **Jogosultság:** `assets:view`

    Args:
        asset_group_id: Eszközcsoport szűrő (opcionális)
        status_filter: Státusz szűrő (opcionális)
        responsible_employee_id: Felelős munkatárs szűrő (opcionális)
        is_active: Aktív státusz szűrő (opcionális)
        limit: Maximum eredmények száma
        offset: Lapozási eltolás
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        List[AssetResponse]: Eszközök listája

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        assets = service.get_assets(
            asset_group_id=asset_group_id,
            status=status_filter,
            responsible_employee_id=responsible_employee_id,
            is_active=is_active,
            limit=limit,
            offset=offset
        )

        return [AssetResponse.model_validate(a) for a in assets]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszközök lekérdezése során: {str(e)}"
        )


@asset_router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="Eszköz részletei",
    description="Egy adott eszköz részletes adatainak lekérdezése.",
    dependencies=[Depends(require_permission("assets:view"))]
)
async def get_asset(
    asset_id: int,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> AssetResponse:
    """
    Eszköz részleteinek lekérdezése.

    **Jogosultság:** `assets:view`

    Args:
        asset_id: Eszköz azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        AssetResponse: Eszköz adatai

    Raises:
        HTTPException 404: Ha az eszköz nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset = service.get_asset_by_id(asset_id)

        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Eszköz nem található: {asset_id}"
            )

        return AssetResponse.model_validate(asset)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszköz lekérdezése során: {str(e)}"
        )


@asset_router.patch(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="Eszköz frissítése",
    description="Meglévő eszköz adatainak frissítése.",
    dependencies=[Depends(require_permission("assets:manage"))]
)
async def update_asset(
    asset_id: int,
    request: AssetUpdate,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> AssetResponse:
    """
    Eszköz frissítése.

    **Jogosultság:** `assets:manage`

    Args:
        asset_id: Eszköz azonosító
        request: Frissítési adatok (AssetUpdate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        AssetResponse: Frissített eszköz adatai

    Raises:
        HTTPException 400: Ha az eszköz nem található vagy egyediségi megszorítás sérül
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset = service.update_asset(
            asset_id=asset_id,
            asset_group_id=request.asset_group_id,
            name=request.name,
            inventory_number=request.inventory_number,
            manufacturer=request.manufacturer,
            model=request.model,
            serial_number=request.serial_number,
            purchase_date=request.purchase_date,
            purchase_price=request.purchase_price,
            current_value=request.current_value,
            location=request.location,
            responsible_employee_id=request.responsible_employee_id,
            status=request.status,
            notes=request.notes,
            is_active=request.is_active
        )

        return AssetResponse.model_validate(asset)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszköz frissítése során: {str(e)}"
        )


@asset_router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eszköz törlése",
    description="Eszköz törlése (soft delete).",
    dependencies=[Depends(require_permission("assets:manage"))]
)
async def delete_asset(
    asset_id: int,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
):
    """
    Eszköz törlése (soft delete).

    **Jogosultság:** `assets:manage`

    Args:
        asset_id: Eszköz azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Raises:
        HTTPException 400: Ha az eszköz nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        service.delete_asset(asset_id)
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az eszköz törlése során: {str(e)}"
        )


# ============================================================================
# Asset Service Endpoints (Szerviz bejegyzések)
# ============================================================================

@asset_router.post(
    "/services",
    response_model=AssetServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Szerviz bejegyzés létrehozása",
    description="Új szerviz bejegyzés létrehozása egy eszközhöz.",
    dependencies=[Depends(require_permission("assets:manage"))]
)
async def create_asset_service_record(
    request: AssetServiceCreate,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> AssetServiceResponse:
    """
    Új szerviz bejegyzés létrehozása.

    **Jogosultság:** `assets:manage`

    Args:
        request: Szerviz adatok (AssetServiceCreate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        AssetServiceResponse: Létrehozott szerviz bejegyzés adatai

    Raises:
        HTTPException 400: Ha az eszköz nem található vagy a szerviz típus érvénytelen
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset_service = service.create_asset_service(
            asset_id=request.asset_id,
            service_type=request.service_type,
            service_date=request.service_date,
            description=request.description,
            cost=request.cost,
            service_provider=request.service_provider,
            next_service_date=request.next_service_date,
            performed_by_employee_id=request.performed_by_employee_id,
            documents_url=request.documents_url
        )

        return AssetServiceResponse.model_validate(asset_service)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a szerviz bejegyzés létrehozása során: {str(e)}"
        )


@asset_router.get(
    "/services",
    response_model=List[AssetServiceResponse],
    summary="Szerviz bejegyzések listázása",
    description="Szerviz bejegyzések lekérdezése szűrési feltételekkel.",
    dependencies=[Depends(require_permission("assets:view"))]
)
async def list_asset_services(
    asset_id: Optional[int] = Query(None, description="Eszköz azonosító szűrő"),
    service_type: Optional[str] = Query(None, description="Szerviz típus szűrő"),
    start_date: Optional[date] = Query(None, description="Kezdő dátum szűrő"),
    end_date: Optional[date] = Query(None, description="Záró dátum szűrő"),
    limit: int = Query(100, ge=1, le=500, description="Maximum eredmények száma"),
    offset: int = Query(0, ge=0, description="Lapozási eltolás"),
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> List[AssetServiceResponse]:
    """
    Szerviz bejegyzések listázása.

    **Jogosultság:** `assets:view`

    Args:
        asset_id: Eszköz azonosító szűrő (opcionális)
        service_type: Szerviz típus szűrő (opcionális)
        start_date: Kezdő dátum szűrő (opcionális)
        end_date: Záró dátum szűrő (opcionális)
        limit: Maximum eredmények száma
        offset: Lapozási eltolás
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        List[AssetServiceResponse]: Szerviz bejegyzések listája

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset_services = service.get_asset_services(
            asset_id=asset_id,
            service_type=service_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        return [AssetServiceResponse.model_validate(s) for s in asset_services]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a szerviz bejegyzések lekérdezése során: {str(e)}"
        )


@asset_router.get(
    "/services/{service_id}",
    response_model=AssetServiceResponse,
    summary="Szerviz bejegyzés részletei",
    description="Egy adott szerviz bejegyzés részletes adatainak lekérdezése.",
    dependencies=[Depends(require_permission("assets:view"))]
)
async def get_asset_service_record(
    service_id: int,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> AssetServiceResponse:
    """
    Szerviz bejegyzés részleteinek lekérdezése.

    **Jogosultság:** `assets:view`

    Args:
        service_id: Szerviz azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        AssetServiceResponse: Szerviz bejegyzés adatai

    Raises:
        HTTPException 404: Ha a szerviz bejegyzés nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset_service = service.get_asset_service_by_id(service_id)

        if not asset_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Szerviz bejegyzés nem található: {service_id}"
            )

        return AssetServiceResponse.model_validate(asset_service)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a szerviz bejegyzés lekérdezése során: {str(e)}"
        )


@asset_router.patch(
    "/services/{service_id}",
    response_model=AssetServiceResponse,
    summary="Szerviz bejegyzés frissítése",
    description="Meglévő szerviz bejegyzés adatainak frissítése.",
    dependencies=[Depends(require_permission("assets:manage"))]
)
async def update_asset_service_record(
    service_id: int,
    request: AssetServiceUpdate,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
) -> AssetServiceResponse:
    """
    Szerviz bejegyzés frissítése.

    **Jogosultság:** `assets:manage`

    Args:
        service_id: Szerviz azonosító
        request: Frissítési adatok (AssetServiceUpdate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Returns:
        AssetServiceResponse: Frissített szerviz bejegyzés adatai

    Raises:
        HTTPException 400: Ha a szerviz bejegyzés nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        asset_service = service.update_asset_service(
            service_id=service_id,
            service_type=request.service_type,
            service_date=request.service_date,
            description=request.description,
            cost=request.cost,
            service_provider=request.service_provider,
            next_service_date=request.next_service_date,
            performed_by_employee_id=request.performed_by_employee_id,
            documents_url=request.documents_url
        )

        return AssetServiceResponse.model_validate(asset_service)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a szerviz bejegyzés frissítése során: {str(e)}"
        )


@asset_router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Szerviz bejegyzés törlése",
    description="Szerviz bejegyzés törlése (hard delete).",
    dependencies=[Depends(require_permission("assets:manage"))]
)
async def delete_asset_service_record(
    service_id: int,
    current_user: Employee = Depends(get_current_user),
    service: AssetManagementService = Depends(get_asset_service)
):
    """
    Szerviz bejegyzés törlése (hard delete).

    **Jogosultság:** `assets:manage`

    Args:
        service_id: Szerviz azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: AssetManagementService instance (dependency)

    Raises:
        HTTPException 400: Ha a szerviz bejegyzés nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        service.delete_asset_service(service_id)
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a szerviz bejegyzés törlése során: {str(e)}"
        )
