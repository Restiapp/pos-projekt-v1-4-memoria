"""
Unit tests for OrderItem API endpoints with course and notes fields.

Tests:
1. Roundtrip test: course and notes data persists correctly through POST and GET
2. Validation test: invalid course values return 4xx errors
3. KDS payload includes course and notes information
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

# Set required environment variables before importing app
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")

from backend.service_orders.main import app
from backend.service_orders.models.database import Base, get_db
from backend.service_orders.models.order_item import OrderItem
from backend.service_orders.models.order import Order
from backend.service_orders.models.table import Table
from backend.service_orders.models.seat import Seat


# Test database setup (SQLite in-memory for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_order_items.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db):
    """Create a test client for the FastAPI app."""
    # Mock RBAC dependency to bypass authentication
    from backend.service_admin.dependencies import require_permission

    def mock_permission(*args, **kwargs):
        return lambda: None

    app.dependency_overrides[require_permission] = mock_permission

    with TestClient(app) as client:
        yield client

    # Clean up
    app.dependency_overrides.pop(require_permission, None)


@pytest.fixture(scope="function")
def setup_test_data(test_db):
    """Create test table, order for testing order items."""
    db = TestingSessionLocal()

    # Create test table
    table = Table(
        table_number=1,
        capacity=4,
        status="OCCUPIED"
    )
    db.add(table)
    db.commit()
    db.refresh(table)

    # Create test order
    order = Order(
        table_id=table.id,
        order_type="DINE_IN",
        status="IN_PROGRESS"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Create test seat
    seat = Seat(
        table_id=table.id,
        seat_number=1
    )
    db.add(seat)
    db.commit()
    db.refresh(seat)

    db.close()

    return {
        "table_id": table.id,
        "order_id": order.id,
        "seat_id": seat.id
    }


class TestOrderItemCourseAndNotes:
    """Test suite for course and notes functionality in order items."""

    def test_roundtrip_course_and_notes(self, test_client, setup_test_data):
        """
        Test that course and notes data persists correctly through POST and GET.

        Acceptance criteria:
        - POST request with course and notes saves correctly to database
        - GET request returns the same course and notes values
        """
        order_id = setup_test_data["order_id"]

        # Create order item with course and notes
        order_item_data = {
            "order_id": order_id,
            "product_id": 123,
            "seat_id": setup_test_data["seat_id"],
            "quantity": 2,
            "unit_price": 1500.00,
            "course": "starter",
            "notes": "No onions please",
            "selected_modifiers": None,
            "kds_station": "Konyha",
            "kds_status": "VÁRAKOZIK"
        }

        # POST: Create order item
        response = test_client.post(
            f"/api/v1/orders/{order_id}/items",
            json=order_item_data
        )

        assert response.status_code == 201, f"Failed to create order item: {response.text}"
        created_item = response.json()

        # Verify response contains course and notes
        assert created_item["course"] == "starter"
        assert created_item["notes"] == "No onions please"
        assert created_item["id"] is not None

        item_id = created_item["id"]

        # GET: Retrieve the created order item
        response = test_client.get(f"/api/v1/orders/items/{item_id}")

        assert response.status_code == 200
        retrieved_item = response.json()

        # Verify roundtrip: retrieved data matches original
        assert retrieved_item["course"] == "starter"
        assert retrieved_item["notes"] == "No onions please"
        assert retrieved_item["product_id"] == 123
        assert retrieved_item["quantity"] == 2

    def test_all_valid_course_types(self, test_client, setup_test_data):
        """Test that all valid course types are accepted."""
        order_id = setup_test_data["order_id"]
        valid_courses = ["starter", "main", "dessert", "drink", "other"]

        for course_type in valid_courses:
            order_item_data = {
                "order_id": order_id,
                "product_id": 100 + valid_courses.index(course_type),
                "quantity": 1,
                "unit_price": 1000.00,
                "course": course_type,
                "notes": f"Test {course_type}"
            }

            response = test_client.post(
                f"/api/v1/orders/{order_id}/items",
                json=order_item_data
            )

            assert response.status_code == 201, \
                f"Failed to create order item with course '{course_type}': {response.text}"

            created_item = response.json()
            assert created_item["course"] == course_type

    def test_invalid_course_returns_422(self, test_client, setup_test_data):
        """
        Test that invalid course values return 422 validation error.

        Acceptance criteria:
        - Invalid course value returns 4xx error (422 for validation)
        """
        order_id = setup_test_data["order_id"]

        # Create order item with INVALID course
        invalid_order_item_data = {
            "order_id": order_id,
            "product_id": 456,
            "quantity": 1,
            "unit_price": 2000.00,
            "course": "invalid_course_type",  # Invalid!
            "notes": "This should fail"
        }

        # POST with invalid course
        response = test_client.post(
            f"/api/v1/orders/{order_id}/items",
            json=invalid_order_item_data
        )

        # Should return 422 Unprocessable Entity (Pydantic validation error)
        assert response.status_code == 422, \
            f"Expected 422 for invalid course, got {response.status_code}"

        error_detail = response.json()
        assert "detail" in error_detail

        # Verify error mentions the course field
        error_str = str(error_detail["detail"]).lower()
        assert "course" in error_str

    def test_course_and_notes_optional(self, test_client, setup_test_data):
        """Test that course and notes are optional fields."""
        order_id = setup_test_data["order_id"]

        # Create order item WITHOUT course and notes
        order_item_data = {
            "order_id": order_id,
            "product_id": 789,
            "quantity": 1,
            "unit_price": 1200.00
        }

        response = test_client.post(
            f"/api/v1/orders/{order_id}/items",
            json=order_item_data
        )

        assert response.status_code == 201
        created_item = response.json()

        # Should be None/null when not provided
        assert created_item["course"] is None
        assert created_item["notes"] is None

    def test_update_course_and_notes(self, test_client, setup_test_data):
        """Test updating course and notes via PUT endpoint."""
        order_id = setup_test_data["order_id"]

        # Create initial order item
        order_item_data = {
            "order_id": order_id,
            "product_id": 111,
            "quantity": 1,
            "unit_price": 1800.00,
            "course": "main",
            "notes": "Medium rare"
        }

        response = test_client.post(
            f"/api/v1/orders/{order_id}/items",
            json=order_item_data
        )

        assert response.status_code == 201
        item_id = response.json()["id"]

        # Update course and notes
        update_data = {
            "course": "dessert",
            "notes": "Extra chocolate"
        }

        response = test_client.put(
            f"/api/v1/orders/items/{item_id}",
            json=update_data
        )

        assert response.status_code == 200
        updated_item = response.json()

        # Verify updates
        assert updated_item["course"] == "dessert"
        assert updated_item["notes"] == "Extra chocolate"

    def test_kds_payload_includes_course_and_notes(self, test_client, setup_test_data):
        """
        Test that KDS endpoints return course and notes in payload.

        Acceptance criteria:
        - KDS station query returns items with course and notes
        """
        order_id = setup_test_data["order_id"]

        # Create order item with KDS station
        order_item_data = {
            "order_id": order_id,
            "product_id": 222,
            "quantity": 1,
            "unit_price": 2500.00,
            "course": "main",
            "notes": "Gluten free",
            "kds_station": "Pizza",
            "kds_status": "VÁRAKOZIK"
        }

        response = test_client.post(
            f"/api/v1/orders/{order_id}/items",
            json=order_item_data
        )

        assert response.status_code == 201

        # Query KDS station endpoint
        response = test_client.get("/api/v1/orders/kds/stations/Pizza/items")

        assert response.status_code == 200
        kds_items = response.json()

        assert len(kds_items) > 0

        # Find our item in KDS response
        our_item = next((item for item in kds_items if item["product_id"] == 222), None)
        assert our_item is not None

        # Verify KDS payload includes course and notes
        assert our_item["course"] == "main"
        assert our_item["notes"] == "Gluten free"
        assert our_item["kds_station"] == "Pizza"

    def test_get_items_by_order_includes_course_and_notes(self, test_client, setup_test_data):
        """Test that GET /orders/{order_id}/items returns course and notes."""
        order_id = setup_test_data["order_id"]

        # Create multiple items with different courses
        items_to_create = [
            {"course": "starter", "notes": "Light portion", "product_id": 301},
            {"course": "main", "notes": "Well done", "product_id": 302},
            {"course": "dessert", "notes": "No sugar", "product_id": 303}
        ]

        for item_data in items_to_create:
            order_item = {
                "order_id": order_id,
                "product_id": item_data["product_id"],
                "quantity": 1,
                "unit_price": 1500.00,
                "course": item_data["course"],
                "notes": item_data["notes"]
            }

            response = test_client.post(
                f"/api/v1/orders/{order_id}/items",
                json=order_item
            )
            assert response.status_code == 201

        # Get all items for order
        response = test_client.get(f"/api/v1/orders/{order_id}/items")

        assert response.status_code == 200
        order_items = response.json()

        assert len(order_items) == 3

        # Verify each item has course and notes
        for item in order_items:
            assert "course" in item
            assert "notes" in item
            assert item["course"] in ["starter", "main", "dessert"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
