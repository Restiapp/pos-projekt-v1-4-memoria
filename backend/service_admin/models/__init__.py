"""
Models Package - SQLAlchemy ORM Models
Module 6 & 8: RBAC + Adminisztráció és NTAK

Ez a package tartalmazza az összes adatbázis modellt a service_admin-hez.

Importálás:
    from backend.service_admin.models import (
        Base,
        AuditLog,
        Employee,
        Role,
        Permission
    )
"""

# Import Base first
from backend.service_admin.models.database import Base

# Import all models
from backend.service_admin.models.audit_log import AuditLog
from backend.service_admin.models.employee import Employee, employee_roles
from backend.service_admin.models.role import Role, role_permissions
from backend.service_admin.models.permission import Permission

# Export all models
__all__ = [
    'Base',
    'AuditLog',
    'Employee',
    'Role',
    'Permission',
    'employee_roles',
    'role_permissions',
]
