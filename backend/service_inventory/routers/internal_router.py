"""
Internal API Router for Service-to-Service Communication
Module 5: Készletkezelés

This router handles internal API calls from other microservices.
These endpoints are NOT meant to be called by external clients.
They do NOT have RBAC protection (service-to-service trust assumed).
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from backend.service_inventory.models.database import get_db
from backend.service_inventory.services.stock_deduction_service import (
    StockDeductionService,
    get_stock_deduction_service
)

logger = logging.getLogger(__name__)

internal_router = APIRouter(
    prefix="/internal",
    tags=["Internal API"],
    responses={
        500: {"description": "Internal Server Error"}
    }
)


# Request/Response Schemas
class StockDeductionRequest(BaseModel):
    """Request schema for stock deduction"""
    order_id: int = Field(..., description="ID rendelés amelyre a készletcsökkentést végre kell hajtani", gt=0)
    orders_service_url: str | None = Field(
        None,
        description="Optional override for Orders Service URL (for testing)"
    )


class IngredientDeduction(BaseModel):
    """Details of a single ingredient deduction"""
    order_item_id: int
    product_id: int
    inventory_item_id: int
    inventory_item_name: str
    quantity_deducted: float
    remaining_stock: float
    unit: str


class SkippedItem(BaseModel):
    """Details of a skipped order item"""
    order_item_id: int | None = None
    product_id: int | None = None
    quantity: int | None = None
    reason: str


class DeductionError(BaseModel):
    """Details of a deduction error"""
    order_item_id: int | None = None
    product_id: int | None = None
    quantity: int | None = None
    error: str


class StockDeductionResponse(BaseModel):
    """Response schema for stock deduction"""
    success: bool
    order_id: int
    items_processed: int
    ingredients_deducted: List[Dict[str, Any]]
    skipped_items: List[Dict[str, Any]] | None = None
    errors: List[Dict[str, Any]]
    message: str


@internal_router.post(
    "/deduct-stock",
    status_code=status.HTTP_200_OK,
    summary="Készlet csökkentése egy lezárt rendelés alapján",
    description="""
    **INTERNAL ENDPOINT** - Called by Orders Service when an order is closed.

    This endpoint:
    1. Fetches order items from Orders Service
    2. Looks up recipes for each product
    3. Calculates ingredient consumption
    4. Deducts ingredients from inventory
    5. Returns a summary of successful/failed deductions

    **Graceful Failure**: Even if some deductions fail (e.g., insufficient stock),
    the endpoint returns 200 OK with error details in the response body.
    This allows the Orders Service to continue closing the order.
    """
)
def deduct_stock_for_order(
    request: StockDeductionRequest,
    db: Session = Depends(get_db),
    service: StockDeductionService = Depends(get_stock_deduction_service)
) -> dict:
    """
    Deduct inventory stock for a closed order

    This endpoint is called by the Orders Service after an order is marked as LEZART.
    It processes all order items, looks up recipes, and deducts ingredients from inventory.

    Args:
        request: StockDeductionRequest with order_id
        db: Database session
        service: StockDeductionService instance

    Returns:
        StockDeductionResponse with deduction summary

    Raises:
        HTTPException 400: If order_id is invalid
        HTTPException 404: If order not found in Orders Service
        HTTPException 500: If unexpected error occurs
    """
    logger.info(f"[INTERNAL API] Stock deduction request for order {request.order_id}")

    try:
        # Execute stock deduction
        result = service.deduct_stock_for_order(
            order_id=request.order_id,
            orders_service_url=request.orders_service_url
        )

        # Log result summary
        if result["success"]:
            logger.info(
                f"[INTERNAL API] Stock deduction completed for order {request.order_id}: "
                f"{len(result['ingredients_deducted'])} ingredients deducted"
            )
        else:
            logger.warning(
                f"[INTERNAL API] Stock deduction completed with errors for order {request.order_id}: "
                f"{len(result['errors'])} errors"
            )

        return StockDeductionResponse(**result)

    except ValueError as e:
        # Business logic error (e.g., order not found)
        logger.error(f"[INTERNAL API] Stock deduction failed for order {request.order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        # Unexpected error
        logger.error(
            f"[INTERNAL API] Unexpected error during stock deduction for order {request.order_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@internal_router.get(
    "/health",
    summary="Internal health check",
    description="Health check endpoint for internal monitoring",
    status_code=status.HTTP_200_OK
)
def internal_health_check():
    """
    Internal health check endpoint

    Returns:
        Simple health status
    """
    return {
        "status": "healthy",
        "service": "service_inventory",
        "endpoint": "internal_api"
    }
