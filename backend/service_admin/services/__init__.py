"""
Services module for Admin Service (Module 8).

This module provides business logic services for the Admin Service,
including NTAK data submission and reporting functionality.
"""

from backend.service_admin.services.ntak_service import NtakService, ntak_service

__all__ = [
    "NtakService",
    "ntak_service",
]
