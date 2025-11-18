"""
CRM Service Business Logic Package

Service layer osztályok a CRM szolgáltatáshoz.
"""

from backend.service_crm.services.customer_service import CustomerService
from backend.service_crm.services.coupon_service import CouponService
from backend.service_crm.services.gift_card_service import GiftCardService
from backend.service_crm.services.address_service import AddressService

__all__ = [
    "CustomerService",
    "CouponService",
    "GiftCardService",
    "AddressService",
]
