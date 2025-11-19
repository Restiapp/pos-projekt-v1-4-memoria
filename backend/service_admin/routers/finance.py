"""
Finance Router - Pénzügyi API végpontok
Module 8: Admin - Finance Management (V3.0 Phase 1)

Ez a router felelős a pénzügyi műveletek kezeléséért:
- Készpénz befizetés/kivétel (cash drawer operations)
- Napi pénztárzárás
- Pénzmozgások lekérdezése
"""

from typing import Optional, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.service_admin.models.database import get_db
from backend.service_admin.models.employee import Employee
from backend.service_admin.services.finance_service import FinanceService
from backend.service_admin.schemas.finance import (
    CashDepositRequest,
    CashWithdrawRequest,
    CashMovementResponse,
    DailyClosureCreate,
    DailyClosureUpdate,
    DailyClosureResponse
)
from backend.service_admin.dependencies import require_permission, get_current_user


# ============================================================================
# Router Initialization
# ============================================================================

finance_router = APIRouter(
    prefix="/finance",
    tags=["Finance"]
)


# ============================================================================
# Dependencies
# ============================================================================

def get_finance_service(db: Session = Depends(get_db)) -> FinanceService:
    """
    Dependency injection a FinanceService-hez.

    Args:
        db: SQLAlchemy Session dependency

    Returns:
        FinanceService: Inicializált service instance
    """
    return FinanceService(db)


# ============================================================================
# Cash Drawer Endpoints (Pénztár műveletek)
# ============================================================================

@finance_router.post(
    "/cash-drawer/deposit",
    response_model=CashMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Készpénz befizetés",
    description="Készpénz befizetés rögzítése a pénztárba.",
    dependencies=[Depends(require_permission("finance:manage"))]
)
async def cash_deposit(
    request: CashDepositRequest,
    current_user: Employee = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
) -> CashMovementResponse:
    """
    Készpénz befizetés rögzítése.

    **Jogosultság:** `finance:manage`

    Args:
        request: Befizetés adatok (CashDepositRequest schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: FinanceService instance (dependency)

    Returns:
        CashMovementResponse: Létrehozott pénzmozgás adatai

    Raises:
        HTTPException 400: Ha az összeg nem pozitív
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        # Használjuk az employee_id-t ha meg van adva, különben a bejelentkezett felhasználót
        employee_id = request.employee_id or current_user.id

        movement = service.record_cash_deposit(
            amount=request.amount,
            description=request.description,
            employee_id=employee_id
        )

        return CashMovementResponse.model_validate(movement)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a befizetés rögzítése során: {str(e)}"
        )


@finance_router.post(
    "/cash-drawer/withdraw",
    response_model=CashMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Készpénz kivétel",
    description="Készpénz kivétel rögzítése a pénztárból.",
    dependencies=[Depends(require_permission("finance:manage"))]
)
async def cash_withdraw(
    request: CashWithdrawRequest,
    current_user: Employee = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
) -> CashMovementResponse:
    """
    Készpénz kivétel rögzítése.

    **Jogosultság:** `finance:manage`

    Args:
        request: Kivétel adatok (CashWithdrawRequest schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: FinanceService instance (dependency)

    Returns:
        CashMovementResponse: Létrehozott pénzmozgás adatai

    Raises:
        HTTPException 400: Ha az összeg nem pozitív vagy nincs elegendő készpénz
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        # Használjuk az employee_id-t ha meg van adva, különben a bejelentkezett felhasználót
        employee_id = request.employee_id or current_user.id

        movement = service.record_cash_withdrawal(
            amount=request.amount,
            description=request.description,
            employee_id=employee_id
        )

        return CashMovementResponse.model_validate(movement)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a kivétel rögzítése során: {str(e)}"
        )


