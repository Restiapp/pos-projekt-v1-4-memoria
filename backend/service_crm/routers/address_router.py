"""
Address Router - FastAPI Endpoints for Address Management
Module 5: Customer Relationship Management (CRM)

Ez a router felelős a címek REST API végpontjaiért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- Ügyfél címeinek kezelése
- Alapértelmezett címek beállítása
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_crm.models.database import get_db
from backend.service_crm.services.address_service import AddressService
from backend.service_crm.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse,
    AddressListResponse,
    AddressTypeEnum
)

# Router létrehozása
addresses_router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
    responses={404: {"description": "Address not found"}}
)


@addresses_router.post(
    "/",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new address",
    description="Creates a new address for a customer (shipping, billing, or both)."
)
def create_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db)
) -> AddressResponse:
    """
    Create a new address.

    Args:
        address_data: Address creation data (customer ID, type, postal code, city, etc.)
        db: Database session (injected)

    Returns:
        AddressResponse: The newly created address

    Raises:
        HTTPException 400: If data is invalid

    Example request body:
        {
            "customer_id": 42,
            "address_type": "SHIPPING",
            "is_default": true,
            "postal_code": "1011",
            "city": "Budapest",
            "street_address": "Fő utca",
            "street_number": "1",
            "floor": "2",
            "door": "15"
        }
    """
    address = AddressService.create_address(db, address_data)
    return AddressResponse.model_validate(address)


@addresses_router.get(
    "/",
    response_model=AddressListResponse,
    summary="List all addresses",
    description="Retrieve a paginated list of addresses with optional filtering."
)
def get_addresses(
    skip: int = Query(0, ge=0, description="Number of addresses to skip (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of addresses to return"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    address_type: Optional[AddressTypeEnum] = Query(None, description="Filter by address type"),
    is_default: Optional[bool] = Query(None, description="Filter by default status"),
    db: Session = Depends(get_db)
) -> AddressListResponse:
    """
    Get a list of addresses with optional filtering.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        customer_id: Optional filter by customer ID
        address_type: Optional filter by address type (SHIPPING, BILLING, BOTH)
        is_default: Optional filter by default status
        db: Database session (injected)

    Returns:
        AddressListResponse: Paginated list of addresses with metadata

    Example:
        GET /addresses?skip=0&limit=20&customer_id=42&address_type=SHIPPING
    """
    addresses = AddressService.get_addresses(
        db,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        address_type=address_type,
        is_default=is_default
    )

    total = AddressService.count_addresses(
        db,
        customer_id=customer_id,
        address_type=address_type,
        is_default=is_default
    )

    page = (skip // limit) + 1 if limit > 0 else 1

    return AddressListResponse(
        items=[AddressResponse.model_validate(addr) for addr in addresses],
        total=total,
        page=page,
        page_size=limit
    )


@addresses_router.get(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Get address by ID",
    description="Retrieve a single address by its unique identifier."
)
def get_address(
    address_id: int,
    db: Session = Depends(get_db)
) -> AddressResponse:
    """
    Get a specific address by ID.

    Args:
        address_id: Address's unique identifier
        db: Database session (injected)

    Returns:
        AddressResponse: Address details

    Raises:
        HTTPException 404: If address not found

    Example:
        GET /addresses/42
    """
    address = AddressService.get_address(db, address_id)
    return AddressResponse.model_validate(address)


@addresses_router.get(
    "/customer/{customer_id}",
    response_model=List[AddressResponse],
    summary="Get customer addresses",
    description="Retrieve all addresses for a specific customer."
)
def get_customer_addresses(
    customer_id: int,
    address_type: Optional[AddressTypeEnum] = Query(None, description="Filter by address type"),
    db: Session = Depends(get_db)
) -> List[AddressResponse]:
    """
    Get all addresses for a customer.

    Args:
        customer_id: Customer's unique identifier
        address_type: Optional filter by address type
        db: Database session (injected)

    Returns:
        List[AddressResponse]: List of customer's addresses

    Example:
        GET /addresses/customer/42?address_type=SHIPPING
    """
    addresses = AddressService.get_customer_addresses(db, customer_id, address_type)
    return [AddressResponse.model_validate(addr) for addr in addresses]


@addresses_router.get(
    "/customer/{customer_id}/default",
    response_model=AddressResponse,
    summary="Get default address",
    description="Retrieve the default address for a customer by type."
)
def get_default_address(
    customer_id: int,
    address_type: AddressTypeEnum = Query(..., description="Address type (SHIPPING, BILLING, BOTH)"),
    db: Session = Depends(get_db)
) -> AddressResponse:
    """
    Get customer's default address by type.

    Args:
        customer_id: Customer's unique identifier
        address_type: Address type to retrieve
        db: Database session (injected)

    Returns:
        AddressResponse: Default address details

    Raises:
        HTTPException 404: If default address not found

    Example:
        GET /addresses/customer/42/default?address_type=SHIPPING
    """
    address = AddressService.get_default_address(db, customer_id, address_type)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nincs alapértelmezett {address_type.value} cím ehhez az ügyfélhez: {customer_id}"
        )
    return AddressResponse.model_validate(address)


@addresses_router.put(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Update address",
    description="Update an existing address's information."
)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db)
) -> AddressResponse:
    """
    Update an address's information.

    Args:
        address_id: Address's unique identifier
        address_data: Updated address data
        db: Database session (injected)

    Returns:
        AddressResponse: Updated address details

    Raises:
        HTTPException 404: If address not found
        HTTPException 400: If data is invalid

    Example request body:
        {
            "floor": "3",
            "door": "20",
            "notes": "Ring the doorbell twice"
        }
    """
    address = AddressService.update_address(db, address_id, address_data)
    return AddressResponse.model_validate(address)


@addresses_router.delete(
    "/{address_id}",
    summary="Delete address",
    description="Delete an address (hard delete)."
)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete an address.

    Args:
        address_id: Address's unique identifier
        db: Database session (injected)

    Returns:
        dict: Confirmation message

    Raises:
        HTTPException 404: If address not found

    Example:
        DELETE /addresses/42
    """
    return AddressService.delete_address(db, address_id)


@addresses_router.post(
    "/{address_id}/set-default",
    response_model=AddressResponse,
    summary="Set default address",
    description="Set an address as the default for its type."
)
def set_default_address(
    address_id: int,
    db: Session = Depends(get_db)
) -> AddressResponse:
    """
    Set address as default.

    Args:
        address_id: Address's unique identifier
        db: Database session (injected)

    Returns:
        AddressResponse: Updated address with default status

    Raises:
        HTTPException 404: If address not found

    Example:
        POST /addresses/42/set-default
    """
    address = AddressService.set_default_address(db, address_id)
    return AddressResponse.model_validate(address)
