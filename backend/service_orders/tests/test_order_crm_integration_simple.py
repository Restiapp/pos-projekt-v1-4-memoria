"""
Integration Tests for Order + CRM Integration (Simplified)
===========================================================

Tests the OrderService logic for customer_uid validation.
This version doesn't require the full FastAPI application.

Test Coverage:
1. Create order with valid customer_uid (successful)
2. Create order without customer_uid (successful)
3. Create order with invalid customer_uid (fails with 404)

Usage:
    pytest backend/service_orders/tests/test_order_crm_integration_simple.py -v
"""

import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic import ValidationError

# Set environment variables
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["CRM_SERVICE_URL"] = "http://localhost:8004"

from backend.service_orders.models.order import Order
from backend.service_orders.models.database import Base
from backend.service_orders.schemas.order import OrderCreate, OrderStatusEnum, OrderTypeEnum
from backend.service_orders.services.order_service import OrderService


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a database session for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# TEST CASES
# ============================================================================

@patch("backend.service_orders.services.order_service.httpx.Client")
def test_create_order_with_valid_customer_uid(mock_client_class, db_session):
    """
    Test Case 1: Create order with valid customer_uid

    Expected: Order is created successfully, CRM is called to validate customer.
    """
    # Arrange: Mock CRM response for valid customer
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "customer_uid": "CUST-123456",
        "first_name": "János",
        "last_name": "Kovács",
        "email": "janos.kovacs@example.com"
    }

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value.get.return_value = mock_response
    mock_client_instance.__exit__.return_value = None
    mock_client_class.return_value = mock_client_instance

    # Act: Create order with customer_uid
    order_data = OrderCreate(
        order_type=OrderTypeEnum.HELYBEN,
        status=OrderStatusEnum.NYITOTT,
        customer_uid="CUST-123456",
        guest_count=4,
        final_vat_rate=27.00
    )

    order = OrderService.create_order(db_session, order_data)

    # Assert: Order created successfully
    assert order.id is not None
    assert order.customer_uid == "CUST-123456"
    assert order.guest_count == 4
    assert order.order_type == "Helyben"
    assert order.status == "NYITOTT"

    # Verify CRM was called
    mock_client_instance.__enter__.return_value.get.assert_called_once()
    call_args = mock_client_instance.__enter__.return_value.get.call_args
    assert "CUST-123456" in str(call_args)


def test_create_order_without_customer_uid(db_session):
    """
    Test Case 2: Create order without customer_uid

    Expected: Order is created successfully without CRM validation.
    """
    # Act: Create order without customer_uid
    order_data = OrderCreate(
        order_type=OrderTypeEnum.ELVITEL,
        status=OrderStatusEnum.NYITOTT,
        guest_count=2,
        final_vat_rate=27.00
    )

    order = OrderService.create_order(db_session, order_data)

    # Assert: Order created successfully
    assert order.id is not None
    assert order.customer_uid is None  # No customer_uid
    assert order.guest_count == 2
    assert order.order_type == "Elvitel"
    assert order.status == "NYITOTT"


@patch("backend.service_orders.services.order_service.httpx.Client")
def test_create_order_with_invalid_customer_uid(mock_client_class, db_session):
    """
    Test Case 3: Create order with invalid (non-existent) customer_uid

    Expected: Order creation fails with 404 error.
    """
    # Arrange: Mock CRM response for non-existent customer
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Customer not found"

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value.get.return_value = mock_response
    mock_client_instance.__exit__.return_value = None
    mock_client_class.return_value = mock_client_instance

    # Act & Assert: Order creation should fail with 404
    order_data = OrderCreate(
        order_type=OrderTypeEnum.KISZALLITAS,
        status=OrderStatusEnum.NYITOTT,
        customer_uid="CUST-INVALID",
        guest_count=3,
        final_vat_rate=27.00
    )

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        OrderService.create_order(db_session, order_data)

    # Assert: Correct error status and message
    assert exc_info.value.status_code == 404
    assert "CUST-INVALID" in str(exc_info.value.detail)
    assert "nem található" in exc_info.value.detail.lower() or "not found" in exc_info.value.detail.lower()

    # Verify CRM was called
    mock_client_instance.__enter__.return_value.get.assert_called_once()


def test_guest_count_validation():
    """
    Test Case 4: Validate guest_count field constraints

    Expected: guest_count must be between 1 and 100.
    """
    # Test with guest_count = 0 (invalid, less than 1)
    with pytest.raises(ValidationError):
        OrderCreate(
            order_type=OrderTypeEnum.HELYBEN,
            status=OrderStatusEnum.NYITOTT,
            guest_count=0,  # Invalid: less than 1
            final_vat_rate=27.00
        )

    # Test with guest_count = 101 (invalid, greater than 100)
    with pytest.raises(ValidationError):
        OrderCreate(
            order_type=OrderTypeEnum.HELYBEN,
            status=OrderStatusEnum.NYITOTT,
            guest_count=101,  # Invalid: greater than 100
            final_vat_rate=27.00
        )

    # Test with valid guest_count
    order_data = OrderCreate(
        order_type=OrderTypeEnum.HELYBEN,
        status=OrderStatusEnum.NYITOTT,
        guest_count=50,  # Valid: between 1 and 100
        final_vat_rate=27.00
    )
    assert order_data.guest_count == 50


@patch("backend.service_orders.services.order_service.httpx.Client")
def test_create_order_crm_service_unavailable(mock_client_class, db_session):
    """
    Test Case 5: Handle CRM service unavailability gracefully

    Expected: Order creation fails with 503 Service Unavailable.
    """
    # Arrange: Mock CRM service connection error
    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value.get.side_effect = Exception("Connection refused")
    mock_client_instance.__exit__.return_value = None
    mock_client_class.return_value = mock_client_instance

    # Act & Assert: Order creation should fail with 503
    order_data = OrderCreate(
        order_type=OrderTypeEnum.HELYBEN,
        status=OrderStatusEnum.NYITOTT,
        customer_uid="CUST-123456",
        guest_count=2,
        final_vat_rate=27.00
    )

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        OrderService.create_order(db_session, order_data)

    # Assert: Correct error status and message
    assert exc_info.value.status_code == 503
    assert "CRM" in exc_info.value.detail or "szolgáltatás" in exc_info.value.detail


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