@finance_router.get(
    "/cash-drawer/movements",
    response_model=List[CashMovementResponse],
    summary="Készpénzmozgások listázása",
    description="Adott időszakra vonatkozó készpénzmozgások listázása.",
    dependencies=[Depends(require_permission("finance:view"))]
)
async def get_cash_movements(
    start_date: Optional[datetime] = Query(None, description="Kezdő dátum"),
    end_date: Optional[datetime] = Query(None, description="Záró dátum"),
    movement_type: Optional[str] = Query(None, description="Mozgás típusa"),
    employee_id: Optional[int] = Query(None, description="Munkatárs azonosító"),
    limit: int = Query(100, ge=1, le=500, description="Maximum eredmények száma"),
    offset: int = Query(0, ge=0, description="Lapozási eltolás"),
    current_user: Employee = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
) -> List[CashMovementResponse]:
    """
    Készpénzmozgások listázása időszak szerint.

    **Jogosultság:** `finance:view`

    Args:
        start_date: Kezdő dátum (opcionális)
        end_date: Záró dátum (opcionális)
        movement_type: Mozgás típusa (opcionális)
        employee_id: Munkatárs azonosító (opcionális)
        limit: Maximum eredmények száma
        offset: Lapozási eltolás
        current_user: Bejelentkezett felhasználó (dependency)
        service: FinanceService instance (dependency)

    Returns:
        List[CashMovementResponse]: Pénzmozgások listája

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        from backend.service_admin.models.finance import CashMovementType

        # Parse movement_type if provided
        parsed_movement_type = None
        if movement_type:
            try:
                parsed_movement_type = CashMovementType(movement_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Érvénytelen mozgás típus: {movement_type}. "
                           f"Érvényes értékek: {[t.value for t in CashMovementType]}"
                )

        movements = service.get_cash_movements(
            start_date=start_date,
            end_date=end_date,
            movement_type=parsed_movement_type,
            employee_id=employee_id,
            limit=limit,
            offset=offset
        )

        return [CashMovementResponse.model_validate(m) for m in movements]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a pénzmozgások lekérdezése során: {str(e)}"
        )


@finance_router.get(
    "/cash-drawer/balance",
    summary="Aktuális készpénz egyenleg",
    description="Lekérdezi az aktuális készpénz egyenleget a pénztárban.",
    dependencies=[Depends(require_permission("finance:view"))]
)
async def get_cash_balance(
    current_user: Employee = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
) -> dict:
    """
    Aktuális készpénz egyenleg lekérdezése.

    **Jogosultság:** `finance:view`

    Args:
        current_user: Bejelentkezett felhasználó (dependency)
        service: FinanceService instance (dependency)

    Returns:
        dict: Aktuális egyenleg

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        balance = service.get_current_cash_balance()

        return {
            "balance": float(balance),
            "currency": "HUF",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt az egyenleg lekérdezése során: {str(e)}"
        )


# ============================================================================
# Daily Closure Endpoints (Napi Pénztárzárás)
# ============================================================================

@finance_router.post(
    "/daily-closures",
    response_model=DailyClosureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Napi pénztárzárás létrehozása",
    description="Új napi pénztárzárás létrehozása.",
    dependencies=[Depends(require_permission("finance:manage"))]
)
async def create_daily_closure(
    request: DailyClosureCreate,
    current_user: Employee = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
) -> DailyClosureResponse:
    """
    Napi pénztárzárás létrehozása.

    **Jogosultság:** `finance:manage`

    Args:
        request: Zárás adatok (DailyClosureCreate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: FinanceService instance (dependency)

    Returns:
        DailyClosureResponse: Létrehozott napi zárás adatai

    Raises:
        HTTPException 400: Ha már van nyitott zárás
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        # Használjuk az employee_id-t ha meg van adva, különben a bejelentkezett felhasználót
        employee_id = request.closed_by_employee_id or current_user.id

        closure = service.create_daily_closure(
            opening_balance=request.opening_balance,
            closed_by_employee_id=employee_id,
            notes=request.notes
        )

        return DailyClosureResponse.model_validate(closure)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a zárás létrehozása során: {str(e)}"
        )


@finance_router.patch(
    "/daily-closures/{closure_id}/close",
    response_model=DailyClosureResponse,
    summary="Napi pénztárzárás lezárása",
    description="Napi pénztárzárás lezárása tényleges egyenleggel.",
    dependencies=[Depends(require_permission("finance:manage"))]
)
async def close_daily_closure(
    closure_id: int,
    request: DailyClosureUpdate,
    current_user: Employee = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
) -> DailyClosureResponse:
    """
    Napi pénztárzárás lezárása.

    **Jogosultság:** `finance:manage`

    Args:
        closure_id: Zárás azonosító
        request: Lezárás adatok (DailyClosureUpdate schema)
        current_user: Bejelentkezett felhasználó (dependency)
        service: FinanceService instance (dependency)

    Returns:
        DailyClosureResponse: Frissített napi zárás adatai

    Raises:
        HTTPException 400: Ha a zárás nem található vagy már lezárt
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        if not request.actual_closing_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A tényleges záró egyenleg megadása kötelező"
            )

        closure = service.close_daily_closure(
            closure_id=closure_id,
            actual_closing_balance=request.actual_closing_balance,
            notes=request.notes
        )

        return DailyClosureResponse.model_validate(closure)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a zárás lezárása során: {str(e)}"
        )


