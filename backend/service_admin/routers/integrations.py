"""
Integrations Router - Külső rendszer integrációk API végpontok
Module 8: Admin - Integrations (V3.0 Phase 1)

Ez a router felelős a külső rendszerekkel való integrációkért:
- Számlázz.hu API integráció
- Egyéb külső rendszerek (később bővíthető)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_admin.models.database import get_db
from backend.service_admin.models.employee import Employee
from backend.service_admin.services.szamlazz_hu_service import (
    SzamlazzHuService,
    get_szamlazz_hu_service
)
from backend.service_admin.schemas.finance import (
    SzamlazzHuInvoiceRequest,
    SzamlazzHuInvoiceResponse
)
from backend.service_admin.dependencies import require_permission, get_current_user
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Router Initialization
# ============================================================================

integrations_router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"]
)


# ============================================================================
# Számlázz.hu Integration Endpoints
# ============================================================================

@integrations_router.post(
    "/szamlazz_hu/create-invoice",
    response_model=SzamlazzHuInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Számla létrehozása Számlázz.hu-n",
    description="Számla létrehozása a Számlázz.hu rendszerben (MOCK implementáció).",
    dependencies=[Depends(require_permission("finance:manage"))]
)
async def create_szamlazz_hu_invoice(
    request: SzamlazzHuInvoiceRequest,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SzamlazzHuInvoiceResponse:
    """
    Számla létrehozása a Számlázz.hu rendszerben.

    **MOCK IMPLEMENTÁCIÓ** - Nem végez valódi API hívást.

    **Jogosultság:** `finance:manage`

    Args:
        request: Számla adatok (SzamlazzHuInvoiceRequest schema)
        current_user: Bejelentkezett felhasználó (dependency)
        db: Database session (dependency)

    Returns:
        SzamlazzHuInvoiceResponse: Számla létrehozás eredménye

    Raises:
        HTTPException 400: Ha az adatok hibásak
        HTTPException 403: Ha nincs jogosultság
        HTTPException 500: Ha hiba történt a számla létrehozása során

    Example:
        ```json
        {
            "order_id": 123,
            "customer_name": "Kovács János",
            "customer_email": "kovacs@example.com",
            "items": [
                {
                    "name": "Pizza Margherita",
                    "quantity": 2,
                    "unit": "db",
                    "unit_price": 1500.00,
                    "vat_rate": 27.0
                }
            ],
            "payment_method": "CASH",
            "notes": "Kiszállítás: 18:00"
        }
        ```
    """
    try:
        # Validáció: Ellenőrizzük hogy van-e legalább egy tétel
        if not request.items or len(request.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A számlának tartalmaznia kell legalább egy tételt"
            )

        # Inicializáljuk a Számlázz.hu service-t (MOCK)
        szamlazz_service = get_szamlazz_hu_service(test_mode=True)

        # Logoljuk a műveletet
        logger.info(
            f"Creating Számlázz.hu invoice - Order ID: {request.order_id}, "
            f"Customer: {request.customer_name}, "
            f"Items count: {len(request.items)}, "
            f"User: {current_user.username}"
        )

        # Számla létrehozása a Számlázz.hu service-en keresztül
        response = szamlazz_service.create_invoice(request)

        # Logoljuk az eredményt
        if response.success:
            logger.info(
                f"Számlázz.hu invoice created successfully - "
                f"Invoice Number: {response.invoice_number}, "
                f"Order ID: {response.order_id}"
            )
        else:
            logger.error(
                f"Számlázz.hu invoice creation failed - "
                f"Order ID: {response.order_id}, "
                f"Message: {response.message}"
            )

        return response

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating Számlázz.hu invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a számla létrehozása során: {str(e)}"
        )


@integrations_router.post(
    "/szamlazz_hu/cancel-invoice",
    summary="Számla stornózása Számlázz.hu-n",
    description="Számla stornózása a Számlázz.hu rendszerben (MOCK implementáció).",
    dependencies=[Depends(require_permission("finance:manage"))]
)
async def cancel_szamlazz_hu_invoice(
    invoice_number: str,
    current_user: Employee = Depends(get_current_user)
) -> dict:
    """
    Számla stornózása a Számlázz.hu rendszerben.

    **MOCK IMPLEMENTÁCIÓ** - Nem végez valódi API hívást.

    **Jogosultság:** `finance:manage`

    Args:
        invoice_number: Számla azonosító
        current_user: Bejelentkezett felhasználó (dependency)

    Returns:
        dict: Stornózás eredménye

    Raises:
        HTTPException 400: Ha a számlaszám hiányzik
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        if not invoice_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A számlaszám megadása kötelező"
            )

        # Inicializáljuk a Számlázz.hu service-t (MOCK)
        szamlazz_service = get_szamlazz_hu_service(test_mode=True)

        # Logoljuk a műveletet
        logger.info(
            f"Cancelling Számlázz.hu invoice - "
            f"Invoice Number: {invoice_number}, "
            f"User: {current_user.username}"
        )

        # Számla stornózása
        result = szamlazz_service.cancel_invoice(invoice_number)

        logger.info(
            f"Számlázz.hu invoice cancelled - "
            f"Invoice Number: {invoice_number}, "
            f"Cancellation Number: {result.get('cancellation_number')}"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling Számlázz.hu invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a számla stornózása során: {str(e)}"
        )


