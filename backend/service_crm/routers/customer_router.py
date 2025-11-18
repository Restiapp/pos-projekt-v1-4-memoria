"""
Customer Router - FastAPI Endpoints for Customer Management
Module 5: Customer Relationship Management (CRM)

Ez a router felelős az ügyfelek REST API végpontjaiért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- Törzsvásárlói pontok kezelése
- Vásárlási statisztikák
"""

from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_crm.models.database import get_db
from backend.service_crm.services.customer_service import CustomerService
from backend.service_crm.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    LoyaltyPointsUpdate
)

# Router létrehozása
customers_router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    responses={404: {"description": "Customer not found"}}
)


@customers_router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
    description="Creates a new customer in the CRM system with personal information and preferences."
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    """
    Create a new customer.

    Args:
        customer_data: Customer creation data (name, email, phone, etc.)
        db: Database session (injected)

    Returns:
        CustomerResponse: The newly created customer

    Raises:
        HTTPException 400: If email already exists or data is invalid

    Example request body:
        {
            "first_name": "János",
            "last_name": "Nagy",
            "email": "janos.nagy@example.com",
            "phone": "+36301234567",
            "marketing_consent": true,
            "sms_consent": false
        }
    """
    customer = CustomerService.create_customer(db, customer_data)
    return CustomerResponse.model_validate(customer)


@customers_router.get(
    "/",
    response_model=CustomerListResponse,
    summary="List all customers",
    description="Retrieve a paginated list of customers with optional search filtering."
)
def get_customers(
    skip: int = Query(0, ge=0, description="Number of customers to skip (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of customers to return"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
) -> CustomerListResponse:
    """
    Get a list of customers with optional filtering.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        search: Optional search term for name or email
        is_active: Optional filter by active/inactive status
        db: Database session (injected)

    Returns:
        CustomerListResponse: Paginated list of customers with metadata

    Example:
        GET /customers?skip=0&limit=20&search=nagy&is_active=true
    """
    customers = CustomerService.get_customers(
        db,
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active
    )

    total = CustomerService.count_customers(
        db,
        search=search,
        is_active=is_active
    )

    page = (skip // limit) + 1 if limit > 0 else 1

    return CustomerListResponse(
        items=[CustomerResponse.model_validate(customer) for customer in customers],
        total=total,
        page=page,
        page_size=limit
    )


@customers_router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get customer by ID",
    description="Retrieve a single customer by their unique identifier."
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    """
    Get a specific customer by ID.

    Args:
        customer_id: Customer's unique identifier
        db: Database session (injected)

    Returns:
        CustomerResponse: Customer details

    Raises:
        HTTPException 404: If customer not found

    Example:
        GET /customers/42
    """
    customer = CustomerService.get_customer(db, customer_id)
    return CustomerResponse.model_validate(customer)


@customers_router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer",
    description="Update an existing customer's information."
)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    """
    Update a customer's information.

    Args:
        customer_id: Customer's unique identifier
        customer_data: Updated customer data
        db: Database session (injected)

    Returns:
        CustomerResponse: Updated customer details

    Raises:
        HTTPException 404: If customer not found
        HTTPException 400: If email already in use or data is invalid

    Example request body:
        {
            "phone": "+36301111111",
            "marketing_consent": false
        }
    """
    customer = CustomerService.update_customer(db, customer_id, customer_data)
    return CustomerResponse.model_validate(customer)


@customers_router.delete(
    "/{customer_id}",
    summary="Delete customer",
    description="Soft delete a customer (sets is_active to False)."
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete (deactivate) a customer.

    Args:
        customer_id: Customer's unique identifier
        db: Database session (injected)

    Returns:
        dict: Confirmation message

    Raises:
        HTTPException 404: If customer not found

    Example:
        DELETE /customers/42
    """
    return CustomerService.delete_customer(db, customer_id)


@customers_router.post(
    "/{customer_id}/loyalty-points",
    response_model=CustomerResponse,
    summary="Update loyalty points",
    description="Add or subtract loyalty points from a customer's account."
)
def update_loyalty_points(
    customer_id: int,
    points_data: LoyaltyPointsUpdate,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    """
    Update customer's loyalty points.

    Args:
        customer_id: Customer's unique identifier
        points_data: Points to add (positive) or subtract (negative)
        db: Database session (injected)

    Returns:
        CustomerResponse: Updated customer with new points balance

    Raises:
        HTTPException 404: If customer not found
        HTTPException 400: If insufficient points for subtraction

    Example request body:
        {
            "points": 10.00,
            "reason": "Birthday bonus"
        }
    """
    customer = CustomerService.update_loyalty_points(db, customer_id, points_data)
    return CustomerResponse.model_validate(customer)


@customers_router.get(
    "/email/{email}",
    response_model=CustomerResponse,
    summary="Get customer by email",
    description="Retrieve a customer by their email address."
)
def get_customer_by_email(
    email: str,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    """
    Get a customer by email address.

    Args:
        email: Customer's email address
        db: Database session (injected)

    Returns:
        CustomerResponse: Customer details

    Raises:
        HTTPException 404: If customer not found

    Example:
        GET /customers/email/janos.nagy@example.com
    """
    customer = CustomerService.get_customer_by_email(db, email)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ügyfél nem található ezzel az email címmel: {email}"
        )
    return CustomerResponse.model_validate(customer)


@customers_router.get(
    "/by-uid/{customer_uid}",
    response_model=CustomerResponse,
    summary="Get customer by UID",
    description="Retrieve a customer by their unique customer_uid (Vendégszám)."
)
def get_customer_by_uid(
    customer_uid: str,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    """
    Get a customer by customer_uid (Vendégszám).

    Args:
        customer_uid: Customer's unique identifier (e.g., CUST-123456)
        db: Database session (injected)

    Returns:
        CustomerResponse: Customer details

    Raises:
        HTTPException 404: If customer not found

    Example:
        GET /customers/by-uid/CUST-123456
    """
    customer = CustomerService.get_customer_by_uid(db, customer_uid)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ügyfél nem található ezzel a vendégszámmal: {customer_uid}"
        )
    return CustomerResponse.model_validate(customer)
