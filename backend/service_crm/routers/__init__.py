"""
CRM Service Routers Package

FastAPI routers a CRM szolgáltatáshoz.
"""

from backend.service_crm.routers.customer_router import customers_router
from backend.service_crm.routers.coupon_router import coupons_router

__all__ = [
    "customers_router",
    "coupons_router",
]
