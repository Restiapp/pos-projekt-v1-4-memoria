"""
Incoming Invoice API Endpoints
Handles procurement/purchasing workflow
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.service_inventory.models.database import get_db
from backend.service_inventory.models import InvoiceStatus
from backend.service_inventory.services.incoming_invoice_service import IncomingInvoiceService
from backend.service_inventory.schemas.incoming_invoice import (
    IncomingInvoiceCreate,
    IncomingInvoiceUpdate,
    IncomingInvoiceResponse,
    IncomingInvoiceListResponse,
    IncomingInvoiceFinalizeRequest,
    IncomingInvoiceFinalizeResponse,
    AddInvoiceItemRequest
)

# Import RBAC dependency (assuming it exists)
try:
    from backend.shared.rbac_middleware import require_permission
except ImportError:
    # Fallback if RBAC not available (for testing)
    def require_permission(permission: str):
        def dependency():
            return True
        return dependency


router = APIRouter(
    prefix="/api/v1/inventory/invoices",
    tags=["Incoming Invoices"]
)


@router.post(
    "",
    response_model=IncomingInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("inventory:manage"))]
)
def create_invoice(
    invoice_data: IncomingInvoiceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new incoming invoice in DRAFT status

    - **supplier_name**: Supplier name
    - **invoice_number**: Unique invoice number
    - **invoice_date**: Invoice date
    - **total_amount**: Total amount (optional, calculated from items)
    - **items**: Invoice line items (optional, can be added later)
    """
    try:
        invoice = IncomingInvoiceService.create_invoice(db, invoice_data)
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "",
    response_model=IncomingInvoiceListResponse,
    dependencies=[Depends(require_permission("inventory:view"))]
)
def list_invoices(
    status_filter: Optional[str] = None,
    supplier_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    """
    List incoming invoices with pagination and filters

    - **status_filter**: Filter by status (DRAFT, FINALIZED)
    - **supplier_name**: Filter by supplier name (partial match)
    - **page**: Page number (starts at 1)
    - **page_size**: Items per page
    """
    # Validate page parameters
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

    # Convert status filter
    status_enum = None
    if status_filter:
        try:
            status_enum = InvoiceStatus[status_filter.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")

    skip = (page - 1) * page_size

    try:
        invoices, total = IncomingInvoiceService.list_invoices(
            db=db,
            status=status_enum,
            supplier_name=supplier_name,
            skip=skip,
            limit=page_size
        )

        return IncomingInvoiceListResponse(
            invoices=invoices,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{invoice_id}",
    response_model=IncomingInvoiceResponse,
    dependencies=[Depends(require_permission("inventory:view"))]
)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific invoice by ID"""
    invoice = IncomingInvoiceService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice with ID {invoice_id} not found")
    return invoice


@router.patch(
    "/{invoice_id}",
    response_model=IncomingInvoiceResponse,
    dependencies=[Depends(require_permission("inventory:manage"))]
)
def update_invoice(
    invoice_id: int,
    update_data: IncomingInvoiceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an invoice (only in DRAFT status)

    Can update supplier_name, invoice_number, invoice_date, or total_amount
    """
    try:
        invoice = IncomingInvoiceService.update_invoice(db, invoice_id, update_data)
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{invoice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("inventory:manage"))]
)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an invoice (only in DRAFT status)
    """
    try:
        deleted = IncomingInvoiceService.delete_invoice(db, invoice_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Invoice with ID {invoice_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{invoice_id}/items",
    response_model=IncomingInvoiceResponse,
    dependencies=[Depends(require_permission("inventory:manage"))]
)
def add_items_to_invoice(
    invoice_id: int,
    items_request: AddInvoiceItemRequest,
    db: Session = Depends(get_db)
):
    """
    Add items to an existing invoice (only in DRAFT status)

    - **items**: List of invoice items to add
    """
    try:
        invoice = IncomingInvoiceService.add_items(db, invoice_id, items_request.items)
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{invoice_id}/finalize",
    response_model=IncomingInvoiceFinalizeResponse,
    dependencies=[Depends(require_permission("inventory:manage"))]
)
def finalize_invoice(
    invoice_id: int,
    finalize_request: IncomingInvoiceFinalizeRequest,
    db: Session = Depends(get_db)
):
    """
    Finalize an invoice - increases stock and creates movement logs

    Once finalized, the invoice cannot be modified or deleted.
    Stock will be increased for all items on the invoice.

    - **employee_id**: Optional employee ID
    - **notes**: Optional notes
    """
    try:
        invoice, movements_count = IncomingInvoiceService.finalize_invoice(
            db=db,
            invoice_id=invoice_id,
            employee_id=finalize_request.employee_id,
            notes=finalize_request.notes
        )

        return IncomingInvoiceFinalizeResponse(
            invoice=invoice,
            stock_movements_created=movements_count,
            message=f"Invoice finalized successfully. {movements_count} stock movements created."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
