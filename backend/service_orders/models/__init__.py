"""
Models Package - SQLAlchemy ORM Models
Module 1: Rendeléskezelés és Asztalok

Ez a package tartalmazza az összes adatbázis modellt a service_orders-hez.

Importálás:
    from backend.service_orders.models import Table, Seat, Order, OrderItem, Base
"""

# Import Base first
from backend.service_orders.models.database import Base

# Import all models
from backend.service_orders.models.table import Table
from backend.service_orders.models.seat import Seat
from backend.service_orders.models.order import Order
from backend.service_orders.models.order_item import OrderItem

# Export all models
__all__ = [
    'Base',
    'Table',
    'Seat',
    'Order',
    'OrderItem',
]
