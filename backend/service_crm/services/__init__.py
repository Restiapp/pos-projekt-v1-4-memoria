"""
CRM Service Business Logic Package

Service layer osztályok a CRM szolgáltatáshoz.
"""

from backend.service_crm.services.customer_service import CustomerService
from backend.service_crm.services.coupon_service import CouponService

__all__ = [
    "CustomerService",
    "CouponService",
]
