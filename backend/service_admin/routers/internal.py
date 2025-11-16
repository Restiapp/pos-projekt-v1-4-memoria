"""
Internal Router - Belső API végpontok
Module 8: Adminisztráció és NTAK - V. Fázis

Ez a router felelős a belső mikroszolgáltatás-kommunikációért,
különösen az NTAK rendelésjelentések és audit naplózás kezeléséért.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import httpx
import logging

from backend.service_admin.models.database import get_db
from backend.service_admin.services import AuditLogService
from backend.service_admin.config import settings
from backend.service_admin.schemas.ntak import (
    NTAKOrderSummaryData,
    NTAKResponse,
    NTAKSendRequest
)

# Configure logger
logger = logging.getLogger(__name__)

# Initialize router
internal_router = APIRouter(
    prefix="/internal",
    tags=["Internal API"]
)


# Dependency: AuditLogService factory
def get_audit_service(db: Session = Depends(get_db)) -> AuditLogService:
    """
    Dependency injection az AuditLogService-hez.

    Args:
        db: SQLAlchemy Session dependency

    Returns:
        AuditLogService: Inicializált service instance
    """
    return AuditLogService(db)


# ============================================
# V.1 - Kritikus NTAK Rendelésjelentés Végpont
# ============================================

@internal_router.post(
    "/report-order/{order_id}",
    response_model=NTAKResponse,
    status_code=status.HTTP_200_OK,
    summary="NTAK Rendelésjelentés",
    description="Belső végpont rendelés NTAK-hoz való jelentéséhez. "
                "Ezt a végpontot az Orders Service hívja meg, amikor egy rendelés lezárul."
)
async def report_order_to_ntak(
    order_id: int,
    request: Request,
    send_request: Optional[NTAKSendRequest] = None,
    audit_service: AuditLogService = Depends(get_audit_service),
    db: Session = Depends(get_db)
) -> NTAKResponse:
    """
    Kritikus végpont: Rendelés jelentése NTAK-hoz.

    Ez a végpont:
    1. Lekéri a rendelés adatait az Orders Service-ből
    2. Átalakítja NTAK formátumba
    3. Elküldi az NTAK API-nak
    4. Naplózza az eredményt az audit logba

    Args:
        order_id: Rendelés egyedi azonosítója
        request: FastAPI Request objektum (IP cím, user agent)
        send_request: Opcionális küldési paraméterek
        audit_service: AuditLogService dependency
        db: Database session

    Returns:
        NTAKResponse: NTAK API válasz

    Raises:
        HTTPException: 404 ha a rendelés nem található
        HTTPException: 500 ha NTAK küldés sikertelen
    """
    logger.info(f"NTAK rendelésjelentés kezdeményezve - order_id: {order_id}")

    # Ha NTAK nincs engedélyezve, csak naplózunk
    if not settings.ntak_enabled:
        logger.warning(f"NTAK szolgáltatás le van tiltva - order_id: {order_id}")

        audit_service.log_event(
            event_type='NTAK_SEND',
            entity_type='ORDER',
            entity_id=order_id,
            status='FAILURE',
            message='NTAK szolgáltatás le van tiltva a konfigurációban',
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent')
        )

        return NTAKResponse(
            success=False,
            message="NTAK szolgáltatás le van tiltva",
            transaction_id=None,
            timestamp=datetime.now(),
            error_code="NTAK_DISABLED"
        )

    try:
        # 1. Lekérjük a rendelés adatait az Orders Service-ből
        logger.info(f"Rendelés adatok lekérése - order_id: {order_id}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            orders_url = f"{settings.orders_service_url}/api/orders/{order_id}"
            response = await client.get(orders_url)

            if response.status_code == 404:
                logger.error(f"Rendelés nem található - order_id: {order_id}")

                audit_service.log_event(
                    event_type='NTAK_SEND',
                    entity_type='ORDER',
                    entity_id=order_id,
                    status='FAILURE',
                    message=f'Rendelés nem található az Orders Service-ben',
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get('user-agent')
                )

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Rendelés nem található: {order_id}"
                )

            response.raise_for_status()
            order_data = response.json()

        # 2. TODO: Átalakítás NTAK formátumba
        #    Ez a későbbi fázisokban kerül implementálásra
        #    Most placeholder adatot használunk
        logger.info(f"Rendelés átalakítása NTAK formátumra - order_id: {order_id}")

        # 3. TODO: NTAK API hívás
        #    Jelenleg mock válasz, később kerül implementálásra
        logger.info(f"NTAK API hívás - order_id: {order_id}")

        # Mock NTAK válasz (később valódi API hívás lesz)
        ntak_transaction_id = f"NTAK-{datetime.now().strftime('%Y%m%d%H%M%S')}-{order_id}"

        ntak_response = NTAKResponse(
            success=True,
            message="Rendelésösszesítő sikeresen elküldve (mock)",
            transaction_id=ntak_transaction_id,
            timestamp=datetime.now(),
            error_code=None
        )

        # 4. Audit log naplózás
        logger.info(f"NTAK küldés sikeres - order_id: {order_id}, tx_id: {ntak_transaction_id}")

        audit_service.log_ntak_send(
            order_id=order_id,
            success=True,
            message=f"NTAK rendelésösszesítő elküldve - TX: {ntak_transaction_id}",
            details={
                "transaction_id": ntak_transaction_id,
                "order_data": order_data,
                "ntak_response": ntak_response.model_dump()
            }
        )

        return ntak_response

    except httpx.HTTPError as e:
        logger.error(f"HTTP hiba a rendelés lekérésekor - order_id: {order_id}, error: {str(e)}")

        audit_service.log_ntak_send(
            order_id=order_id,
            success=False,
            message=f"HTTP hiba az Orders Service kommunikáció során: {str(e)}",
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Orders Service nem elérhető: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Váratlan hiba NTAK küldéskor - order_id: {order_id}, error: {str(e)}")

        audit_service.log_ntak_send(
            order_id=order_id,
            success=False,
            message=f"Váratlan hiba: {str(e)}",
            details={"error": str(e), "error_type": type(e).__name__}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba a NTAK jelentés során: {str(e)}"
        )


# ============================================
# V.2 - NTAK Sztornó Végpont
# ============================================

@internal_router.post(
    "/cancel-order/{order_id}",
    response_model=NTAKResponse,
    status_code=status.HTTP_200_OK,
    summary="NTAK Rendelés Sztornó",
    description="Belső végpont rendelés NTAK sztornójához."
)
async def cancel_order_in_ntak(
    order_id: int,
    request: Request,
    audit_service: AuditLogService = Depends(get_audit_service)
) -> NTAKResponse:
    """
    Rendelés sztornózása NTAK-ban.

    Ez a végpont:
    1. Ellenőrzi, hogy a rendelés korábban be lett-e jelentve NTAK-ba
    2. Elküldi a sztornó kérést az NTAK API-nak
    3. Naplózza az eredményt

    Args:
        order_id: Rendelés egyedi azonosítója
        request: FastAPI Request objektum
        audit_service: AuditLogService dependency

    Returns:
        NTAKResponse: NTAK API válasz
    """
    logger.info(f"NTAK sztornó kezdeményezve - order_id: {order_id}")

    if not settings.ntak_enabled:
        logger.warning(f"NTAK szolgáltatás le van tiltva - order_id: {order_id}")

        audit_service.log_ntak_cancel(
            order_id=order_id,
            success=False,
            message='NTAK szolgáltatás le van tiltva'
        )

        return NTAKResponse(
            success=False,
            message="NTAK szolgáltatás le van tiltva",
            transaction_id=None,
            timestamp=datetime.now(),
            error_code="NTAK_DISABLED"
        )

    try:
        # TODO: NTAK sztornó API hívás implementálása
        # Mock válasz
        cancel_transaction_id = f"NTAK-CANCEL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{order_id}"

        logger.info(f"NTAK sztornó sikeres - order_id: {order_id}, tx_id: {cancel_transaction_id}")

        audit_service.log_ntak_cancel(
            order_id=order_id,
            success=True,
            message=f"NTAK rendelés sztornózva - TX: {cancel_transaction_id}",
            details={"transaction_id": cancel_transaction_id}
        )

        return NTAKResponse(
            success=True,
            message="Rendelés sztornó sikeresen elküldve (mock)",
            transaction_id=cancel_transaction_id,
            timestamp=datetime.now(),
            error_code=None
        )

    except Exception as e:
        logger.error(f"Hiba NTAK sztornókor - order_id: {order_id}, error: {str(e)}")

        audit_service.log_ntak_cancel(
            order_id=order_id,
            success=False,
            message=f"Hiba: {str(e)}",
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba a NTAK sztornó során: {str(e)}"
        )


# ============================================
# V.3 - Audit Log Lekérdezés (Admin/Debug)
# ============================================

@internal_router.get(
    "/audit-logs",
    status_code=status.HTTP_200_OK,
    summary="Audit Log Lekérdezés",
    description="Belső végpont audit logok lekérdezéséhez (admin/debug célokra)."
)
async def get_audit_logs(
    event_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    audit_service: AuditLogService = Depends(get_audit_service)
):
    """
    Audit logok lekérdezése szűrési feltételekkel.

    Args:
        event_type: Szűrés esemény típusra (pl. 'NTAK_SEND')
        entity_type: Szűrés entitás típusra (pl. 'ORDER')
        entity_id: Szűrés entitás ID-ra
        status_filter: Szűrés státuszra ('SUCCESS', 'FAILURE', 'PENDING')
        limit: Max visszaadott rekordok száma
        offset: Lapozás offset
        audit_service: AuditLogService dependency

    Returns:
        dict: Audit logok listája és meta információk
    """
    logger.info(f"Audit logok lekérése - filters: event={event_type}, entity={entity_type}, id={entity_id}")

    try:
        logs = audit_service.get_logs(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status_filter,
            limit=limit,
            offset=offset
        )

        total_count = audit_service.count_logs(
            event_type=event_type,
            status=status_filter
        )

        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "logs": [
                {
                    "id": log.id,
                    "event_type": log.event_type,
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "user_id": log.user_id,
                    "status": log.status,
                    "message": log.message,
                    "details": log.details,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ]
        }

    except Exception as e:
        logger.error(f"Hiba az audit logok lekérésekor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba az audit logok lekérésekor: {str(e)}"
        )


# ============================================
# V.4 - Rendeléshez Tartozó Audit Logok
# ============================================

@internal_router.get(
    "/audit-logs/order/{order_id}",
    status_code=status.HTTP_200_OK,
    summary="Rendelés Audit Log",
    description="Egy adott rendeléshez tartozó összes audit log lekérése."
)
async def get_order_audit_logs(
    order_id: int,
    audit_service: AuditLogService = Depends(get_audit_service)
):
    """
    Egy adott rendeléshez tartozó összes audit log lekérése.

    Args:
        order_id: Rendelés egyedi azonosítója
        audit_service: AuditLogService dependency

    Returns:
        dict: Audit logok listája
    """
    logger.info(f"Rendelés audit logok lekérése - order_id: {order_id}")

    try:
        logs = audit_service.get_order_audit_logs(order_id)

        return {
            "order_id": order_id,
            "log_count": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "event_type": log.event_type,
                    "status": log.status,
                    "message": log.message,
                    "details": log.details,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ]
        }

    except Exception as e:
        logger.error(f"Hiba a rendelés audit logok lekérésekor - order_id: {order_id}, error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hiba az audit logok lekérésekor: {str(e)}"
        )
