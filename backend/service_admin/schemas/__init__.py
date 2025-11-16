"""
Pydantic schemas for the Service Admin module (Module 8).

This package contains all request/response schemas for the POS Service Admin,
including NTAK (National Tourism Data Service Center) data submission schemas
for mandatory Hungarian tax and tourism reporting compliance.

Usage:
    from backend.service_admin.schemas import (
        NTAKLineItem,
        NTAKPayment,
        NTAKOrderSummaryData,
        NTAKResponse,
        NTAKSendRequest,
        NTAKStatusResponse
    )
"""

# NTAK schemas
from .ntak import (
    NTAKLineItem,
    NTAKPayment,
    NTAKOrderSummaryData,
    NTAKResponse,
    NTAKSendRequest,
    NTAKStatusResponse,
)

__all__ = [
    # NTAK
    "NTAKLineItem",
    "NTAKPayment",
    "NTAKOrderSummaryData",
    "NTAKResponse",
    "NTAKSendRequest",
    "NTAKStatusResponse",
]
