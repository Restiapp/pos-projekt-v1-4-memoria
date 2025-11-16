"""
Services module for Admin Service (Module 6 & 8).

This module provides business logic services for the Admin Service,
including NTAK data submission, reporting functionality, audit logging,
employee management, and RBAC (Role-Based Access Control).

This module exports all service classes for business logic operations.
"""

from backend.service_admin.services.ntak_service import NtakService, ntak_service
from backend.service_admin.services.audit_log_service import AuditLogService
from backend.service_admin.services.employee_service import EmployeeService
from backend.service_admin.services.role_service import RoleService
from backend.service_admin.services.permission_service import PermissionService

__all__ = [
    # NTAK Service (Module 8 - Phase 4.1)
    "NtakService",
    "ntak_service",

    # Audit Log Service (Module 8 - Phase 4.5)
    "AuditLogService",

    # Employee Service (Module 6 - Phase 3.1)
    "EmployeeService",

    # RBAC Services (Module 6 - Phase 3.3, 3.4)
    "RoleService",
    "PermissionService",
]
