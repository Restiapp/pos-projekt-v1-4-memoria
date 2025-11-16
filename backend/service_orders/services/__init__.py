"""
Service Layer - Business Logic
Module 1: Rendeléskezelés és Asztalok

Ez a modul exportálja az összes service osztályt és példányt.
A service réteg felelős az üzleti logika végrehajtásáért és a modell réteg feletti absztrakcióért.

Importálás:
    from backend.service_orders.services import TableService, SeatService, OrderService, table_service, seat_service
"""

from backend.service_orders.services.table_service import TableService, table_service
from backend.service_orders.services.seat_service import SeatService, seat_service
from backend.service_orders.services.order_service import OrderService

__all__ = [
    # Table Service
    'TableService',
    'table_service',

    # Seat Service
    'SeatService',
    'seat_service',

    # Order Service
    'OrderService',
]
