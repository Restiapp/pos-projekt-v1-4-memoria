"""
Reports Router - Dashboard Analitika API végpontok

Ez a router felelős a dashboard analitikai végpontok kezeléséért:
- Értékesítési statisztikák (napi bontás)
- Top termékek elemzése
- Készletfogyási riportok
"""

from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.service_admin.models.database import get_db
from backend.service_admin.models.employee import Employee
from backend.service_admin.services.reports_service import ReportsService
from backend.service_admin.schemas.reports import (
    SalesReportResponse,
    TopProductsResponse,
    ConsumptionReportResponse
)
from backend.service_admin.dependencies import require_permission, get_current_user


# ============================================================================
# Router Initialization
# ============================================================================

reports_router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# ============================================================================
# Dependencies
# ============================================================================

def get_reports_service(db: Session = Depends(get_db)) -> ReportsService:
    """
    Dependency injection a ReportsService-hez.

    Args:
        db: SQLAlchemy Session dependency

    Returns:
        ReportsService: Inicializált service instance
    """
    return ReportsService(db)


# ============================================================================
# Sales Report Endpoints
# ============================================================================

@reports_router.get(
    "/sales",
    response_model=SalesReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Értékesítési statisztikák (napi bontás)",
    description="Értékesítési riport lekérése napi bontásban, cash/card bontással.",
    dependencies=[Depends(require_permission("reports:view"))]
)
async def get_sales_report(
    start_date: Optional[date] = Query(
        None,
        description="Kezdő dátum (YYYY-MM-DD). Default: 30 nappal ezelőtt"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Záró dátum (YYYY-MM-DD). Default: ma"
    ),
    current_user: Employee = Depends(get_current_user),
    service: ReportsService = Depends(get_reports_service)
) -> SalesReportResponse:
    """
    Értékesítési statisztikák lekérése napi bontásban.

    **Jogosultság:** `reports:view`

    **Visszaadott adatok:**
    - Napi bevételek (összesített, cash, card)
    - Napi rendelésszámok
    - Átlagos rendelésérték naponta
    - Időszak összesítők

    Args:
        start_date: Kezdő dátum (opcionális)
        end_date: Záró dátum (opcionális)
        current_user: Bejelentkezett felhasználó (dependency)
        service: ReportsService instance (dependency)

    Returns:
        SalesReportResponse: Napi bontású értékesítési adatok

    Raises:
        HTTPException 400: Ha a dátumok hibásak
        HTTPException 403: Ha nincs jogosultság
        HTTPException 503: Ha a service_orders nem elérhető
    """
    try:
        # Dátumok validálása
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A kezdő dátum nem lehet későbbi mint a záró dátum"
            )

        # Maximum 365 napos intervallum
        if start_date and end_date:
            delta = (end_date - start_date).days
            if delta > 365:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum 365 napos időszakot lehet lekérdezni"
                )

        report = await service.get_sales_report(
            start_date=start_date,
            end_date=end_date
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Hiba történt az értékesítési adatok lekérdezése során: {str(e)}"
        )


# ============================================================================
# Top Products Endpoints
# ============================================================================

@reports_router.get(
    "/top-products",
    response_model=TopProductsResponse,
    status_code=status.HTTP_200_OK,
    summary="Top termékek elemzése",
    description="Legnépszerűbb termékek eladott mennyiség és bevétel alapján.",
    dependencies=[Depends(require_permission("reports:view"))]
)
async def get_top_products(
    start_date: Optional[date] = Query(
        None,
        description="Kezdő dátum (YYYY-MM-DD). Default: 30 nappal ezelőtt"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Záró dátum (YYYY-MM-DD). Default: ma"
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum hány terméket adjunk vissza (default: 10)"
    ),
    current_user: Employee = Depends(get_current_user),
    service: ReportsService = Depends(get_reports_service)
) -> TopProductsResponse:
    """
    Top termékek elemzése eladott mennyiség alapján.

    **Jogosultság:** `reports:view`

    **Visszaadott adatok:**
    - Termék név és kategória
    - Eladott mennyiség (db)
    - Összes bevétel a termékből
    - Átlagos eladási ár

    Args:
        start_date: Kezdő dátum (opcionális)
        end_date: Záró dátum (opcionális)
        limit: Maximum eredmények száma (1-100)
        current_user: Bejelentkezett felhasználó (dependency)
        service: ReportsService instance (dependency)

    Returns:
        TopProductsResponse: Top termékek listája

    Raises:
        HTTPException 400: Ha a dátumok vagy limit hibás
        HTTPException 403: Ha nincs jogosultság
        HTTPException 503: Ha a service_orders vagy service_menu nem elérhető
    """
    try:
        # Dátumok validálása
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A kezdő dátum nem lehet későbbi mint a záró dátum"
            )

        report = await service.get_top_products(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Hiba történt a top termékek lekérdezése során: {str(e)}"
        )


# ============================================================================
# Inventory Consumption Endpoints
# ============================================================================

@reports_router.get(
    "/consumption",
    response_model=ConsumptionReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Készletfogyási riport",
    description="Alapanyag/készletcikkek fogyási adatai az időszakban.",
    dependencies=[Depends(require_permission("reports:view"))]
)
async def get_consumption_report(
    start_date: Optional[date] = Query(
        None,
        description="Kezdő dátum (YYYY-MM-DD). Default: 30 nappal ezelőtt"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Záró dátum (YYYY-MM-DD). Default: ma"
    ),
    current_user: Employee = Depends(get_current_user),
    service: ReportsService = Depends(get_reports_service)
) -> ConsumptionReportResponse:
    """
    Készletfogyási riport lekérése.

    **Jogosultság:** `reports:view`

    **Visszaadott adatok:**
    - Alapanyag/készletcikk neve
    - Fogyott mennyiség és egység
    - Becsült költség

    Args:
        start_date: Kezdő dátum (opcionális)
        end_date: Záró dátum (opcionális)
        current_user: Bejelentkezett felhasználó (dependency)
        service: ReportsService instance (dependency)

    Returns:
        ConsumptionReportResponse: Készletfogyási adatok

    Raises:
        HTTPException 400: Ha a dátumok hibásak
        HTTPException 403: Ha nincs jogosultság
        HTTPException 503: Ha a service_inventory nem elérhető
    """
    try:
        # Dátumok validálása
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A kezdő dátum nem lehet későbbi mint a záró dátum"
            )

        report = await service.get_consumption_report(
            start_date=start_date,
            end_date=end_date
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        # Graceful degradation: log error but don't fail
        # (consumption report is nice-to-have, not critical)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Hiba történt a készletfogyási adatok lekérdezése során: {str(e)}"
        )


# ============================================================================
# Health Check Endpoint (for testing)
# ============================================================================

@reports_router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Reports service health check",
    description="Ellenőrzi hogy a reports service működik-e."
)
async def health_check():
    """
    Egyszerű health check endpoint tesztelésre.

    Returns:
        dict: Status üzenet
    """
    return {
        "status": "healthy",
        "service": "reports",
        "message": "Reports service is running"
    }
