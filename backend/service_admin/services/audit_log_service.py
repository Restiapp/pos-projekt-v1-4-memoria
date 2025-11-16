"""
AuditLogService - Audit naplózás kezelése
Module 8: Adminisztráció és NTAK - IV. Fázis

Ez a service felelős az audit log bejegyzések létrehozásáért és lekérdezéséért.
Támogatja az NTAK adatküldések, rendszeresemények és user action-ök naplózását.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.service_admin.models.audit_log import AuditLog


class AuditLogService:
    """
    Service osztály az audit naplózás kezeléséhez.

    Felelősségek:
    - NTAK adatküldések naplózása (sikeres/sikertelen)
    - Rendszeresemények rögzítése
    - User action-ök követése
    - Audit log lekérdezések
    """

    def __init__(self, db: Session):
        """
        Inicializálja az AuditLogService-t.

        Args:
            db: SQLAlchemy Session objektum dependency injectionből
        """
        self.db = db

    def log_event(
        self,
        event_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: str = "SUCCESS",
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Létrehoz egy új audit log bejegyzést.

        Args:
            event_type: Esemény típusa (pl. 'NTAK_SEND', 'NTAK_CANCEL', 'USER_LOGIN')
            entity_type: Érintett entitás típusa (pl. 'ORDER', 'PAYMENT', 'USER')
            entity_id: Érintett entitás ID-ja
            user_id: Felhasználó ID (ki végezte a műveletet)
            status: Művelet státusza ('SUCCESS', 'FAILURE', 'PENDING')
            message: Rövid leírás az eseményről
            details: Részletes adatok JSONB formátumban (dict)
            ip_address: Kliens IP címe
            user_agent: Kliens user agent string

        Returns:
            AuditLog: A létrehozott audit log objektum

        Example:
            >>> service.log_event(
            ...     event_type='NTAK_SEND',
            ...     entity_type='ORDER',
            ...     entity_id=123,
            ...     status='SUCCESS',
            ...     message='NTAK rendelésösszesítő elküldve',
            ...     details={'transaction_id': 'NTAK-2024-001234'}
            ... )
        """
        audit_log = AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            status=status,
            message=message,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        return audit_log

    def log_ntak_send(
        self,
        order_id: int,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> AuditLog:
        """
        Speciális metódus NTAK adatküldés naplózásához.

        Args:
            order_id: Rendelés ID
            success: Sikeres volt-e a küldés
            message: Státusz üzenet
            details: Részletes információk (NTAK válasz, payload, stb.)
            user_id: Felhasználó ID (opcionális)

        Returns:
            AuditLog: A létrehozott audit log objektum
        """
        return self.log_event(
            event_type='NTAK_SEND',
            entity_type='ORDER',
            entity_id=order_id,
            user_id=user_id,
            status='SUCCESS' if success else 'FAILURE',
            message=message,
            details=details
        )

    def log_ntak_cancel(
        self,
        order_id: int,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> AuditLog:
        """
        Speciális metódus NTAK sztornó naplózásához.

        Args:
            order_id: Rendelés ID
            success: Sikeres volt-e a sztornó
            message: Státusz üzenet
            details: Részletes információk
            user_id: Felhasználó ID (opcionális)

        Returns:
            AuditLog: A létrehozott audit log objektum
        """
        return self.log_event(
            event_type='NTAK_CANCEL',
            entity_type='ORDER',
            entity_id=order_id,
            user_id=user_id,
            status='SUCCESS' if success else 'FAILURE',
            message=message,
            details=details
        )

    def get_logs(
        self,
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Lekéri az audit logokat szűrési feltételekkel.

        Args:
            event_type: Szűrés esemény típusra
            entity_type: Szűrés entitás típusra
            entity_id: Szűrés entitás ID-ra
            user_id: Szűrés felhasználóra
            status: Szűrés státuszra
            limit: Max visszaadott rekordok száma (default: 100)
            offset: Lapozás offset (default: 0)

        Returns:
            List[AuditLog]: Audit log bejegyzések listája
        """
        query = self.db.query(AuditLog)

        # Szűrések alkalmazása
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if status:
            query = query.filter(AuditLog.status == status)

        # Rendezés időbélyeg szerint csökkenő sorrendben (legújabb elől)
        query = query.order_by(desc(AuditLog.created_at))

        # Lapozás
        query = query.limit(limit).offset(offset)

        return query.all()

    def get_order_audit_logs(self, order_id: int) -> List[AuditLog]:
        """
        Lekéri egy adott rendeléshez tartozó összes audit log bejegyzést.

        Args:
            order_id: Rendelés ID

        Returns:
            List[AuditLog]: Az adott rendeléshez tartozó audit logok
        """
        return self.get_logs(entity_type='ORDER', entity_id=order_id)

    def get_ntak_logs(
        self,
        order_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Lekéri az NTAK-hoz kapcsolódó audit logokat.

        Args:
            order_id: Opcionális rendelés ID szűrő
            status: Opcionális státusz szűrő
            limit: Max visszaadott rekordok száma

        Returns:
            List[AuditLog]: NTAK audit logok
        """
        query = self.db.query(AuditLog).filter(
            AuditLog.event_type.in_(['NTAK_SEND', 'NTAK_CANCEL'])
        )

        if order_id:
            query = query.filter(AuditLog.entity_id == order_id)
        if status:
            query = query.filter(AuditLog.status == status)

        query = query.order_by(desc(AuditLog.created_at)).limit(limit)

        return query.all()

    def count_logs(
        self,
        event_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Megszámolja az audit logokat szűrési feltételekkel.

        Args:
            event_type: Opcionális esemény típus szűrő
            status: Opcionális státusz szűrő

        Returns:
            int: Audit logok száma
        """
        query = self.db.query(AuditLog)

        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if status:
            query = query.filter(AuditLog.status == status)

        return query.count()
