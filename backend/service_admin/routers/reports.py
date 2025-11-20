"""
Reports Router - Analytics & Reporting API endpoints
Module 8: Admin - Reporting & Analytics

This router provides endpoints for business intelligence and analytics:
- Sales reports with daily breakdown and payment method analysis
- Top products by quantity sold
- Inventory consumption tracking
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.service_admin.models.database import get_db
from backend.service_admin.models.employee import Employee
from backend.service_admin.services.reporting_service import ReportingService
from backend.service_admin.schemas.report import (
    SalesReportResponse,
    TopProductsReportResponse,
    ConsumptionReportResponse
)
from backend.service_admin.dependencies import require_permission, get_current_user


# ============================================================================
# Router Initialization
# ============================================================================

reports_router = APIRouter(
    prefix="/reports",
    tags=["Reports & Analytics"]
)


# ============================================================================
# Sales Report Endpoints
# ============================================================================

@reports_router.get(
    "/sales",
    response_model=SalesReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Értékesítési riport",
    description="Napi bontású értékesítési riport bevétellel, rendelésszámmal és átlagos kosárértékkel. Bontás fizetési mód szerint (CASH, CARD).",
    dependencies=[Depends(require_permission("reports:view"))]
)
async def get_sales_report(
    start_date: date = Query(
        ...,
        description="Kezdő dátum (YYYY-MM-DD)",
        example="2024-01-01"
    ),
    end_date: date = Query(
        ...,
        description="Befejező dátum (YYYY-MM-DD)",
        example="2024-01-31"
    ),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SalesReportResponse:
    """
    Értékesítési riport generálása dátumtartományra.

    **Jogosultság:** `reports:view`

    A riport tartalmazza:
    - Napi bontású bevétel, rendelésszám, átlagos kosárérték
    - Fizetési mód szerinti bontás (készpénz/kártya)
    - Összesítő statisztikák az időszakra

    Args:
        start_date: Kezdő dátum
        end_date: Befejező dátum
        current_user: Bejelentkezett felhasználó (dependency)
        db: Adatbázis session (dependency)

    Returns:
        SalesReportResponse: Értékesítési riport adatai

    Raises:
        HTTPException 400: Ha a dátumtartomány érvénytelen
        HTTPException 403: Ha nincs jogosultság
    """
    # Validate date range
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A kezdő dátum nem lehet későbbi a befejező dátumnál"
        )

    try:
        report_data = await ReportingService.get_sales_report(
            db=db,
            start_date=start_date,
            end_date=end_date
        )
        return report_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a riport generálása során: {str(e)}"
        )


# ============================================================================
# Top Products Report Endpoints
# ============================================================================

@reports_router.get(
    "/top-products",
    response_model=TopProductsReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Top termékek riport",
    description="Legtöbbet eladott termékek listája mennyiség alapján, opcionális dátumszűréssel.",
    dependencies=[Depends(require_permission("reports:view"))]
)
async def get_top_products_report(
    limit: int = Query(
        10,
        description="Maximum hány terméket listázzon",
        ge=1,
        le=100,
        example=10
    ),
    start_date: Optional[date] = Query(
        None,
        description="Kezdő dátum (opcionális, YYYY-MM-DD)",
        example="2024-01-01"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Befejező dátum (opcionális, YYYY-MM-DD)",
        example="2024-01-31"
    ),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TopProductsReportResponse:
    """
    Top termékek riport generálása.

    **Jogosultság:** `reports:view`

    A riport tartalmazza:
    - Termék azonosító és név
    - Összes eladott mennyiség
    - Összes bevétel a termékből
    - Hány rendelésben szerepelt
    - Átlagos eladási ár

    Args:
        limit: Maximum hány terméket adjon vissza
        start_date: Opcionális kezdő dátum szűréshez
        end_date: Opcionális befejező dátum szűréshez
        current_user: Bejelentkezett felhasználó (dependency)
        db: Adatbázis session (dependency)

    Returns:
        TopProductsReportResponse: Top termékek riport adatai

    Raises:
        HTTPException 400: Ha a dátumtartomány érvénytelen
        HTTPException 403: Ha nincs jogosultság
    """
    # Validate date range if both dates are provided
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A kezdő dátum nem lehet későbbi a befejező dátumnál"
        )

    # Both dates must be provided together
    if (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A kezdő és befejező dátumot együtt kell megadni"
        )

    try:
        report_data = await ReportingService.get_top_products_report(
            db=db,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        return report_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a riport generálása során: {str(e)}"
        )


# ============================================================================
# Consumption Report Endpoints
# ============================================================================

@reports_router.get(
    "/consumption",
    response_model=ConsumptionReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Készletfogyás riport",
    description="Készletcikkek fogyásának elemzése aktuális készlet alapján.",
    dependencies=[Depends(require_permission("reports:view"))]
)
async def get_consumption_report(
    start_date: Optional[date] = Query(
        None,
        description="Kezdő dátum (opcionális, jövőbeli használatra)",
        example="2024-01-01"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Befejező dátum (opcionális, jövőbeli használatra)",
        example="2024-01-31"
    ),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ConsumptionReportResponse:
    """
    Készletfogyás riport generálása.

    **Jogosultság:** `reports:view`

    A riport tartalmazza:
    - Készletcikk azonosító és név
    - Nyitó készlet (becsült)
    - Jelenlegi készlet
    - Felhasznált mennyiség
    - Fogyás százalékban
    - Becsült fogyás értéke

    **Megjegyzés:** A jelenlegi implementáció az aktuális készletet
    használja alapként. Részletesebb elemzéshez történeti adatok
    (napi leltárak) szükségesek.

    Args:
        start_date: Kezdő dátum (jövőbeli használatra)
        end_date: Befejező dátum (jövőbeli használatra)
        current_user: Bejelentkezett felhasználó (dependency)
        db: Adatbázis session (dependency)

    Returns:
        ConsumptionReportResponse: Készletfogyás riport adatai

    Raises:
        HTTPException 400: Ha a dátumtartomány érvénytelen
        HTTPException 403: Ha nincs jogosultság
    """
    # Validate date range if both dates are provided
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A kezdő dátum nem lehet későbbi a befejező dátumnál"
        )

    try:
        report_data = await ReportingService.get_consumption_report(
            db=db,
            start_date=start_date,
            end_date=end_date
        )
        return report_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a riport generálása során: {str(e)}"
        )
