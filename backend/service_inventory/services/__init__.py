"""
Service layer for Inventory Management (Module 5).

This module exports all service classes for the inventory system.
"""

from backend.service_inventory.services.daily_inventory_service import DailyInventoryService

__all__ = [
    "DailyInventoryService",
]
