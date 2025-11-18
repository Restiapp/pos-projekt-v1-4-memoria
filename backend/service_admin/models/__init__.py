"""
Models Package - SQLAlchemy ORM Models
Module 6 & 8: RBAC + Adminisztráció és NTAK (V3.0 Extended)

Ez a package tartalmazza az összes adatbázis modellt a service_admin-hez.

Importálás:
    from backend.service_admin.models import (
        Base,
        AuditLog,
        Employee,
        Role,
        Permission,
        CashMovement,
        DailyClosure,
        AssetGroup,
        Asset,
        AssetService,
        Vehicle,
        VehicleRefueling,
        VehicleMaintenance
    )
"""

# Import Base first
from backend.service_admin.models.database import Base

# Import all models
from backend.service_admin.models.audit_log import AuditLog
from backend.service_admin.models.employee import Employee, employee_roles
from backend.service_admin.models.role import Role, role_permissions
from backend.service_admin.models.permission import Permission

# V3.0: Finance models
from backend.service_admin.models.finance import (
    CashMovement,
    CashMovementType,
    DailyClosure,
    ClosureStatus
)

# V3.0: Assets models
from backend.service_admin.models.assets import (
    AssetGroup,
    Asset,
    AssetStatus,
    AssetService,
    ServiceType
)

# V3.0: Vehicles models
from backend.service_admin.models.vehicles import (
    Vehicle,
    VehicleStatus,
    FuelType,
    VehicleRefueling,
    VehicleMaintenance,
    MaintenanceType
)

# Export all models
__all__ = [
    # Database
    'Base',
    # RBAC & Audit
    'AuditLog',
    'Employee',
    'Role',
    'Permission',
    'employee_roles',
    'role_permissions',
    # Finance (V3.0)
    'CashMovement',
    'CashMovementType',
    'DailyClosure',
    'ClosureStatus',
    # Assets (V3.0)
    'AssetGroup',
    'Asset',
    'AssetStatus',
    'AssetService',
    'ServiceType',
    # Vehicles (V3.0)
    'Vehicle',
    'VehicleStatus',
    'FuelType',
    'VehicleRefueling',
    'VehicleMaintenance',
    'MaintenanceType',
]
