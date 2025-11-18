"""
Vehicle Router - Járművek API végpontok
Module 8: Admin - Vehicle Management (V3.0 Phase 3.4)

Ez a router felelős a járművek kezeléséért:
- Járművek (Vehicle) CRUD műveletek
- Tankolások (VehicleRefueling) kezelése
- Karbantartások (VehicleMaintenance) kezelése
- Figyelmeztetések (biztosítás, műszaki lejárat)
"""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.service_admin.models.database import get_db
from backend.service_admin.models.employee import Employee
from backend.service_admin.services.vehicle_service import VehicleManagementService
from backend.service_admin.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
    VehicleRefuelingCreate,
    VehicleRefuelingUpdate,
    VehicleRefuelingResponse,
    VehicleMaintenanceCreate,
    VehicleMaintenanceUpdate,
    VehicleMaintenanceResponse
)
from backend.service_admin.dependencies import require_permission, get_current_user


# ============================================================================
# Router Initialization
# ============================================================================

vehicle_router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)


# ============================================================================
# Dependencies
# ============================================================================

def get_vehicle_service(db: Session = Depends(get_db)) -> VehicleManagementService:
    """
    Dependency injection a VehicleManagementService-hez.

    Args:
        db: SQLAlchemy Session dependency

    Returns:
        VehicleManagementService: Inicializált service instance
    """
    return VehicleManagementService(db)


# ============================================================================
# Vehicle Endpoints (Járművek)
# ============================================================================

@vehicle_router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Jármű létrehozása",
    description="Új jármű létrehozása.",
    dependencies=[Depends(require_permission("vehicles:manage"))]
)
async def create_vehicle(
    request: VehicleCreate,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> VehicleResponse:
    """
    Új jármű létrehozása.

    **Jogosultság:** `vehicles:manage`

    Args:
        request: Jármű adatok (VehicleCreate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        VehicleResponse: Létrehozott jármű adatai

    Raises:
        HTTPException 400: Ha a rendszám vagy VIN már létezik
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        vehicle = service.create_vehicle(
            license_plate=request.license_plate,
            brand=request.brand,
            model=request.model,
            year=request.year,
            vin=request.vin,
            fuel_type=request.fuel_type,
            purchase_date=request.purchase_date,
            purchase_price=request.purchase_price,
            current_value=request.current_value,
            current_mileage=request.current_mileage,
            responsible_employee_id=request.responsible_employee_id,
            status=request.status or "ACTIVE",
            insurance_expiry_date=request.insurance_expiry_date,
            mot_expiry_date=request.mot_expiry_date,
            notes=request.notes,
            is_active=request.is_active or True
        )

        return VehicleResponse.model_validate(vehicle)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a jármű létrehozása során: {str(e)}"
        )


@vehicle_router.get(
    "",
    response_model=List[VehicleResponse],
    summary="Járművek listázása",
    description="Járművek lekérdezése szűrési feltételekkel.",
    dependencies=[Depends(require_permission("vehicles:view"))]
)
async def list_vehicles(
    status_filter: Optional[str] = Query(None, alias="status", description="Státusz szűrő"),
    fuel_type: Optional[str] = Query(None, description="Üzemanyag típus szűrő"),
    responsible_employee_id: Optional[int] = Query(None, description="Felelős munkatárs szűrő"),
    is_active: Optional[bool] = Query(None, description="Aktív státusz szűrő"),
    limit: int = Query(100, ge=1, le=500, description="Maximum eredmények száma"),
    offset: int = Query(0, ge=0, description="Lapozási eltolás"),
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> List[VehicleResponse]:
    """
    Járművek listázása.

    **Jogosultság:** `vehicles:view`

    Args:
        status_filter: Státusz szűrő (opcionális)
        fuel_type: Üzemanyag típus szűrő (opcionális)
        responsible_employee_id: Felelős munkatárs szűrő (opcionális)
        is_active: Aktív státusz szűrő (opcionális)
        limit: Maximum eredmények száma
        offset: Lapozási eltolás
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        List[VehicleResponse]: Járművek listája

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        vehicles = service.get_vehicles(
            status=status_filter,
            fuel_type=fuel_type,
            responsible_employee_id=responsible_employee_id,
            is_active=is_active,
            limit=limit,
            offset=offset
        )

        return [VehicleResponse.model_validate(v) for v in vehicles]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a járművek lekérdezése során: {str(e)}"
        )