@integrations_router.get(
    "/szamlazz_hu/invoice/{invoice_number}/pdf",
    summary="Számla PDF letöltése",
    description="Számla PDF letöltése a Számlázz.hu rendszerből (MOCK implementáció).",
    dependencies=[Depends(require_permission("finance:view"))]
)
async def get_szamlazz_hu_invoice_pdf(
    invoice_number: str,
    current_user: Employee = Depends(get_current_user)
) -> dict:
    """
    Számla PDF URL lekérdezése.

    **MOCK IMPLEMENTÁCIÓ** - Visszaad egy mock PDF URL-t.

    **Jogosultság:** `finance:view`

    Args:
        invoice_number: Számla azonosító
        current_user: Bejelentkezett felhasználó (dependency)

    Returns:
        dict: PDF URL

    Raises:
        HTTPException 400: Ha a számlaszám hiányzik
        HTTPException 403: Ha nincs jogosultság
    """
    try:
        if not invoice_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A számlaszám megadása kötelező"
            )

        # Inicializáljuk a Számlázz.hu service-t (MOCK)
        szamlazz_service = get_szamlazz_hu_service(test_mode=True)

        # PDF URL lekérdezése
        pdf_url = szamlazz_service.get_invoice_pdf(invoice_number)

        logger.info(
            f"Retrieved Számlázz.hu invoice PDF - "
            f"Invoice Number: {invoice_number}, "
            f"User: {current_user.username}"
        )

        return {
            "invoice_number": invoice_number,
            "pdf_url": pdf_url,
            "message": "PDF URL sikeresen lekérdezve (MOCK)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Számlázz.hu invoice PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba történt a PDF lekérdezése során: {str(e)}"
        )


@integrations_router.get(
    "/szamlazz_hu/health",
    summary="Számlázz.hu kapcsolat ellenőrzése",
    description="Számlázz.hu API kapcsolat ellenőrzése (MOCK implementáció).",
    dependencies=[Depends(require_permission("finance:view"))]
)
async def check_szamlazz_hu_health(
    current_user: Employee = Depends(get_current_user)
) -> dict:
    """
    Számlázz.hu API kapcsolat ellenőrzése.

    **MOCK IMPLEMENTÁCIÓ** - Mindig sikeres választ ad.

    **Jogosultság:** `finance:view`

    Args:
        current_user: Bejelentkezett felhasználó (dependency)

    Returns:
        dict: Kapcsolat státusz
    """
    try:
        # Inicializáljuk a Számlázz.hu service-t (MOCK)
        szamlazz_service = get_szamlazz_hu_service(test_mode=True)

        # Kapcsolat ellenőrzése
        is_connected = szamlazz_service.check_connection()

        return {
            "service": "Számlázz.hu",
            "status": "connected" if is_connected else "disconnected",
            "mode": "MOCK",
            "message": "Számlázz.hu API kapcsolat aktív (MOCK implementáció)"
        }

    except Exception as e:
        logger.error(f"Error checking Számlázz.hu health: {str(e)}")
        return {
            "service": "Számlázz.hu",
            "status": "error",
            "mode": "MOCK",
            "message": f"Hiba történt: {str(e)}"
        }
