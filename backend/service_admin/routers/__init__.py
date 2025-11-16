"""
Routers module for Admin Service (Module 8 & Module 6).

This module exports all API routers for endpoint registration.
Includes both Module 8 (NTAK/Internal) and Module 6 (RBAC) routers.
"""

from backend.service_admin.routers.internal import internal_router
from backend.service_admin.routers.employees import employees_router
from backend.service_admin.routers.roles import roles_router

__all__ = [
    # Internal Router (Module 8 - NTAK)
    "internal_router",

    # Employee Router (Module 6 - Phase 4.1)
    "employees_router",

    # Role Router (Module 6 - Phase 4.2)
    "roles_router",
]