@vehicle_router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Jármű részletei",
    description="Egy adott jármű részletes adatainak lekérdezése.",
    dependencies=[Depends(require_permission("vehicles:view"))]
)
async def get_vehicle(
    vehicle_id: int,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> VehicleResponse:
    """
    Jármű részleteinek lekérdezése.

    **Jogosultság:** `vehicles:view`

    Args:
        vehicle_id: Jármű azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        VehicleResponse: Jármű adatai

    Raises:
        HTTPException 404: Ha a jármű nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        vehicle = service.get_vehicle_by_id(vehicle_id)

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Jármű nem található: {vehicle_id}"
            )

        return VehicleResponse.model_validate(vehicle)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a jármű lekérdezése során: {str(e)}"
        )


@vehicle_router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Jármű frissítése",
    description="Meglévő jármű adatainak frissítése.",
    dependencies=[Depends(require_permission("vehicles:manage"))]
)
async def update_vehicle(
    vehicle_id: int,
    request: VehicleUpdate,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> VehicleResponse:
    """
    Jármű frissítése.

    **Jogosultság:** `vehicles:manage`

    Args:
        vehicle_id: Jármű azonosító
        request: Frissítési adatok (VehicleUpdate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        VehicleResponse: Frissített jármű adatai

    Raises:
        HTTPException 400: Ha a jármű nem található vagy egyediségi megszorítás sérül
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        vehicle = service.update_vehicle(
            vehicle_id=vehicle_id,
            license_plate=request.license_plate,
            brand=request.brand,
            model=request.model,
            year=request.year,
            vin=request.vin,
            fuel_type=request.fuel_type,
            purchase_date=request.purchase_date,
            purchase_price=request.purchase_price,
            current_value=request.current_value,
            current_mileage=request.current_mileage,
            responsible_employee_id=request.responsible_employee_id,
            status=request.status,
            insurance_expiry_date=request.insurance_expiry_date,
            mot_expiry_date=request.mot_expiry_date,
            notes=request.notes,
            is_active=request.is_active
        )

        return VehicleResponse.model_validate(vehicle)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a jármű frissítése során: {str(e)}"
        )


@vehicle_router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Jármű törlése",
    description="Jármű törlése (soft delete).",
    dependencies=[Depends(require_permission("vehicles:manage"))]
)
async def delete_vehicle(
    vehicle_id: int,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
):
    """
    Jármű törlése (soft delete).

    **Jogosultság:** `vehicles:manage`

    Args:
        vehicle_id: Jármű azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Raises:
        HTTPException 400: Ha a jármű nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        service.delete_vehicle(vehicle_id)
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a jármű törlése során: {str(e)}"
        )


# ============================================================================
# Vehicle Warning Endpoints (Figyelmeztetések)
# ============================================================================

@vehicle_router.get(
    "/{vehicle_id}/warnings",
    summary="Jármű figyelmeztetései",
    description="Egy adott jármű figyelmeztetéseinek lekérdezése (biztosítás, műszaki, szerviz).",
    dependencies=[Depends(require_permission("vehicles:view"))]
)
async def get_vehicle_warnings(
    vehicle_id: int,
    days_threshold: int = Query(30, ge=1, le=365, description="Figyelmeztetési küszöb (napokban)"),
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
):
    """
    Jármű figyelmeztetéseinek lekérdezése.

    **Jogosultság:** `vehicles:view`

    Args:
        vehicle_id: Jármű azonosító
        days_threshold: Figyelmeztetési küszöb (napokban, default: 30)
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        Dict: Figyelmeztetések

    Raises:
        HTTPException 404: Ha a jármű nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        warnings = service.get_vehicle_warnings(vehicle_id, days_threshold)
        return warnings

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a figyelmeztetések lekérdezése során: {str(e)}"
        )


