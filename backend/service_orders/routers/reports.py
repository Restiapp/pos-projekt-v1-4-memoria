"""
Reports Router - FastAPI Endpoints for Payment Reports
Module 1: Rendeléskezelés és Asztalok

Ez a router felelős a riport végpontokért, beleértve:
- Napi fizetési összesítők
- Fizetési módok szerinti bontás
"""

from typing import Dict, Optional
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.service_orders.models.database import get_db
from backend.service_orders.models.payment import Payment
from backend.service_orders.models.order import Order
from pydantic import BaseModel, Field


# Router létrehozása
reports_router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    responses={404: {"description": "Report not found"}}
)


class DailyPaymentSummary(BaseModel):
    """Schema for daily payment summary response."""

    date: date = Field(
        ...,
        description="Report date"
    )
    payment_summary: Dict[str, float] = Field(
        ...,
        description="Payment breakdown by method",
        examples=[{"KESZPENZ": 10000.00, "KARTYA": 5000.00, "SZEP_KARTYA": 2000.00}]
    )
    total_amount: float = Field(
        ...,
        description="Total payments for the day"
    )


@reports_router.get(
    "/daily-payments",
    response_model=DailyPaymentSummary,
    summary="Get daily payment summary",
    description="Returns payment summary aggregated by payment method for a specific date."
)
def get_daily_payment_summary(
    report_date: Optional[date] = Query(
        None,
        description="Report date (defaults to today)"
    ),
    db: Session = Depends(get_db)
) -> DailyPaymentSummary:
    """
    Get daily payment summary aggregated by payment method.

    Args:
        report_date: The date to generate the report for (defaults to today)
        db: Database session

    Returns:
        DailyPaymentSummary: Payment breakdown by method
    """
    # Default to today if no date provided
    if report_date is None:
        report_date = date.today()

    # Convert date to datetime range (start of day to end of day)
    start_datetime = datetime.combine(report_date, datetime.min.time())
    end_datetime = datetime.combine(report_date, datetime.max.time())

    # Query payments for the specified date, grouped by payment_method
    # Join with orders to get only closed orders
    payment_aggregates = db.query(
        Payment.payment_method,
        func.sum(Payment.amount).label('total')
    ).join(
        Order, Payment.order_id == Order.id
    ).filter(
        Payment.created_at >= start_datetime,
        Payment.created_at <= end_datetime,
        Payment.status == 'SIKERES',  # Only successful payments
        Order.status == 'LEZART'  # Only closed orders
    ).group_by(
        Payment.payment_method
    ).all()

    # Build payment summary dictionary
    payment_summary = {}
    total_amount = 0.0

    for payment_method, amount in payment_aggregates:
        # Convert Decimal to float for JSON serialization
        amount_float = float(amount) if amount else 0.0
        payment_summary[payment_method] = amount_float
        total_amount += amount_float

    return DailyPaymentSummary(
        date=report_date,
        payment_summary=payment_summary,
        total_amount=total_amount
    )
