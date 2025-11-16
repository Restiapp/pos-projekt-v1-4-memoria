"""
Models Package - SQLAlchemy ORM Models
Module 8: Adminisztráció és NTAK

Ez a package tartalmazza az összes adatbázis modellt a service_admin-hez.

Importálás:
    from backend.service_admin.models import (
        Base,
        AuditLog
    )
"""

# Import Base first
from backend.service_admin.models.database import Base

# Import all models
from backend.service_admin.models.audit_log import AuditLog

# Export all models
__all__ = [
    'Base',
    'AuditLog',
]