@vehicle_router.get(
    "/warnings/all",
    summary="Összes jármű figyelmeztetései",
    description="Összes aktív jármű figyelmeztetéseinek lekérdezése.",
    dependencies=[Depends(require_permission("vehicles:view"))]
)
async def get_all_vehicle_warnings(
    days_threshold: int = Query(30, ge=1, le=365, description="Figyelmeztetési küszöb (napokban)"),
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
):
    """
    Összes aktív jármű figyelmeztetéseinek lekérdezése.

    **Jogosultság:** `vehicles:view`

    Args:
        days_threshold: Figyelmeztetési küszöb (napokban, default: 30)
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        List[Dict]: Járművek figyelmeztetéseinek listája

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        all_warnings = service.get_all_vehicle_warnings(days_threshold)
        return all_warnings

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a figyelmeztetések lekérdezése során: {str(e)}"
        )


# ============================================================================
# Vehicle Refueling Endpoints (Tankolások)
# ============================================================================

@vehicle_router.post(
    "/refuelings",
    response_model=VehicleRefuelingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tankolás bejegyzés létrehozása",
    description="Új tankolás bejegyzés létrehozása egy járműhöz.",
    dependencies=[Depends(require_permission("vehicles:manage"))]
)
async def create_vehicle_refueling(
    request: VehicleRefuelingCreate,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> VehicleRefuelingResponse:
    """
    Új tankolás bejegyzés létrehozása.

    **Jogosultság:** `vehicles:manage`

    Args:
        request: Tankolás adatok (VehicleRefuelingCreate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        VehicleRefuelingResponse: Létrehozott tankolás bejegyzés adatai

    Raises:
        HTTPException 400: Ha a jármű nem található vagy az üzemanyag típus érvénytelen
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        refueling = service.create_vehicle_refueling(
            vehicle_id=request.vehicle_id,
            refueling_date=request.refueling_date,
            mileage=request.mileage,
            fuel_type=request.fuel_type,
            quantity_liters=request.quantity_liters,
            price_per_liter=request.price_per_liter,
            total_cost=request.total_cost,
            full_tank=request.full_tank or True,
            location=request.location,
            invoice_number=request.invoice_number,
            recorded_by_employee_id=request.recorded_by_employee_id,
            notes=request.notes
        )

        return VehicleRefuelingResponse.model_validate(refueling)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a tankolás bejegyzés létrehozása során: {str(e)}"
        )


@vehicle_router.get(
    "/refuelings",
    response_model=List[VehicleRefuelingResponse],
    summary="Tankolások listázása",
    description="Tankolás bejegyzések lekérdezése szűrési feltételekkel.",
    dependencies=[Depends(require_permission("vehicles:view"))]
)
async def list_vehicle_refuelings(
    vehicle_id: Optional[int] = Query(None, description="Jármű azonosító szűrő"),
    fuel_type: Optional[str] = Query(None, description="Üzemanyag típus szűrő"),
    start_date: Optional[date] = Query(None, description="Kezdő dátum szűrő"),
    end_date: Optional[date] = Query(None, description="Záró dátum szűrő"),
    limit: int = Query(100, ge=1, le=500, description="Maximum eredmények száma"),
    offset: int = Query(0, ge=0, description="Lapozási eltolás"),
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> List[VehicleRefuelingResponse]:
    """
    Tankolás bejegyzések listázása.

    **Jogosultság:** `vehicles:view`

    Args:
        vehicle_id: Jármű azonosító szűrő (opcionális)
        fuel_type: Üzemanyag típus szűrő (opcionális)
        start_date: Kezdő dátum szűrő (opcionális)
        end_date: Záró dátum szűrő (opcionális)
        limit: Maximum eredmények száma
        offset: Lapozási eltolás
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        List[VehicleRefuelingResponse]: Tankolás bejegyzések listája

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        refuelings = service.get_vehicle_refuelings(
            vehicle_id=vehicle_id,
            fuel_type=fuel_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        return [VehicleRefuelingResponse.model_validate(r) for r in refuelings]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a tankolások lekérdezése során: {str(e)}"
        )


@vehicle_router.get(
    "/refuelings/{refueling_id}",
    response_model=VehicleRefuelingResponse,
    summary="Tankolás részletei",
    description="Egy adott tankolás bejegyzés részletes adatainak lekérdezése.",
    dependencies=[Depends(require_permission("vehicles:view"))]
)
async def get_vehicle_refueling(
    refueling_id: int,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> VehicleRefuelingResponse:
    """
    Tankolás bejegyzés részleteinek lekérdezése.

    **Jogosultság:** `vehicles:view`

    Args:
        refueling_id: Tankolás azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        VehicleRefuelingResponse: Tankolás bejegyzés adatai

    Raises:
        HTTPException 404: Ha a tankolás bejegyzés nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        refueling = service.get_vehicle_refueling_by_id(refueling_id)

        if not refueling:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tankolás bejegyzés nem található: {refueling_id}"
            )

        return VehicleRefuelingResponse.model_validate(refueling)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a tankolás lekérdezése során: {str(e)}"
        )


