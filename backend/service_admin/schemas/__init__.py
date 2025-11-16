"""
Pydantic schemas for the Service Admin module (Module 8).

This package contains all request/response schemas for the POS Service Admin,
including:
- NTAK (National Tourism Data Service Center) data submission schemas
  for mandatory Hungarian tax and tourism reporting compliance
- RBAC (Role-Based Access Control) schemas for employee, role, and permission management
- Authentication schemas for login and token management

Usage:
    from backend.service_admin.schemas import (
        # NTAK schemas
        NTAKLineItem,
        NTAKPayment,
        NTAKOrderSummaryData,
        NTAKResponse,
        NTAKSendRequest,
        NTAKStatusResponse,
        # Employee schemas
        EmployeeCreate,
        EmployeeUpdate,
        EmployeeResponse,
        EmployeeListResponse,
        # Role schemas
        RoleCreate,
        RoleUpdate,
        RoleResponse,
        RoleWithPermissionsResponse,
        RoleListResponse,
        # Permission schemas
        PermissionCreate,
        PermissionUpdate,
        PermissionResponse,
        PermissionListResponse,
        # Auth schemas
        LoginRequest,
        TokenResponse,
        CurrentUser,
        PasswordChangeRequest,
        PasswordResetRequest,
    )
"""

# NTAK schemas
from .ntak import (
    NTAKLineItem,
    NTAKPayment,
    NTAKOrderSummaryData,
    NTAKResponse,
    NTAKSendRequest,
    NTAKStatusResponse,
)

# Employee schemas
from .employee import (
    EmployeeBase,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeInDB,
    EmployeeResponse,
    EmployeeListResponse,
)

# Role schemas
from .role import (
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleInDB,
    RoleResponse,
    RoleWithPermissionsResponse,
    RoleListResponse,
)

# Permission schemas
from .permission import (
    PermissionBase,
    PermissionCreate,
    PermissionUpdate,
    PermissionInDB,
    PermissionResponse,
    PermissionListResponse,
)

# Auth schemas
from .auth import (
    LoginRequest,
    TokenResponse,
    CurrentUser,
    PasswordChangeRequest,
    PasswordResetRequest,
)

__all__ = [
    # NTAK
    "NTAKLineItem",
    "NTAKPayment",
    "NTAKOrderSummaryData",
    "NTAKResponse",
    "NTAKSendRequest",
    "NTAKStatusResponse",
    # Employee
    "EmployeeBase",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeInDB",
    "EmployeeResponse",
    "EmployeeListResponse",
    # Role
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleInDB",
    "RoleResponse",
    "RoleWithPermissionsResponse",
    "RoleListResponse",
    # Permission
    "PermissionBase",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionInDB",
    "PermissionResponse",
    "PermissionListResponse",
    # Auth
    "LoginRequest",
    "TokenResponse",
    "CurrentUser",
    "PasswordChangeRequest",
    "PasswordResetRequest",
]
