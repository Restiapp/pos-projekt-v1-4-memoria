"""
NAV OSA Integration Router
Module 5: Készletkezelés

This router handles NAV (Nemzeti Adó- és Vámhivatal) Online Számlázó API integration.
Endpoints for sending invoices to NAV, querying status, and managing tax compliance.

Current implementation uses MOCK NAV service.
TODO (Fázis 4): Replace MOCK with real NAV API integration.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.service_inventory.models.database import get_db
from backend.service_inventory.services.nav_osa_service import (
    NAVOSAService,
    get_nav_osa_service
)
from backend.service_inventory.schemas.nav_osa_invoice import (
    NAVSendInvoiceRequest,
    NAVSendInvoiceResponse
)

logger = logging.getLogger(__name__)

osa_router = APIRouter(
    prefix="/osa",
    tags=["NAV OSA Integration"],
    responses={
        500: {"description": "Internal Server Error"}
    }
)


@osa_router.post(
    "/send-invoice",
    response_model=NAVSendInvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Számla küldése a NAV Online Számlázó rendszerbe",
    description="""
    **NAV OSA Integration Endpoint** - Send invoice to NAV Online Számlázó API.

    **CURRENT STATUS: MOCK IMPLEMENTATION**

    This endpoint currently uses a MOCK NAV service that simulates API responses
    without actually connecting to the NAV servers.

    **TODO (Fázis 4): Real NAV API Integration**
    - Implement proper XML generation for invoiceData
    - Add cryptographic signing with tax technical user credentials
    - Implement proper error handling for NAV API responses
    - Add retry logic for network failures
    - Implement webhook handling for async NAV responses

    **Authentication Required**: This endpoint requires `inventory:manage` permission.

    **Request Body**:
    - `invoice_id`: ID of the invoice in local database
    - `test_mode`: Use NAV test environment (default: true)

    **Response**:
    - `success`: Whether the operation succeeded
    - `invoice_id`: Local invoice ID
    - `nav_transaction_id`: NAV transaction ID (for tracking)
    - `status`: Processing status (PENDING, ACCEPTED, REJECTED)
    - `message`: Human-readable message
    - `nav_response`: Full NAV API response (for debugging)
    """
)
def send_invoice_to_nav(
    request: NAVSendInvoiceRequest,
    db: Session = Depends(get_db),
    service: NAVOSAService = Depends(get_nav_osa_service)
) -> NAVSendInvoiceResponse:
    """
    Send invoice to NAV Online Számlázó API

    Args:
        request: NAVSendInvoiceRequest with invoice_id and test_mode
        db: Database session
        service: NAVOSAService instance

    Returns:
        NAVSendInvoiceResponse with NAV transaction details

    Raises:
        HTTPException 404: If invoice not found
        HTTPException 400: If invoice is invalid or already sent
        HTTPException 500: If NAV API call fails
    """
    logger.info(
        f"[NAV OSA] Send invoice request: invoice_id={request.invoice_id}, "
        f"test_mode={request.test_mode}"
    )

    try:
        # TODO (Fázis 4): Fetch invoice from database
        # For now, using mock data
        invoice_data = {
            "invoice_id": request.invoice_id,
            "invoice_number": f"MOCK-{request.invoice_id}",
            "test_mode": request.test_mode
        }

        # Send to NAV (MOCK)
        result = service.send_invoice_to_nav(
            invoice_data=invoice_data,
            test_mode=request.test_mode
        )

        # TODO (Fázis 4): Update invoice status in database
        # - Set status to "SENT"
        # - Store nav_transaction_id
        # - Store nav_response_data

        logger.info(
            f"[NAV OSA] Invoice {request.invoice_id} sent successfully: "
            f"transaction_id={result.get('transaction_id')}"
        )

        return NAVSendInvoiceResponse(
            success=result["success"],
            invoice_id=request.invoice_id,
            nav_transaction_id=result.get("transaction_id"),
            status=result.get("status", "PENDING"),
            message=result.get("message", "Invoice sent to NAV"),
            nav_response=result.get("nav_response")
        )

    except ValueError as e:
        # Business logic error (e.g., invoice not found, invalid state)
        logger.error(f"[NAV OSA] Failed to send invoice {request.invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Unexpected error (e.g., NAV API failure)
        logger.error(f"[NAV OSA] Unexpected error sending invoice {request.invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send invoice to NAV: {str(e)}"
        )


@osa_router.get(
    "/invoice-status/{transaction_id}",
    summary="NAV számla státusz lekérdezése",
    description="""
    **MOCK IMPLEMENTATION** - Query invoice processing status from NAV.

    TODO (Fázis 4): Implement real NAV status query endpoint.
    """,
    status_code=status.HTTP_200_OK
)
def query_invoice_status(
    transaction_id: str,
    db: Session = Depends(get_db),
    service: NAVOSAService = Depends(get_nav_osa_service)
):
    """
    Query invoice processing status from NAV

    Args:
        transaction_id: NAV transaction ID from previous send_invoice call
        db: Database session
        service: NAVOSAService instance

    Returns:
        Invoice processing status

    Raises:
        HTTPException 404: If transaction not found
        HTTPException 500: If NAV API call fails
    """
    logger.info(f"[NAV OSA] Query status for transaction: {transaction_id}")

    try:
        result = service.query_invoice_status(transaction_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("message", "Transaction not found")
            )

        return result

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[NAV OSA] Error querying status for {transaction_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query invoice status: {str(e)}"
        )


@osa_router.post(
    "/validate-tax-number/{tax_number}",
    summary="Adószám ellenőrzése NAV-on keresztül",
    description="""
    **MOCK IMPLEMENTATION** - Validate Hungarian tax number via NAV API.

    TODO (Fázis 4): Implement real NAV tax number validation.
    """,
    status_code=status.HTTP_200_OK
)
def validate_tax_number(
    tax_number: str,
    db: Session = Depends(get_db),
    service: NAVOSAService = Depends(get_nav_osa_service)
):
    """
    Validate Hungarian tax number via NAV API

    Args:
        tax_number: Hungarian tax number (format: XXXXXXXX-Y-ZZ)
        db: Database session
        service: NAVOSAService instance

    Returns:
        Validation result with taxpayer data

    Raises:
        HTTPException 400: If tax number format is invalid
        HTTPException 500: If NAV API call fails
    """
    logger.info(f"[NAV OSA] Validate tax number: {tax_number}")

    try:
        result = service.validate_tax_number(tax_number)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Invalid tax number")
            )

        return result

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[NAV OSA] Error validating tax number {tax_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate tax number: {str(e)}"
        )
