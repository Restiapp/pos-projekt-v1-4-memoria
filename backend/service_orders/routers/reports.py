"""
Reports Router - Daily Payments Reporting
Module 4: Fizetések és Számla Kezelés

Ez a router felelős a pénzügyi riportok API végpontjaiért,
különös tekintettel a napi pénztárzáráshoz szükséges fizetési összegzésekre.
"""

from datetime import date
from typing import Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.services.payment_service import PaymentService

# Router létrehozása
reports_router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"]
)


@reports_router.get(
    "/daily-payments",
    response_model=Dict[str, float],
    summary="Napi fizetések összegzése fizetési mód szerint",
    description="""
    Visszaadja egy adott nap összes sikeres fizetését fizetési módok szerint csoportosítva.

    Ez az endpoint támogatja a service_admin napi pénztárzárás funkcióját,
    amely a close_daily_closure művelet során meghívja ezt az endpointot,
    hogy megkapja a fizetési módok szerinti bevételi bontást.

    **Példa válasz:**
    ```json
    {
        "KESZPENZ": 10000.00,
        "KARTYA": 5000.00,
        "SZEP_KARTYA": 2000.00
    }
    ```

    **Használat:**
    - Ha nincs megadva dátum, az aktuális nap fizetéseit adja vissza
    - A query paraméterben ISO formátumú dátumot várunk (YYYY-MM-DD)
    - Csak SIKERES státuszú fizetéseket veszi figyelembe
    """
)
async def get_daily_payments(
    target_date: date = Query(
        default=None,
        description="A dátum, amelyre az összegzést kérjük (ISO formátum: YYYY-MM-DD). Ha nincs megadva, az aktuális napot használja.",
        example="2024-01-15"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, float]:
    """
    Napi fizetések összegzése fizetési mód szerint.

    Args:
        target_date: A célzott dátum (ha nincs megadva, az aktuális nap)
        db: Database session (dependency injection)

    Returns:
        Dict[str, float]: Fizetési módok szerinti összegzés
        Példa: {"KESZPENZ": 10000.00, "KARTYA": 5000.00}
    """
    # Ha nincs megadva dátum, használjuk az aktuális napot
    if target_date is None:
        target_date = date.today()

    # PaymentService meghívása az összegzéshez
    payment_summary = PaymentService.get_daily_payment_summary(db, target_date)

    return payment_summary
