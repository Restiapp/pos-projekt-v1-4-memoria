"""
Gift Card Router - FastAPI Endpoints for Gift Card Management
Module 5: Customer Relationship Management (CRM)

Ez a router felelős az ajándékkártyák REST API végpontjaiért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- Ajándékkártya beváltás (redeem)
- Egyenleg módosítás
- Validáció
"""

from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_crm.models.database import get_db
from backend.service_crm.services.gift_card_service import GiftCardService
from backend.service_crm.schemas.gift_card import (
    GiftCardCreate,
    GiftCardUpdate,
    GiftCardResponse,
    GiftCardListResponse,
    GiftCardRedemption,
    GiftCardRedemptionResponse,
    GiftCardBalanceUpdate
)

# Router létrehozása
gift_cards_router = APIRouter(
    prefix="/gift-cards",
    tags=["Gift Cards"],
    responses={404: {"description": "Gift card not found"}}
)


@gift_cards_router.post(
    "/",
    response_model=GiftCardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new gift card",
    description="Creates a new gift card with a unique code and initial balance."
)
def create_gift_card(
    gift_card_data: GiftCardCreate,
    db: Session = Depends(get_db)
) -> GiftCardResponse:
    """
    Create a new gift card.

    Args:
        gift_card_data: Gift card creation data (code, balance, validity, etc.)
        db: Database session (injected)

    Returns:
        GiftCardResponse: The newly created gift card

    Raises:
        HTTPException 400: If card code already exists or data is invalid

    Example request body:
        {
            "card_code": "GIFT-2024-ABC123",
            "pin_code": "1234",
            "initial_balance": 10000.00,
            "valid_until": "2025-12-31T23:59:59",
            "is_active": true,
            "customer_id": 42
        }
    """
    gift_card = GiftCardService.create_gift_card(db, gift_card_data)
    return GiftCardResponse.model_validate(gift_card)


