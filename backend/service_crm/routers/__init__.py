"""
CRM Service Routers Package

FastAPI routers a CRM szolgáltatáshoz.
"""

from backend.service_crm.routers.customer_router import customers_router
from backend.service_crm.routers.coupon_router import coupons_router
from backend.service_crm.routers.gift_card_router import gift_cards_router
from backend.service_crm.routers.address_router import addresses_router

__all__ = [
    "customers_router",
    "coupons_router",
    "gift_cards_router",
    "addresses_router",
]
