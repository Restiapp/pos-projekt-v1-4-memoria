"""
Service Layer - Business Logic
Module 1: Rendeléskezelés és Asztalok
Module 4: Fizetések

Ez a modul exportálja az összes service osztályt és példányt.
A service réteg felelős az üzleti logika végrehajtásáért és a modell réteg feletti absztrakcióért.

Importálás:
    from backend.service_orders.services import (
        TableService, SeatService, OrderService, OrderItemService, PaymentService,
        table_service, seat_service
    )
"""

from backend.service_orders.services.table_service import TableService, table_service
from backend.service_orders.services.seat_service import SeatService, seat_service
from backend.service_orders.services.order_service import OrderService
from backend.service_orders.services.order_item_service import OrderItemService
from backend.service_orders.services.payment_service import PaymentService

__all__ = [
    # Table Service
    'TableService',
    'table_service',

    # Seat Service
    'SeatService',
    'seat_service',

    # Order Service
    'OrderService',

    # OrderItem Service
    'OrderItemService',

    # Payment Service (Module 4, Phase 4.6-4.8)
    'PaymentService',
]
