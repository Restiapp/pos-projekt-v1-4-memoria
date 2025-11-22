"""
Models Package - SQLAlchemy ORM Models
Module 1: Rendeléskezelés és Asztalok
Module 4: Fizetések

Ez a package tartalmazza az összes adatbázis modellt a service_orders-hez.

Importálás:
    from backend.service_orders.models import Table, Seat, Order, OrderItem, Payment, Base, Room
"""

# Import Base first
from backend.service_orders.models.database import Base

# Import all models
from backend.service_orders.models.room import Room
from backend.service_orders.models.table import Table
from backend.service_orders.models.seat import Seat
from backend.service_orders.models.order import Order
from backend.service_orders.models.order_item import OrderItem
from backend.service_orders.models.payment import Payment
from backend.service_orders.models.reservation import Reservation, ReservationStatus, ReservationSource
from backend.service_orders.models.opening_hours import OpeningHours
from backend.service_orders.models.room import Room

# Export all models
__all__ = [
    'Base',
    'Room',
    'Table',
    'Seat',
    'Order',
    'OrderItem',
    'Payment',
    'Reservation',
    'ReservationStatus',
    'ReservationSource',
    'OpeningHours',
    'Room',
]
