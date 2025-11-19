"""
Incoming Invoices Router - FastAPI Endpoints
Module 5: Készletkezelés - NAV OSA Integration

Ez a modul tartalmazza az IncomingInvoice entitáshoz tartozó API végpontokat.
A bejövő számlák a NAV Online Számla rendszeréből kerülnek lekérdezésre.
"""

import logging
from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.service_inventory.models.database import get_db
from backend.service_inventory.models.incoming_invoice import IncomingInvoice
from backend.service_inventory.services.nav_osa_service import (
    NAVOSAService,
    get_nav_osa_service
)
from backend.service_inventory.schemas.incoming_invoice import (
    IncomingInvoiceResponse,
    IncomingInvoiceListResponse,
    FetchIncomingInvoicesRequest,
    FetchIncomingInvoicesResponse
)

logger = logging.getLogger(__name__)

# Router instance
router = APIRouter(
    prefix="/inventory/incoming-invoices",
    tags=["Incoming Invoices (NAV OSA)"],
    responses={
        404: {"description": "Invoice not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/fetch-from-osa",
    response_model=FetchIncomingInvoicesResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch incoming invoices from NAV OSA",
    description="""
    **NAV OSA Integration Endpoint** - Fetch incoming supplier invoices from NAV.

    **CURRENT STATUS: MOCK IMPLEMENTATION**

    This endpoint fetches incoming invoices from the NAV Online Számlázó API
    and saves them to the local database with status 'NEW'.

    **TODO (Fázis 4): Real NAV API Integration**
    - Implement proper authentication with NAV API
    - Add date range filtering
    - Implement pagination for large result sets
    - Add error handling for NAV API failures
    - Implement incremental sync (only fetch new invoices)

    **Query Parameters**:
    - `from_date`: Start date for invoice query (optional, format: YYYY-MM-DD)
    - `to_date`: End date for invoice query (optional, format: YYYY-MM-DD)
    - `test_mode`: Use NAV test environment (default: true)

    **Response**:
    - `success`: Whether the operation succeeded
    - `fetched_count`: Number of invoices fetched from NAV
    - `saved_count`: Number of new invoices saved to database
    - `message`: Human-readable message
    - `invoices`: List of fetched and saved invoices
    """
)
def fetch_incoming_invoices_from_osa(
    from_date: Optional[date] = Query(None, description="Start date for invoice query"),
    to_date: Optional[date] = Query(None, description="End date for invoice query"),
    test_mode: bool = Query(True, description="Use NAV test environment"),
    db: Session = Depends(get_db),
    nav_service: NAVOSAService = Depends(get_nav_osa_service)
) -> FetchIncomingInvoicesResponse:
    """
    Fetch incoming invoices from NAV OSA and save to database.

    This endpoint:
    1. Calls the NAV OSA API to fetch incoming invoices
    2. Saves new invoices to the incoming_invoices table with status 'NEW'
    3. Skips invoices that already exist (based on invoice_number)
    4. Returns the list of fetched and saved invoices

    Args:
        from_date: Start date for invoice query
        to_date: End date for invoice query
        test_mode: Use NAV test environment
        db: Database session
        nav_service: NAV OSA service instance

    Returns:
        FetchIncomingInvoicesResponse with operation results

    Raises:
        HTTPException 500: If NAV API call fails or database error occurs
    """
    logger.info("[Incoming Invoices] Fetching invoices from NAV OSA")
    logger.info(f"[Incoming Invoices] Parameters: from_date={from_date}, to_date={to_date}, test_mode={test_mode}")

    try:
        # Convert dates to ISO format strings if provided
        from_date_str = from_date.isoformat() if from_date else None
        to_date_str = to_date.isoformat() if to_date else None

        # Fetch invoices from NAV OSA (MOCK)
        nav_result = nav_service.fetch_incoming_invoices(
            from_date=from_date_str,
            to_date=to_date_str,
            test_mode=test_mode
        )

        if not nav_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch invoices from NAV: {nav_result.get('message', 'Unknown error')}"
            )

        fetched_invoices = nav_result.get("invoices", [])
        fetched_count = len(fetched_invoices)
        saved_invoices = []
        saved_count = 0

        logger.info(f"[Incoming Invoices] Fetched {fetched_count} invoices from NAV")

        # Save each invoice to database
        for invoice_data in fetched_invoices:
            try:
                # Parse invoice_date string to date object
                invoice_date_obj = None
                if invoice_data.get("invoice_date"):
                    invoice_date_obj = datetime.fromisoformat(invoice_data["invoice_date"]).date()

                # Create IncomingInvoice model instance
                new_invoice = IncomingInvoice(
                    invoice_number=invoice_data["invoice_number"],
                    supplier_tax_number=invoice_data.get("supplier_tax_number"),
                    supplier_name=invoice_data.get("supplier_name"),
                    invoice_date=invoice_date_obj,
                    total_amount=invoice_data.get("total_amount"),
                    currency=invoice_data.get("currency", "HUF"),
                    nav_data=invoice_data,  # Store full NAV response
                    status="NEW"  # Default status
                )

                # Add to database
                db.add(new_invoice)
                db.commit()
                db.refresh(new_invoice)

                saved_invoices.append(new_invoice)
                saved_count += 1

                logger.info(f"[Incoming Invoices] Saved invoice: {invoice_data['invoice_number']}")

            except IntegrityError as e:
                # Invoice already exists (duplicate invoice_number)
                db.rollback()
                logger.warning(
                    f"[Incoming Invoices] Invoice {invoice_data['invoice_number']} already exists, skipping"
                )
                continue

            except Exception as e:
                # Other database errors
                db.rollback()
                logger.error(
                    f"[Incoming Invoices] Error saving invoice {invoice_data.get('invoice_number', 'UNKNOWN')}: {str(e)}"
                )
                continue

        logger.info(f"[Incoming Invoices] Saved {saved_count} new invoices to database")

        # Convert saved invoices to response schema
        invoice_responses = [
            IncomingInvoiceResponse.model_validate(inv) for inv in saved_invoices
        ]

        return FetchIncomingInvoicesResponse(
            success=True,
            fetched_count=fetched_count,
            saved_count=saved_count,
            message=f"Successfully fetched {fetched_count} invoices from NAV, saved {saved_count} new invoices",
            invoices=invoice_responses
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[Incoming Invoices] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch incoming invoices: {str(e)}"
        )


@router.get(
    "",
    response_model=IncomingInvoiceListResponse,
    summary="List incoming invoices",
    description="Retrieve a paginated list of incoming invoices with optional filtering"
)
def list_incoming_invoices(
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status (NEW, REVIEWED, SETTLED)"),
    db: Session = Depends(get_db)
) -> IncomingInvoiceListResponse:
    """
    List incoming invoices with pagination and filtering.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        status_filter: Filter by invoice status
        db: Database session

    Returns:
        IncomingInvoiceListResponse with paginated results
    """
    logger.info(f"[Incoming Invoices] Listing invoices: skip={skip}, limit={limit}, status={status_filter}")

    try:
        # Build query
        query = db.query(IncomingInvoice)

        # Apply status filter if provided
        if status_filter:
            query = query.filter(IncomingInvoice.status == status_filter)

        # Get total count
        total = query.count()

        # Apply pagination
        invoices = query.order_by(IncomingInvoice.created_at.desc()).offset(skip).limit(limit).all()

        # Convert to response schema
        invoice_responses = [
            IncomingInvoiceResponse.model_validate(inv) for inv in invoices
        ]

        return IncomingInvoiceListResponse(
            items=invoice_responses,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit
        )

    except Exception as e:
        logger.error(f"[Incoming Invoices] Error listing invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list incoming invoices: {str(e)}"
        )


@router.get(
    "/{invoice_id}",
    response_model=IncomingInvoiceResponse,
    summary="Get incoming invoice by ID",
    description="Retrieve a single incoming invoice by its unique identifier"
)
def get_incoming_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
) -> IncomingInvoiceResponse:
    """
    Get a single incoming invoice by ID.

    Args:
        invoice_id: Invoice ID
        db: Database session

    Returns:
        IncomingInvoiceResponse

    Raises:
        HTTPException 404: If invoice not found
    """
    logger.info(f"[Incoming Invoices] Getting invoice: {invoice_id}")

    try:
        invoice = db.query(IncomingInvoice).filter(IncomingInvoice.id == invoice_id).first()

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incoming invoice with id {invoice_id} not found"
            )

        return IncomingInvoiceResponse.model_validate(invoice)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[Incoming Invoices] Error getting invoice {invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get incoming invoice: {str(e)}"
        )
