"""
Service Layer - Business Logic
Module 1: Rendeléskezelés és Asztalok

Ez a modul exportálja az összes service osztályt és példányt.
A service réteg felelQs az üzleti logika végrehajtásáért és a modell réteg feletti absztrakcióért.
"""

from backend.service_orders.services.table_service import TableService, table_service
from backend.service_orders.services.seat_service import SeatService, seat_service

__all__ = [
    # Table Service
    'TableService',
    'table_service',

    # Seat Service
    'SeatService',
    'seat_service',
]
