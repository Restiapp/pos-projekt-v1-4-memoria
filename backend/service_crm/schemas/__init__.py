"""
CRM Service Schemas Package

Pydantic schemas a CRM szolgáltatáshoz.
"""

from backend.service_crm.schemas.customer import (
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    CustomerInDB,
    CustomerResponse,
    CustomerListResponse,
    LoyaltyPointsUpdate
)
from backend.service_crm.schemas.address import (
    AddressTypeEnum,
    AddressBase,
    AddressCreate,
    AddressUpdate,
    AddressInDB,
    AddressResponse,
    AddressListResponse
)
from backend.service_crm.schemas.coupon import (
    DiscountTypeEnum,
    CouponBase,
    CouponCreate,
    CouponUpdate,
    CouponInDB,
    CouponResponse,
    CouponListResponse,
    CouponValidationRequest,
    CouponValidationResponse
)

__all__ = [
    # Customer schemas
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerInDB",
    "CustomerResponse",
    "CustomerListResponse",
    "LoyaltyPointsUpdate",
    # Address schemas
    "AddressTypeEnum",
    "AddressBase",
    "AddressCreate",
    "AddressUpdate",
    "AddressInDB",
    "AddressResponse",
    "AddressListResponse",
    # Coupon schemas
    "DiscountTypeEnum",
    "CouponBase",
    "CouponCreate",
    "CouponUpdate",
    "CouponInDB",
    "CouponResponse",
    "CouponListResponse",
    "CouponValidationRequest",
    "CouponValidationResponse",
]
