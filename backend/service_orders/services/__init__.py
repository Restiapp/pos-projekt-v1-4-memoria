"""
Service Layer - Business Logic
Module 1: Rendeléskezelés és Asztalok

Ez a modul exportálja az összes service osztályt
a rendeléskezelés és asztalkezelés számára.
"""

from backend.service_orders.services.order_item_service import OrderItemService

__all__ = [
    'OrderItemService',
]