@vehicle_router.patch(
    "/refuelings/{refueling_id}",
    response_model=VehicleRefuelingResponse,
    summary="Tankolás frissítése",
    description="Meglévő tankolás bejegyzés adatainak frissítése.",
    dependencies=[Depends(require_permission("vehicles:manage"))]
)
async def update_vehicle_refueling(
    refueling_id: int,
    request: VehicleRefuelingUpdate,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> VehicleRefuelingResponse:
    """
    Tankolás bejegyzés frissítése.

    **Jogosultság:** `vehicles:manage`

    Args:
        refueling_id: Tankolás azonosító
        request: Frissítési adatok (VehicleRefuelingUpdate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        VehicleRefuelingResponse: Frissített tankolás bejegyzés adatai

    Raises:
        HTTPException 400: Ha a tankolás bejegyzés nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        refueling = service.update_vehicle_refueling(
            refueling_id=refueling_id,
            refueling_date=request.refueling_date,
            mileage=request.mileage,
            fuel_type=request.fuel_type,
            quantity_liters=request.quantity_liters,
            price_per_liter=request.price_per_liter,
            total_cost=request.total_cost,
            full_tank=request.full_tank,
            location=request.location,
            invoice_number=request.invoice_number,
            recorded_by_employee_id=request.recorded_by_employee_id,
            notes=request.notes
        )

        return VehicleRefuelingResponse.model_validate(refueling)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a tankolás frissítése során: {str(e)}"
        )


@vehicle_router.delete(
    "/refuelings/{refueling_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Tankolás törlése",
    description="Tankolás bejegyzés törlése (hard delete).",
    dependencies=[Depends(require_permission("vehicles:manage"))]
)
async def delete_vehicle_refueling(
    refueling_id: int,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
):
    """
    Tankolás bejegyzés törlése (hard delete).

    **Jogosultság:** `vehicles:manage`

    Args:
        refueling_id: Tankolás azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Raises:
        HTTPException 400: Ha a tankolás bejegyzés nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        service.delete_vehicle_refueling(refueling_id)
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a tankolás törlése során: {str(e)}"
        )


# ============================================================================
# Vehicle Maintenance Endpoints (Karbantartások)
# ============================================================================

