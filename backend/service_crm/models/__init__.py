"""
CRM Service Models Package

Az összes CRM szolgáltatáshoz kapcsolódó SQLAlchemy modell.
"""

from backend.service_crm.models.database import Base, get_db, init_db, drop_all_tables
from backend.service_crm.models.customer import Customer
from backend.service_crm.models.address import Address
from backend.service_crm.models.coupon import Coupon
from backend.service_crm.models.gift_card import GiftCard

__all__ = [
    'Base',
    'get_db',
    'init_db',
    'drop_all_tables',
    'Customer',
    'Address',
    'Coupon',
    'GiftCard',
]
