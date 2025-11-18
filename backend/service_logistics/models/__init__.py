"""
Models Package for Logistics Service
V3.0: Kiszállítási Szolgáltatás

Ez a package tartalmazza az összes SQLAlchemy modellt a Logistics Service-hez.
"""

from backend.service_logistics.models.database import Base, get_db, init_db
from backend.service_logistics.models.delivery_zone import DeliveryZone
from backend.service_logistics.models.courier import Courier

__all__ = [
    'Base',
    'get_db',
    'init_db',
    'DeliveryZone',
    'Courier',
]