@vehicle_router.post(
    "/maintenances",
    response_model=VehicleMaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Karbantartás bejegyzés létrehozása",
    description="Új karbantartás bejegyzés létrehozása egy járműhöz.",
    dependencies=[Depends(require_permission("vehicles:manage"))]
)
async def create_vehicle_maintenance(
    request: VehicleMaintenanceCreate,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> VehicleMaintenanceResponse:
    """
    Új karbantartás bejegyzés létrehozása.

    **Jogosultság:** `vehicles:manage`

    Args:
        request: Karbantartás adatok (VehicleMaintenanceCreate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        VehicleMaintenanceResponse: Létrehozott karbantartás bejegyzés adatai

    Raises:
        HTTPException 400: Ha a jármű nem található vagy a karbantartás típus érvénytelen
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        maintenance = service.create_vehicle_maintenance(
            vehicle_id=request.vehicle_id,
            maintenance_type=request.maintenance_type,
            maintenance_date=request.maintenance_date,
            mileage=request.mileage,
            description=request.description,
            cost=request.cost,
            service_provider=request.service_provider,
            next_maintenance_date=request.next_maintenance_date,
            next_maintenance_mileage=request.next_maintenance_mileage,
            invoice_number=request.invoice_number,
            recorded_by_employee_id=request.recorded_by_employee_id,
            notes=request.notes
        )

        return VehicleMaintenanceResponse.model_validate(maintenance)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a karbantartás bejegyzés létrehozása során: {str(e)}"
        )


@vehicle_router.get(
    "/maintenances",
    response_model=List[VehicleMaintenanceResponse],
    summary="Karbantartások listázása",
    description="Karbantartás bejegyzések lekérdezése szűrési feltételekkel.",
    dependencies=[Depends(require_permission("vehicles:view"))]
)
async def list_vehicle_maintenances(
    vehicle_id: Optional[int] = Query(None, description="Jármű azonosító szűrő"),
    maintenance_type: Optional[str] = Query(None, description="Karbantartás típus szűrő"),
    start_date: Optional[date] = Query(None, description="Kezdő dátum szűrő"),
    end_date: Optional[date] = Query(None, description="Záró dátum szűrő"),
    limit: int = Query(100, ge=1, le=500, description="Maximum eredmények száma"),
    offset: int = Query(0, ge=0, description="Lapozási eltolás"),
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> List[VehicleMaintenanceResponse]:
    """
    Karbantartás bejegyzések listázása.

    **Jogosultság:** `vehicles:view`

    Args:
        vehicle_id: Jármű azonosító szűrő (opcionális)
        maintenance_type: Karbantartás típus szűrő (opcionális)
        start_date: Kezdő dátum szűrő (opcionális)
        end_date: Záró dátum szűrő (opcionális)
        limit: Maximum eredmények száma
        offset: Lapozási eltolás
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        List[VehicleMaintenanceResponse]: Karbantartás bejegyzések listája

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        maintenances = service.get_vehicle_maintenances(
            vehicle_id=vehicle_id,
            maintenance_type=maintenance_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        return [VehicleMaintenanceResponse.model_validate(m) for m in maintenances]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a karbantartások lekérdezése során: {str(e)}"
        )


@vehicle_router.get(
    "/maintenances/{maintenance_id}",
    response_model=VehicleMaintenanceResponse,
    summary="Karbantartás részletei",
    description="Egy adott karbantartás bejegyzés részletes adatainak lekérdezése.",
    dependencies=[Depends(require_permission("vehicles:view"))]
)
async def get_vehicle_maintenance(
    maintenance_id: int,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> VehicleMaintenanceResponse:
    """
    Karbantartás bejegyzés részleteinek lekérdezése.

    **Jogosultság:** `vehicles:view`

    Args:
        maintenance_id: Karbantartás azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        VehicleMaintenanceResponse: Karbantartás bejegyzés adatai

    Raises:
        HTTPException 404: Ha a karbantartás bejegyzés nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        maintenance = service.get_vehicle_maintenance_by_id(maintenance_id)

        if not maintenance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Karbantartás bejegyzés nem található: {maintenance_id}"
            )

        return VehicleMaintenanceResponse.model_validate(maintenance)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a karbantartás lekérdezése során: {str(e)}"
        )


@vehicle_router.patch(
    "/maintenances/{maintenance_id}",
    response_model=VehicleMaintenanceResponse,
    summary="Karbantartás frissítése",
    description="Meglévő karbantartás bejegyzés adatainak frissítése.",
    dependencies=[Depends(require_permission("vehicles:manage"))]
)
async def update_vehicle_maintenance(
    maintenance_id: int,
    request: VehicleMaintenanceUpdate,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
) -> VehicleMaintenanceResponse:
    """
    Karbantartás bejegyzés frissítése.

    **Jogosultság:** `vehicles:manage`

    Args:
        maintenance_id: Karbantartás azonosító
        request: Frissítési adatok (VehicleMaintenanceUpdate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Returns:
        VehicleMaintenanceResponse: Frissített karbantartás bejegyzés adatai

    Raises:
        HTTPException 400: Ha a karbantartás bejegyzés nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        maintenance = service.update_vehicle_maintenance(
            maintenance_id=maintenance_id,
            maintenance_type=request.maintenance_type,
            maintenance_date=request.maintenance_date,
            mileage=request.mileage,
            description=request.description,
            cost=request.cost,
            service_provider=request.service_provider,
            next_maintenance_date=request.next_maintenance_date,
            next_maintenance_mileage=request.next_maintenance_mileage,
            invoice_number=request.invoice_number,
            recorded_by_employee_id=request.recorded_by_employee_id,
            notes=request.notes
        )

        return VehicleMaintenanceResponse.model_validate(maintenance)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a karbantartás frissítése során: {str(e)}"
        )


@vehicle_router.delete(
    "/maintenances/{maintenance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Karbantartás törlése",
    description="Karbantartás bejegyzés törlése (hard delete).",
    dependencies=[Depends(require_permission("vehicles:manage"))]
)
async def delete_vehicle_maintenance(
    maintenance_id: int,
    current_user: Employee = Depends(get_current_user),
    service: VehicleManagementService = Depends(get_vehicle_service)
):
    """
    Karbantartás bejegyzés törlése (hard delete).

    **Jogosultság:** `vehicles:manage`

    Args:
        maintenance_id: Karbantartás azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: VehicleManagementService instance (dependency)

    Raises:
        HTTPException 400: Ha a karbantartás bejegyzés nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        service.delete_vehicle_maintenance(maintenance_id)
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a karbantartás törlése során: {str(e)}"
        )