@finance_router.get(
    "/daily-closures",
    response_model=List[DailyClosureResponse],
    summary="Napi zárások listázása",
    description="Napi pénztárzárások lekérdezése szűrési feltételekkel.",
    dependencies=[Depends(require_permission("finance:view"))]
)
async def list_daily_closures(
    start_date: Optional[date] = Query(None, description="Kezdő dátum"),
    end_date: Optional[date] = Query(None, description="Záró dátum"),
    status_filter: Optional[str] = Query(None, alias="status", description="Státusz szűrő"),
    limit: int = Query(50, ge=1, le=200, description="Maximum eredmények száma"),
    offset: int = Query(0, ge=0, description="Lapozási eltolás"),
    current_user: Employee = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
) -> List[DailyClosureResponse]:
    """
    Napi zárások listázása.

    **Jogosultság:** `finance:view`

    Args:
        start_date: Kezdő dátum (opcionális)
        end_date: Záró dátum (opcionális)
        status_filter: Státusz szűrő (opcionális)
        limit: Maximum eredmények száma
        offset: Lapozási eltolás
        current_user: Bejelentkezett felhasználó (dependency)
        service: FinanceService instance (dependency)

    Returns:
        List[DailyClosureResponse]: Napi zárások listája

    Raises:
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        closures = service.get_daily_closures(
            start_date=start_date,
            end_date=end_date,
            status=status_filter,
            limit=limit,
            offset=offset
        )

        return [DailyClosureResponse.model_validate(c) for c in closures]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a zárások lekérdezése során: {str(e)}"
        )


@finance_router.get(
    "/daily-closures/by-date/{date}",
    response_model=DailyClosureResponse,
    summary="Napi zárás lekérdezése dátum alapján",
    description="Egy adott dátumhoz tartozó napi zárás részletes adatainak lekérdezése.",
    dependencies=[Depends(require_permission("finance:view"))]
)
async def get_daily_closure_by_date(
    date: date,
    current_user: Employee = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
) -> DailyClosureResponse:
    """
    Napi zárás lekérdezése dátum alapján.

    **Jogosultság:** `finance:view`

    Args:
        date: Dátum (YYYY-MM-DD formátumban)
        current_user: Bejelentkezett felhasználó (dependency)
        service: FinanceService instance (dependency)

    Returns:
        DailyClosureResponse: Napi zárás adatai

    Raises:
        HTTPException 404: Ha a zárás nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        closure = service.get_daily_closure_by_date(date)

        if not closure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Napi zárás nem található a következő dátumra: {date}"
            )

        return DailyClosureResponse.model_validate(closure)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a zárás lekérdezése során: {str(e)}"
        )


@finance_router.get(
    "/daily-closures/{closure_id}",
    response_model=DailyClosureResponse,
    summary="Napi zárás részletei",
    description="Egy adott napi zárás részletes adatainak lekérdezése.",
    dependencies=[Depends(require_permission("finance:view"))]
)
async def get_daily_closure(
    closure_id: int,
    current_user: Employee = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service)
) -> DailyClosureResponse:
    """
    Napi zárás részleteinek lekérdezése.

    **Jogosultság:** `finance:view`

    Args:
        closure_id: Zárás azonosító
        current_user: Bejelentkezett felhasználó (dependency)
        service: FinanceService instance (dependency)

    Returns:
        DailyClosureResponse: Napi zárás adatai

    Raises:
        HTTPException 404: Ha a zárás nem található
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        closure = service.get_daily_closure_by_id(closure_id)

        if not closure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Napi zárás nem található: {closure_id}"
            )

        return DailyClosureResponse.model_validate(closure)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a zárás lekérdezése során: {str(e)}"
        )
