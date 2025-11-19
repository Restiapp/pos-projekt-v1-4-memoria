"""
KDS Service Tests - Kitchen Display System
Module 1: Rendeléskezelés és Asztalok / Epic B: Konyha/KDS

Tesztek a Kitchen Display System funkcionalitáshoz.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from backend.service_orders.models.database import Base
from backend.service_orders.models.order import Order
from backend.service_orders.models.order_item import OrderItem, KDSStatus
from backend.service_orders.models.table import Table
from backend.service_orders.services.kds_service import KDSService
from backend.service_orders.schemas.order_item import KDSStatusEnum
from backend.service_orders.main import app


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_kds.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database for each test.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_table(db_session: Session):
    """Create a sample table for testing."""
    table = Table(
        table_number=5,
        capacity=4,
        status="OCCUPIED",
        section="Main"
    )
    db_session.add(table)
    db_session.commit()
    db_session.refresh(table)
    return table


@pytest.fixture
def sample_order(db_session: Session, sample_table):
    """Create a sample order for testing."""
    order = Order(
        order_type="Helyben",
        status="NYITOTT",
        table_id=sample_table.id,
        total_amount=Decimal("3000.00"),
        final_vat_rate=Decimal("27.00")
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_order_items(db_session: Session, sample_order):
    """Create sample order items for testing."""
    items = [
        OrderItem(
            order_id=sample_order.id,
            product_id=1,
            quantity=1,
            unit_price=Decimal("1500.00"),
            kds_station="GRILL",
            kds_status=KDSStatus.WAITING
        ),
        OrderItem(
            order_id=sample_order.id,
            product_id=2,
            quantity=2,
            unit_price=Decimal("750.00"),
            kds_station="COLD",
            kds_status=KDSStatus.WAITING
        )
    ]
    for item in items:
        db_session.add(item)
    db_session.commit()
    for item in items:
        db_session.refresh(item)
    return items


class TestKDSStatusEnum:
    """Test KDS Status Enum values and transitions."""

    def test_kds_status_values(self):
        """Test that KDS status enum has correct values."""
        assert KDSStatus.WAITING.value == "WAITING"
        assert KDSStatus.PREPARING.value == "PREPARING"
        assert KDSStatus.READY.value == "READY"
        assert KDSStatus.SERVED.value == "SERVED"

    def test_kds_status_enum_conversion(self):
        """Test conversion between schema and model enums."""
        schema_enum = KDSStatusEnum.WAITING
        model_enum = KDSStatus(schema_enum.value)
        assert model_enum == KDSStatus.WAITING


class TestKDSService:
    """Test KDS Service business logic."""

    def test_get_active_items_no_filter(self, db_session, sample_order_items):
        """Test getting all active items without station filter."""
        service = KDSService()
        active_items = service.get_active_items(db_session)

        assert len(active_items) == 1  # One order
        assert active_items[0]["order_id"] == sample_order_items[0].order_id
        assert len(active_items[0]["items"]) == 2  # Two items in the order

    def test_get_active_items_with_station_filter(self, db_session, sample_order_items):
        """Test getting active items filtered by station."""
        service = KDSService()
        active_items = service.get_active_items(db_session, station="GRILL")

        assert len(active_items) == 1
        assert len(active_items[0]["items"]) == 1  # Only GRILL item
        assert active_items[0]["items"][0].kds_station == "GRILL"

    def test_get_active_items_excludes_served(self, db_session, sample_order_items):
        """Test that served items are excluded from active items."""
        # Mark one item as SERVED
        sample_order_items[0].kds_status = KDSStatus.SERVED
        db_session.commit()

        service = KDSService()
        active_items = service.get_active_items(db_session)

        assert len(active_items) == 1
        assert len(active_items[0]["items"]) == 1  # Only non-served item
        assert active_items[0]["items"][0].id == sample_order_items[1].id

    def test_update_item_status(self, db_session, sample_order_items):
        """Test updating item status."""
        service = KDSService()
        item_id = sample_order_items[0].id

        updated_item = service.update_item_status(
            db_session,
            item_id,
            KDSStatusEnum.PREPARING
        )

        assert updated_item is not None
        assert updated_item.kds_status == KDSStatusEnum.PREPARING

    def test_update_item_status_invalid_id(self, db_session):
        """Test updating status for non-existent item."""
        service = KDSService()
        updated_item = service.update_item_status(
            db_session,
            99999,
            KDSStatusEnum.PREPARING
        )

        assert updated_item is None

    def test_order_status_update_all_ready(self, db_session, sample_order, sample_order_items):
        """Test that order status updates to FELDOLGOZVA when all items are READY."""
        service = KDSService()

        # Update first item to READY
        service.update_item_status(
            db_session,
            sample_order_items[0].id,
            KDSStatusEnum.READY
        )

        # Order should still be NYITOTT
        db_session.refresh(sample_order)
        assert sample_order.status == "NYITOTT"

        # Update second item to READY
        service.update_item_status(
            db_session,
            sample_order_items[1].id,
            KDSStatusEnum.READY
        )

        # Now order should be FELDOLGOZVA
        db_session.refresh(sample_order)
        assert sample_order.status == "FELDOLGOZVA"

    def test_order_status_no_update_if_not_all_ready(self, db_session, sample_order, sample_order_items):
        """Test that order status doesn't update if not all items are READY."""
        service = KDSService()

        # Update only first item to READY
        service.update_item_status(
            db_session,
            sample_order_items[0].id,
            KDSStatusEnum.READY
        )

        # Update second item to PREPARING (not READY)
        service.update_item_status(
            db_session,
            sample_order_items[1].id,
            KDSStatusEnum.PREPARING
        )

        # Order should still be NYITOTT
        db_session.refresh(sample_order)
        assert sample_order.status == "NYITOTT"

    def test_get_items_by_station_and_status(self, db_session, sample_order_items):
        """Test getting items by station and status."""
        service = KDSService()

        # Get GRILL items with WAITING status
        items = service.get_items_by_station_and_status(
            db_session,
            "GRILL",
            KDSStatusEnum.WAITING
        )

        assert len(items) == 1
        assert items[0].kds_station == "GRILL"
        assert items[0].kds_status == KDSStatusEnum.WAITING

    def test_get_items_by_station_no_status_filter(self, db_session, sample_order_items):
        """Test getting items by station without status filter."""
        service = KDSService()

        # Update one COLD item to PREPARING
        sample_order_items[1].kds_status = KDSStatus.PREPARING
        db_session.commit()

        # Get all COLD items regardless of status
        items = service.get_items_by_station_and_status(
            db_session,
            "COLD",
            None
        )

        assert len(items) == 1
        assert items[0].kds_station == "COLD"


