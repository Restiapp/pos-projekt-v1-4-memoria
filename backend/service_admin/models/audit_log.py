"""
AuditLog Model - SQLAlchemy ORM
Module 8: Adminisztráció és NTAK

NTAK és adminisztratív műveletek naplózása.
Minden NTAK adatküldés, sztornó, és kritikus rendszeresemény naplózása.
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Index
from sqlalchemy.sql import func

from backend.service_admin.models.database import Base, CompatibleJSON


class AuditLog(Base):
    """
    Audit Log modell NTAK és adminisztratív műveletek naplózásához.

    Támogatja:
    - NTAK adatküldések naplózása (sikeresség, hiba)
    - Rendszeresemények követése (user actions, system events)
    - Hibakeresés és compliance auditálás
    - IP címek és user agent információk tárolása
    """
    __tablename__ = 'ntak_audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Esemény típusa: 'NTAK_SEND', 'NTAK_CANCEL', 'USER_LOGIN', 'SYSTEM_ERROR', etc.
    event_type = Column(String(100), nullable=False, index=True)

    # Érintett entitás típusa: 'ORDER', 'PAYMENT', 'USER', 'SYSTEM', etc.
    entity_type = Column(String(100), nullable=True)

    # Érintett entitás ID-ja
    entity_id = Column(Integer, nullable=True)

    # Felhasználó ID (ki végezte a műveletet)
    user_id = Column(Integer, nullable=True)

    # Művelet státusza: 'SUCCESS', 'FAILURE', 'PENDING'
    status = Column(String(50), nullable=False, default='SUCCESS')

    # Rövid leírás
    message = Column(Text, nullable=True)

    # Részletes adatok JSON formátumban
    # Pl. NTAK válasz, request payload, error details
    # PostgreSQL: JSONB, SQLite: TEXT with JSON serialization
    details = Column(CompatibleJSON, nullable=True)

    # Hálózati információk
    ip_address = Column(String(45), nullable=True)  # IPv6 support (45 chars)
    user_agent = Column(Text, nullable=True)

    # Automatikus időbélyeg
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )

    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, "
            f"event_type='{self.event_type}', "
            f"entity_type='{self.entity_type}', "
            f"status='{self.status}', "
            f"created_at={self.created_at})>"
        )


# Indexek a gyakori lekérdezésekhez
Index('idx_audit_event_entity', AuditLog.event_type, AuditLog.entity_type)
Index('idx_audit_user_created', AuditLog.user_id, AuditLog.created_at.desc())
Index('idx_audit_status_created', AuditLog.status, AuditLog.created_at.desc())
