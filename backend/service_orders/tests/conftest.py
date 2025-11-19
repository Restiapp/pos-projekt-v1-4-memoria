"""
Pytest Configuration and Fixtures for Service Orders Tests
Sprint 2 - Task A5: Payment API Tests
"""

import os
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment variables BEFORE importing app
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
os.environ["PORT"] = "8002"
os.environ["MENU_SERVICE_URL"] = "http://localhost:8001"

from backend.service_orders.main import app
from backend.service_orders.models.database import Base, get_db
from backend.service_orders.models.order import Order
from backend.service_orders.models.table import Table
from backend.service_admin.dependencies import require_permission


# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.

    Yields:
        Session: SQLAlchemy database session
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a TestClient with database session override.

    Args:
        db_session: Database session fixture

    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_require_permission(permission: str):
        """Mock RBAC permission check - always allow in tests."""
        return lambda: None

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_permission] = override_require_permission

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_table(db_session):
    """
    Create a sample table for testing.

    Args:
        db_session: Database session fixture

    Returns:
        Table: Created table object
    """
    table = Table(
        table_number=10,
        status="FOGLALT",
        capacity=4
    )
    db_session.add(table)
    db_session.commit()
    db_session.refresh(table)
    return table


@pytest.fixture
def sample_order(db_session, sample_table):
    """
    Create a sample order for testing payments.

    Args:
        db_session: Database session fixture
        sample_table: Table fixture

    Returns:
        Order: Created order object with total_amount set
    """
    order = Order(
        order_type="Helyben",
        status="NYITOTT",
        table_id=sample_table.id,
        total_amount=Decimal("5000.00"),
        final_vat_rate=Decimal("27.00")
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order