@gift_cards_router.get(
    "/",
    response_model=GiftCardListResponse,
    summary="List all gift cards",
    description="Retrieve a paginated list of gift cards with optional filtering."
)
def get_gift_cards(
    skip: int = Query(0, ge=0, description="Number of gift cards to skip (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of gift cards to return"),
    search: Optional[str] = Query(None, description="Search by card code"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    is_valid: Optional[bool] = Query(None, description="Filter by validity (active + not expired + has balance)"),
    db: Session = Depends(get_db)
) -> GiftCardListResponse:
    """
    Get a list of gift cards with optional filtering.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        search: Optional search term for card code
        is_active: Optional filter by active/inactive status
        customer_id: Optional filter by customer ID
        is_valid: Optional filter by validity (active, not expired, has balance)
        db: Database session (injected)

    Returns:
        GiftCardListResponse: Paginated list of gift cards with metadata

    Example:
        GET /gift-cards?skip=0&limit=20&is_active=true&customer_id=42
    """
    gift_cards = GiftCardService.get_gift_cards(
        db,
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active,
        customer_id=customer_id,
        is_valid=is_valid
    )

    total = GiftCardService.count_gift_cards(
        db,
        search=search,
        is_active=is_active,
        customer_id=customer_id,
        is_valid=is_valid
    )

    page = (skip // limit) + 1 if limit > 0 else 1

    return GiftCardListResponse(
        items=[GiftCardResponse.model_validate(gc) for gc in gift_cards],
        total=total,
        page=page,
        page_size=limit
    )


@gift_cards_router.get(
    "/{gift_card_id}",
    response_model=GiftCardResponse,
    summary="Get gift card by ID",
    description="Retrieve a single gift card by its unique identifier."
)
def get_gift_card(
    gift_card_id: int,
    db: Session = Depends(get_db)
) -> GiftCardResponse:
    """
    Get a specific gift card by ID.

    Args:
        gift_card_id: Gift card's unique identifier
        db: Database session (injected)

    Returns:
        GiftCardResponse: Gift card details

    Raises:
        HTTPException 404: If gift card not found

    Example:
        GET /gift-cards/42
    """
    gift_card = GiftCardService.get_gift_card(db, gift_card_id)
    return GiftCardResponse.model_validate(gift_card)


@gift_cards_router.get(
    "/code/{card_code}",
    response_model=GiftCardResponse,
    summary="Get gift card by code",
    description="Retrieve a gift card by its unique card code."
)
def get_gift_card_by_code(
    card_code: str,
    db: Session = Depends(get_db)
) -> GiftCardResponse:
    """
    Get a gift card by card code.

    Args:
        card_code: Gift card's unique code
        db: Database session (injected)

    Returns:
        GiftCardResponse: Gift card details

    Raises:
        HTTPException 404: If gift card not found

    Example:
        GET /gift-cards/code/GIFT-2024-ABC123
    """
    gift_card = GiftCardService.get_gift_card_by_code(db, card_code)
    if not gift_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ajándékkártya nem található ezzel a kóddal: {card_code}"
        )
    return GiftCardResponse.model_validate(gift_card)


@gift_cards_router.put(
    "/{gift_card_id}",
    response_model=GiftCardResponse,
    summary="Update gift card",
    description="Update an existing gift card's information."
)
def update_gift_card(
    gift_card_id: int,
    gift_card_data: GiftCardUpdate,
    db: Session = Depends(get_db)
) -> GiftCardResponse:
    """
    Update a gift card's information.

    Args:
        gift_card_id: Gift card's unique identifier
        gift_card_data: Updated gift card data
        db: Database session (injected)

    Returns:
        GiftCardResponse: Updated gift card details

    Raises:
        HTTPException 404: If gift card not found
        HTTPException 400: If data is invalid

    Example request body:
        {
            "is_active": false,
            "valid_until": "2026-12-31T23:59:59"
        }
    """
    gift_card = GiftCardService.update_gift_card(db, gift_card_id, gift_card_data)
    return GiftCardResponse.model_validate(gift_card)


@gift_cards_router.delete(
    "/{gift_card_id}",
    summary="Delete gift card",
    description="Soft delete a gift card (sets is_active to False)."
)
def delete_gift_card(
    gift_card_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete (deactivate) a gift card.

    Args:
        gift_card_id: Gift card's unique identifier
        db: Database session (injected)

    Returns:
        dict: Confirmation message

    Raises:
        HTTPException 404: If gift card not found

    Example:
        DELETE /gift-cards/42
    """
    return GiftCardService.delete_gift_card(db, gift_card_id)


@gift_cards_router.post(
    "/redeem",
    response_model=GiftCardRedemptionResponse,
    summary="Redeem gift card",
    description="Redeem (use) a gift card by deducting amount from balance."
)
def redeem_gift_card(
    redemption_data: GiftCardRedemption,
    db: Session = Depends(get_db)
) -> GiftCardRedemptionResponse:
    """
    Redeem a gift card.

    Args:
        redemption_data: Redemption data (card code, PIN, amount)
        db: Database session (injected)

    Returns:
        GiftCardRedemptionResponse: Redemption result with updated balance

    Raises:
        HTTPException 404: If gift card not found
        HTTPException 400: If card is invalid, PIN is wrong, or insufficient balance

    Example request body:
        {
            "card_code": "GIFT-2024-ABC123",
            "pin_code": "1234",
            "amount": 5000.00,
            "order_id": 123
        }
    """
    result = GiftCardService.redeem_gift_card(db, redemption_data)

    # Ha sikeres, lekérjük a frissített kártyát
    if result.get("success"):
        gift_card = GiftCardService.get_gift_card(db, result["gift_card_id"])
        return GiftCardRedemptionResponse(
            success=True,
            message=result["message"],
            redeemed_amount=result["redeemed_amount"],
            remaining_balance=result["remaining_balance"],
            gift_card=GiftCardResponse.model_validate(gift_card)
        )

    return GiftCardRedemptionResponse(
        success=False,
        message=result.get("message", "Beváltás sikertelen")
    )


@gift_cards_router.post(
    "/{gift_card_id}/balance",
    response_model=GiftCardResponse,
    summary="Update gift card balance",
    description="Add or subtract balance from a gift card (refunds, bonuses, corrections)."
)
def update_balance(
    gift_card_id: int,
    balance_data: GiftCardBalanceUpdate,
    db: Session = Depends(get_db)
) -> GiftCardResponse:
    """
    Update gift card balance.

    Args:
        gift_card_id: Gift card's unique identifier
        balance_data: Balance update data (amount and reason)
        db: Database session (injected)

    Returns:
        GiftCardResponse: Updated gift card with new balance

    Raises:
        HTTPException 404: If gift card not found
        HTTPException 400: If balance would become negative

    Example request body:
        {
            "amount": 1000.00,
            "reason": "Refund from cancelled order"
        }
    """
    gift_card = GiftCardService.update_balance(db, gift_card_id, balance_data)
    return GiftCardResponse.model_validate(gift_card)


@gift_cards_router.post(
    "/validate",
    summary="Validate gift card",
    description="Validate a gift card's status, balance, and PIN (if provided)."
)
def validate_gift_card(
    card_code: str = Query(..., description="Gift card code to validate"),
    pin_code: Optional[str] = Query(None, description="PIN code (if required)"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Validate a gift card.

    Args:
        card_code: Gift card code
        pin_code: Optional PIN code
        db: Database session (injected)

    Returns:
        dict: Validation result with card details and validity status

    Raises:
        HTTPException 404: If gift card not found

    Example:
        POST /gift-cards/validate?card_code=GIFT-2024-ABC123&pin_code=1234
    """
    return GiftCardService.validate_gift_card(db, card_code, pin_code)
