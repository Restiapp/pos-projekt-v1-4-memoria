"""
Services Package - Business Logic Layer
Module 1: Rendeléskezelés és Asztalok

Ez a package tartalmazza az összes service osztályt a service_orders-hez.

Importálás:
    from backend.service_orders.services import OrderService
"""

from backend.service_orders.services.order_service import OrderService

__all__ = [
    'OrderService',
]
