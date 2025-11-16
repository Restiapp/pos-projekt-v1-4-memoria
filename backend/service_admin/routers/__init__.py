"""
Routers module for Admin Service (Module 6 & 8).

This module exports all API routers for endpoint registration.
"""

from backend.service_admin.routers.internal import internal_router
from backend.service_admin.routers.auth import auth_router

__all__ = ['internal_router', 'auth_router']