class TestKDSStatusTransitions:
    """Test KDS status transition workflows."""

    def test_status_transition_workflow(self, db_session, sample_order_items):
        """Test full status transition: WAITING -> PREPARING -> READY -> SERVED."""
        service = KDSService()
        item_id = sample_order_items[0].id

        # WAITING -> PREPARING
        item = service.update_item_status(db_session, item_id, KDSStatusEnum.PREPARING)
        assert item.kds_status == KDSStatusEnum.PREPARING

        # PREPARING -> READY
        item = service.update_item_status(db_session, item_id, KDSStatusEnum.READY)
        assert item.kds_status == KDSStatusEnum.READY

        # READY -> SERVED
        item = service.update_item_status(db_session, item_id, KDSStatusEnum.SERVED)
        assert item.kds_status == KDSStatusEnum.SERVED

    def test_status_can_skip_steps(self, db_session, sample_order_items):
        """Test that status can skip steps (e.g., WAITING -> READY directly)."""
        service = KDSService()
        item_id = sample_order_items[0].id

        # WAITING -> READY (skip PREPARING)
        item = service.update_item_status(db_session, item_id, KDSStatusEnum.READY)
        assert item.kds_status == KDSStatusEnum.READY


class TestKDSGrouping:
    """Test KDS item grouping by table/order."""

    def test_multiple_orders_grouping(self, db_session, sample_table):
        """Test that items from different orders are grouped separately."""
        # Create two orders
        order1 = Order(
            order_type="Helyben",
            status="NYITOTT",
            table_id=sample_table.id,
            total_amount=Decimal("1500.00")
        )
        order2 = Order(
            order_type="Helyben",
            status="NYITOTT",
            table_id=sample_table.id,
            total_amount=Decimal("2000.00")
        )
        db_session.add_all([order1, order2])
        db_session.commit()

        # Add items to each order
        item1 = OrderItem(
            order_id=order1.id,
            product_id=1,
            quantity=1,
            unit_price=Decimal("1500.00"),
            kds_station="GRILL",
            kds_status=KDSStatus.WAITING
        )
        item2 = OrderItem(
            order_id=order2.id,
            product_id=2,
            quantity=1,
            unit_price=Decimal("2000.00"),
            kds_station="GRILL",
            kds_status=KDSStatus.WAITING
        )
        db_session.add_all([item1, item2])
        db_session.commit()

        service = KDSService()
        active_items = service.get_active_items(db_session)

        # Should have 2 groups (one per order)
        assert len(active_items) == 2
        assert active_items[0]["order_id"] != active_items[1]["order_id"]


class TestKDSEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_active_items(self, db_session):
        """Test getting active items when there are none."""
        service = KDSService()
        active_items = service.get_active_items(db_session)

        assert len(active_items) == 0

    def test_all_items_served(self, db_session, sample_order_items):
        """Test that no items are returned when all are SERVED."""
        # Mark all items as SERVED
        for item in sample_order_items:
            item.kds_status = KDSStatus.SERVED
        db_session.commit()

        service = KDSService()
        active_items = service.get_active_items(db_session)

        assert len(active_items) == 0

    def test_invalid_status_value(self, db_session, sample_order_items):
        """Test that invalid status values raise ValueError."""
        service = KDSService()

        with pytest.raises(ValueError):
            # This should raise ValueError because we're creating an invalid enum
            KDSStatus("INVALID_STATUS")
