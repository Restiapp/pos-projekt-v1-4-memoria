"""
Integration Tests for Order + CRM Integration
==============================================

Tests the integration between service_orders and service_crm,
specifically testing customer_uid validation during order creation.

Test Coverage:
1. Create order with valid customer_uid (successful)
2. Create order without customer_uid (successful)
3. Create order with invalid customer_uid (fails with 404)

Requirements:
    pip install pytest pytest-mock httpx

Usage:
    pytest backend/service_orders/tests/test_order_crm_integration.py -v
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set environment variables before importing app
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["CRM_SERVICE_URL"] = "http://localhost:8004"

# Import application
from backend.service_orders.main import app
from backend.service_orders.models.database import Base, get_db
from backend.service_orders.config import settings


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

# In-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


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
def mock_crm_service():
    """
    Fixture to mock httpx.Client calls to service_crm.

    Returns a context manager that can be used with 'with' statement.
    """
    return patch("httpx.Client")


# ============================================================================
# TEST CASES
# ============================================================================

def test_create_order_with_valid_customer_uid(mock_crm_service):
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
        "email": "janos.kovacs@example.com",
        "loyalty_points": 100.0
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value.get.return_value = mock_response
    mock_crm_service.return_value = mock_client

    # Act: Create order with customer_uid
    with mock_crm_service:
        response = client.post("/api/v1/orders/", json={
            "order_type": "Helyben",
            "status": "NYITOTT",
            "customer_uid": "CUST-123456",
            "guest_count": 4,
            "final_vat_rate": 27.00
        })

    # Assert: Order created successfully
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["customer_uid"] == "CUST-123456"
    assert data["guest_count"] == 4
    assert data["order_type"] == "Helyben"
    assert data["status"] == "NYITOTT"
    assert "id" in data

    # Verify CRM was called
    mock_client.__enter__.return_value.get.assert_called_once()
    call_args = mock_client.__enter__.return_value.get.call_args
    assert "CUST-123456" in call_args[0][0]  # URL contains customer_uid


def test_create_order_without_customer_uid():
    """
    Test Case 2: Create order without customer_uid

    Expected: Order is created successfully without CRM validation.
    """
    # Act: Create order without customer_uid
    response = client.post("/api/v1/orders/", json={
        "order_type": "Elvitel",
        "status": "NYITOTT",
        "guest_count": 2,
        "final_vat_rate": 27.00
    })

    # Assert: Order created successfully
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["customer_uid"] is None  # No customer_uid
    assert data["guest_count"] == 2
    assert data["order_type"] == "Elvitel"
    assert data["status"] == "NYITOTT"
    assert "id" in data


def test_create_order_with_invalid_customer_uid(mock_crm_service):
    """
    Test Case 3: Create order with invalid (non-existent) customer_uid

    Expected: Order creation fails with 404 error.
    """
    # Arrange: Mock CRM response for non-existent customer
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Customer not found"

    mock_client = MagicMock()
    mock_client.__enter__.return_value.get.return_value = mock_response
    mock_crm_service.return_value = mock_client

    # Act: Create order with invalid customer_uid
    with mock_crm_service:
        response = client.post("/api/v1/orders/", json={
            "order_type": "Kiszállítás",
            "status": "NYITOTT",
            "customer_uid": "CUST-INVALID",
            "guest_count": 3,
            "final_vat_rate": 27.00
        })

    # Assert: Order creation fails with 404
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    data = response.json()
    assert "detail" in data
    assert "nem található" in data["detail"].lower() or "not found" in data["detail"].lower()
    assert "CUST-INVALID" in data["detail"]

    # Verify CRM was called
    mock_client.__enter__.return_value.get.assert_called_once()
    call_args = mock_client.__enter__.return_value.get.call_args
    assert "CUST-INVALID" in call_args[0][0]  # URL contains customer_uid


def test_create_order_with_guest_count_validation():
    """
    Test Case 4: Validate guest_count field constraints

    Expected: guest_count must be between 1 and 100.
    """
    # Test with guest_count = 0 (invalid, less than 1)
    response = client.post("/api/v1/orders/", json={
        "order_type": "Helyben",
        "status": "NYITOTT",
        "guest_count": 0,  # Invalid: less than 1
        "final_vat_rate": 27.00
    })
    assert response.status_code == 422  # Validation error

    # Test with guest_count = 101 (invalid, greater than 100)
    response = client.post("/api/v1/orders/", json={
        "order_type": "Helyben",
        "status": "NYITOTT",
        "guest_count": 101,  # Invalid: greater than 100
        "final_vat_rate": 27.00
    })
    assert response.status_code == 422  # Validation error

    # Test with valid guest_count
    response = client.post("/api/v1/orders/", json={
        "order_type": "Helyben",
        "status": "NYITOTT",
        "guest_count": 50,  # Valid: between 1 and 100
        "final_vat_rate": 27.00
    })
    assert response.status_code == 201  # Success


def test_create_order_crm_service_unavailable(mock_crm_service):
    """
    Test Case 5: Handle CRM service unavailability gracefully

    Expected: Order creation fails with 503 Service Unavailable.
    """
    # Arrange: Mock CRM service connection error
    mock_client = MagicMock()
    mock_client.__enter__.return_value.get.side_effect = Exception("Connection refused")
    mock_crm_service.return_value = mock_client

    # Act: Create order with customer_uid (CRM unavailable)
    with mock_crm_service:
        response = client.post("/api/v1/orders/", json={
            "order_type": "Helyben",
            "status": "NYITOTT",
            "customer_uid": "CUST-123456",
            "guest_count": 2,
            "final_vat_rate": 27.00
        })

    # Assert: Order creation fails with 503
    assert response.status_code == 503, f"Expected 503, got {response.status_code}: {response.text}"

    data = response.json()
    assert "detail" in data
    assert "CRM" in data["detail"] or "szolgáltatás" in data["detail"]


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
