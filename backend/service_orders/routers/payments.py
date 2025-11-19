"""
Payment Router - FastAPI Endpoints for Payment Management
Module 4: Fizetések és Split Payment

Ez a router felelős a fizetések REST API végpontjaiért, beleértve:
- GET /payments/methods - Elérhető fizetési módok lekérdezése
- POST /orders/{id}/payments - Split payment támogatás (egy vagy több fizetés)

Sprint 2 - Task A5: Payment API + Split Fizetés
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.service_orders.models.database import get_db
from backend.service_orders.services.payment_service import PaymentService
from backend.service_orders.schemas.payment import (
    PaymentMethodsResponse,
    SplitPaymentRequest,
    SplitPaymentResponse,
)

# Router létrehozása
payments_router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    responses={404: {"description": "Not found"}}
)


@payments_router.get(
    "/methods",
    response_model=PaymentMethodsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available payment methods",
    description="""
    Retrieve a list of all available payment methods supported by the POS system.

    Returns payment methods with their codes and display names:
    - cash: Készpénz
    - card: Bankkártya
    - szep_card: SZÉP kártya
    - transfer: Átutalás
    - voucher: Utalvány

    This endpoint does not require authentication and can be used by frontend
    applications to populate payment method selection dropdowns.
    """
)
def get_payment_methods() -> PaymentMethodsResponse:
    """
    Get all available payment methods.

    Returns:
        PaymentMethodsResponse: List of available payment methods

    Example response:
        {
            "methods": [
                {
                    "code": "cash",
                    "display_name": "Készpénz",
                    "enabled": true
                },
                {
                    "code": "card",
                    "display_name": "Bankkártya",
                    "enabled": true
                }
            ]
        }
    """
    return PaymentService.get_payment_methods()
