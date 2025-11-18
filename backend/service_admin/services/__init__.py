"""
Services module for Admin Service (Module 6 & 8).

This module provides business logic services for the Admin Service,
including NTAK data submission, reporting functionality, audit logging,
employee management, authentication/authorization, and RBAC (Role-Based Access Control).

This module exports all service classes for business logic operations.
"""

from backend.service_admin.services.ntak_service import NtakService, ntak_service
from backend.service_admin.services.audit_log_service import AuditLogService
from backend.service_admin.services.employee_service import EmployeeService
from backend.service_admin.services.role_service import RoleService
from backend.service_admin.services.permission_service import PermissionService
from backend.service_admin.services.auth_service import AuthService, get_auth_service
from backend.service_admin.services.finance_service import FinanceService
from backend.service_admin.services.szamlazz_hu_service import SzamlazzHuService, get_szamlazz_hu_service
from backend.service_admin.services.asset_service import AssetManagementService
from backend.service_admin.services.vehicle_service import VehicleManagementService

__all__ = [
    # NTAK Service (Module 8 - Phase 4.1)
    "NtakService",
    "ntak_service",

    # Audit Log Service (Module 8 - Phase 4.5)
    "AuditLogService",

    # Employee Service (Module 6 - Phase 3.1)
    "EmployeeService",

    # Auth Service (Module 6 - Phase 3.2)
    "AuthService",
    "get_auth_service",

    # RBAC Services (Module 6 - Phase 3.3, 3.4)
    "RoleService",
    "PermissionService",

    # Finance Service (Module 8 - V3.0 Phase 1)
    "FinanceService",

    # Számlázz.hu Service (Module 8 - V3.0 Phase 1)
    "SzamlazzHuService",
    "get_szamlazz_hu_service",

    # Asset Management Service (Module 8 - V3.0 Phase 3.2)
    "AssetManagementService",

    # Vehicle Management Service (Module 8 - V3.0 Phase 3.4)
    "VehicleManagementService",
]
