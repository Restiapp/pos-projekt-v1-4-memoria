"""
Routers module for Admin Service (Module 8 & Module 6).

This module exports all API routers for endpoint registration.
Includes both Module 8 (NTAK/Internal) and Module 6 (RBAC) routers.
"""

from backend.service_admin.routers.internal import internal_router
from backend.service_admin.routers.employees import employees_router
from backend.service_admin.routers.roles import roles_router
from backend.service_admin.routers.permissions import permissions_router
from backend.service_admin.routers.auth import auth_router
from backend.service_admin.routers.finance import finance_router
from backend.service_admin.routers.integrations import integrations_router
from backend.service_admin.routers.asset_router import asset_router
from backend.service_admin.routers.vehicle_router import vehicle_router

__all__ = [
    # Internal Router (Module 8 - NTAK)
    "internal_router",

    # Employee Router (Module 6 - Phase 4.1)
    "employees_router",

    # Role Router (Module 6 - Phase 4.2)
    "roles_router",

    # Permission Router (Module 6 - Phase 4.3)
    "permissions_router",

    # Auth Router (Module 6 - Phase 4.4)
    "auth_router",

    # Finance Router (Module 8 - V3.0 Phase 1)
    "finance_router",

    # Integrations Router (Module 8 - V3.0 Phase 1)
    "integrations_router",

    # Asset Router (Module 8 - V3.0 Phase 3.2)
    "asset_router",

    # Vehicle Router (Module 8 - V3.0 Phase 3.4)
    "vehicle_router",
]
