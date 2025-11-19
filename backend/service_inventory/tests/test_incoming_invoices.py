"""
Unit tests for Incoming Invoices API endpoints.

Tests the NAV OSA integration for fetching incoming invoices and
saving them to the database.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.service_inventory.main import app
from backend.service_inventory.models.database import Base, get_db
from backend.service_inventory.models.incoming_invoice import IncomingInvoice
from backend.service_inventory.services.nav_osa_service import get_nav_osa_service, NAVOSAService


# Test database setup (SQLite in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_incoming_invoices.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_nav_osa_service():
    """Override NAV OSA service dependency for testing."""
    db = next(override_get_db())
    return NAVOSAService(db)


# Override dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_nav_osa_service] = override_get_nav_osa_service

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Create and drop test database tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_fetch_incoming_invoices_success(setup_database):
    """
    Test successful fetching of incoming invoices from NAV OSA.

    This test verifies that:
    1. The endpoint successfully calls the NAV OSA service
    2. Dummy invoice data is fetched
    3. Invoices are saved to the database with status 'NEW'
    4. The response contains the correct counts and invoice data
    """
    # Mock authentication by removing RBAC dependency
    # (In real tests, you would mock the require_permission dependency)
    from backend.service_admin.dependencies import require_permission
    app.dependency_overrides[require_permission("inventory:manage")] = lambda: None

    # Make request to fetch incoming invoices
    response = client.get("/api/v1/inventory/incoming-invoices/fetch-from-osa")

    # Assert successful response
    assert response.status_code == 200

    # Parse response
    data = response.json()

    # Assert response structure
    assert data["success"] is True
    assert "fetched_count" in data
    assert "saved_count" in data
    assert "message" in data
    assert "invoices" in data

    # Assert that invoices were fetched
    assert data["fetched_count"] > 0
    assert data["saved_count"] == data["fetched_count"]  # All should be new

    # Assert invoice structure
    invoices = data["invoices"]
    assert len(invoices) > 0

    first_invoice = invoices[0]
    assert "id" in first_invoice
    assert "invoice_number" in first_invoice
    assert "supplier_name" in first_invoice
    assert "total_amount" in first_invoice
    assert "status" in first_invoice
    assert first_invoice["status"] == "NEW"  # Default status

    # Verify invoices are in database
    db = TestingSessionLocal()
    db_invoices = db.query(IncomingInvoice).all()
    assert len(db_invoices) == data["saved_count"]

    # Verify first invoice details
    db_invoice = db_invoices[0]
    assert db_invoice.status == "NEW"
    assert db_invoice.invoice_number is not None
    assert db_invoice.supplier_name is not None
    assert db_invoice.total_amount is not None
    assert db_invoice.currency == "HUF"
    assert db_invoice.nav_data is not None  # Should contain full NAV response

    db.close()


def test_fetch_incoming_invoices_duplicate_handling(setup_database):
    """
    Test that duplicate invoices are not saved twice.

    This test verifies that:
    1. First fetch saves all invoices
    2. Second fetch with same data does not create duplicates
    3. The saved_count on second fetch is 0
    """
    # Mock authentication
    from backend.service_admin.dependencies import require_permission
    app.dependency_overrides[require_permission("inventory:manage")] = lambda: None

    # First fetch
    response1 = client.get("/api/v1/inventory/incoming-invoices/fetch-from-osa")
    assert response1.status_code == 200
    data1 = response1.json()
    first_saved_count = data1["saved_count"]

    # Second fetch (should find duplicates)
    response2 = client.get("/api/v1/inventory/incoming-invoices/fetch-from-osa")
    assert response2.status_code == 200
    data2 = response2.json()

    # Assert that no new invoices were saved
    assert data2["fetched_count"] == data1["fetched_count"]
    assert data2["saved_count"] == 0  # All duplicates

    # Verify database still has only the original invoices
    db = TestingSessionLocal()
    db_invoices = db.query(IncomingInvoice).all()
    assert len(db_invoices) == first_saved_count
    db.close()


def test_list_incoming_invoices(setup_database):
    """
    Test listing incoming invoices with pagination.

    This test verifies that:
    1. The list endpoint returns paginated results
    2. Filtering by status works correctly
    """
    # Mock authentication
    from backend.service_admin.dependencies import require_permission
    app.dependency_overrides[require_permission("inventory:manage")] = lambda: None

    # First, fetch some invoices
    fetch_response = client.get("/api/v1/inventory/incoming-invoices/fetch-from-osa")
    assert fetch_response.status_code == 200

    # Now list invoices
    list_response = client.get("/api/v1/inventory/incoming-invoices")
    assert list_response.status_code == 200

    data = list_response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data

    # Assert we have invoices
    assert data["total"] > 0
    assert len(data["items"]) > 0

    # Test status filtering
    status_response = client.get("/api/v1/inventory/incoming-invoices?status_filter=NEW")
    assert status_response.status_code == 200
    status_data = status_response.json()

    # All returned invoices should have status NEW
    for invoice in status_data["items"]:
        assert invoice["status"] == "NEW"


def test_get_incoming_invoice_by_id(setup_database):
    """
    Test getting a single incoming invoice by ID.

    This test verifies that:
    1. An invoice can be retrieved by its ID
    2. A 404 is returned for non-existent invoice IDs
    """
    # Mock authentication
    from backend.service_admin.dependencies import require_permission
    app.dependency_overrides[require_permission("inventory:manage")] = lambda: None

    # First, fetch some invoices
    fetch_response = client.get("/api/v1/inventory/incoming-invoices/fetch-from-osa")
    assert fetch_response.status_code == 200
    fetch_data = fetch_response.json()

    # Get the first invoice ID
    first_invoice_id = fetch_data["invoices"][0]["id"]

    # Get invoice by ID
    get_response = client.get(f"/api/v1/inventory/incoming-invoices/{first_invoice_id}")
    assert get_response.status_code == 200

    invoice_data = get_response.json()
    assert invoice_data["id"] == first_invoice_id
    assert "invoice_number" in invoice_data
    assert "status" in invoice_data

    # Test 404 for non-existent ID
    not_found_response = client.get("/api/v1/inventory/incoming-invoices/99999")
    assert not_found_response.status_code == 404


def test_fetch_with_date_filters(setup_database):
    """
    Test fetching invoices with date range filters.

    This test verifies that:
    1. Date filters are accepted as query parameters
    2. The endpoint successfully processes the request
    """
    # Mock authentication
    from backend.service_admin.dependencies import require_permission
    app.dependency_overrides[require_permission("inventory:manage")] = lambda: None

    # Test with date filters
    today = date.today().isoformat()
    response = client.get(
        f"/api/v1/inventory/incoming-invoices/fetch-from-osa"
        f"?from_date={today}&to_date={today}&test_mode=true"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["fetched_count"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
