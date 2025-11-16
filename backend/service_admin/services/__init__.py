"""
Services module for Admin Service (Module 6 & 8).

This module provides business logic services for the Admin Service,
including RBAC (Role & Permission), NTAK data submission, reporting
functionality, and audit logging.

This module exports all service classes for business logic operations.
"""

from backend.service_admin.services.ntak_service import NtakService, ntak_service
from backend.service_admin.services.audit_log_service import AuditLogService
from backend.service_admin.services.role_service import RoleService
from backend.service_admin.services.permission_service import PermissionService

__all__ = [
    # NTAK Service (Phase 4.1)
    "NtakService",
    "ntak_service",

    # Audit Log Service (Phase 4.5)
    "AuditLogService",

    # RBAC Services (Module 6 - Phase 3.3, 3.4)
    "RoleService",
    "PermissionService",
]
