"""
Routers module for Admin Service (Module 8).

This module exports all API routers for endpoint registration.
"""

from backend.service_admin.routers.internal import internal_router
from backend.service_admin.routers.roles import roles_router

__all__ = ['internal_router', 'roles_router']
