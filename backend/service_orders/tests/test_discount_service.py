"""
Unit Tests for Discount Service
Module 1: Rendeléskezelés - Kedvezmények

Tesztek a kedvezmény szolgáltatáshoz, beleértve:
- Kedvezmény számítások validálása
- Rendelés-szintű kedvezmények alkalmazása
- Tétel-szintű kedvezmények alkalmazása
- Végösszeg újraszámítása kedvezmények után

V3.0 Feature: Task A4 - Discount Model Tests
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException

from backend.service_orders.models.database import Base
from backend.service_orders.models.order import Order
from backend.service_orders.models.order_item import OrderItem
from backend.service_orders.models.table import Table
from backend.service_orders.services.discount_service import DiscountService
from backend.service_orders.schemas.discount import (
    DiscountTypeEnum,
    ApplyOrderDiscountRequest,
    ApplyItemDiscountRequest
)


# ============================================================================
# Test Database Setup
# ============================================================================

@pytest.fixture(scope="function")
def db_session():
    """
    Create an in-memory SQLite database for testing.

    This fixture creates a fresh database for each test function,
    ensuring test isolation.
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    # Cleanup
    session.close()


@pytest.fixture
def sample_table(db_session: Session):
    """Create a sample table for testing."""
    table = Table(
        table_number=1,
        capacity=4,
        status="Foglalt",
        location="Ablak melletti"
    )
    db_session.add(table)
    db_session.commit()
    db_session.refresh(table)
    return table


@pytest.fixture
def sample_order(db_session: Session, sample_table: Table):
    """Create a sample order for testing."""
    order = Order(
        order_type="Helyben",
        status="NYITOTT",
        table_id=sample_table.id,
        total_amount=Decimal("0.00"),
        final_vat_rate=Decimal("27.00")
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_order_items(db_session: Session, sample_order: Order):
    """Create sample order items for testing."""
    items = [
        OrderItem(
            order_id=sample_order.id,
            product_id=1,
            quantity=2,
            unit_price=Decimal("1000.00"),
            kds_status="VÁRAKOZIK"
        ),
        OrderItem(
            order_id=sample_order.id,
            product_id=2,
            quantity=1,
            unit_price=Decimal("500.00"),
            kds_status="VÁRAKOZIK"
        )
    ]

    for item in items:
        db_session.add(item)

    db_session.commit()

    for item in items:
        db_session.refresh(item)

    return items


# ============================================================================
# Discount Calculation Tests
# ============================================================================

class TestDiscountCalculations:
    """Test discount calculation logic."""

    def test_calculate_percentage_discount(self):
        """Test percentage discount calculation."""
        # 10% off 1000 HUF = 100 HUF
        result = DiscountService.calculate_discount_amount(
            Decimal("1000.00"),
            DiscountTypeEnum.PERCENTAGE,
            Decimal("10.00")
        )
        assert result == Decimal("100.00")

        # 25% off 2000 HUF = 500 HUF
        result = DiscountService.calculate_discount_amount(
            Decimal("2000.00"),
            DiscountTypeEnum.PERCENTAGE,
            Decimal("25.00")
        )
        assert result == Decimal("500.00")

        # 50% off 1500 HUF = 750 HUF
        result = DiscountService.calculate_discount_amount(
            Decimal("1500.00"),
            DiscountTypeEnum.PERCENTAGE,
            Decimal("50.00")
        )
        assert result == Decimal("750.00")

    def test_calculate_fixed_discount(self):
        """Test fixed amount discount calculation."""
        # 500 HUF off 1000 HUF = 500 HUF
        result = DiscountService.calculate_discount_amount(
            Decimal("1000.00"),
            DiscountTypeEnum.FIXED,
            Decimal("500.00")
        )
        assert result == Decimal("500.00")

        # 200 HUF off 1500 HUF = 200 HUF
        result = DiscountService.calculate_discount_amount(
            Decimal("1500.00"),
            DiscountTypeEnum.FIXED,
            Decimal("200.00")
        )
        assert result == Decimal("200.00")

    def test_discount_cannot_exceed_original_amount(self):
        """Test that discount is capped at original amount."""
        # Trying to discount 1500 HUF from 1000 HUF should cap at 1000 HUF
        result = DiscountService.calculate_discount_amount(
            Decimal("1000.00"),
            DiscountTypeEnum.FIXED,
            Decimal("1500.00")
        )
        assert result == Decimal("1000.00")

        # 150% discount should cap at 100% (full amount)
        result = DiscountService.calculate_discount_amount(
            Decimal("1000.00"),
            DiscountTypeEnum.PERCENTAGE,
            Decimal("150.00")
        )
        assert result == Decimal("1000.00")

    def test_calculate_final_amount(self):
        """Test final amount calculation after discount."""
        # 1000 - 100 = 900
        result = DiscountService.calculate_final_amount(
            Decimal("1000.00"),
            Decimal("100.00")
        )
        assert result == Decimal("900.00")

        # 2500 - 500 = 2000
        result = DiscountService.calculate_final_amount(
            Decimal("2500.00"),
            Decimal("500.00")
        )
        assert result == Decimal("2000.00")

    def test_final_amount_cannot_be_negative(self):
        """Test that final amount is never negative."""
        # Discount exceeds original amount - should return 0
        result = DiscountService.calculate_final_amount(
            Decimal("1000.00"),
            Decimal("1500.00")
        )
        assert result == Decimal("0.00")

    def test_invalid_negative_original_amount(self):
        """Test that negative original amounts raise ValueError."""
        with pytest.raises(ValueError, match="nem lehet negatív"):
            DiscountService.calculate_discount_amount(
                Decimal("-1000.00"),
                DiscountTypeEnum.PERCENTAGE,
                Decimal("10.00")
            )


# ============================================================================
# Order-Level Discount Tests
# ============================================================================

class TestOrderLevelDiscounts:
    """Test order-level discount application."""

    def test_apply_percentage_discount_to_order(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test applying percentage discount to entire order."""
        # Order has 2 items: 2x1000 + 1x500 = 2500 HUF
        # Apply 10% discount = 250 HUF off, final = 2250 HUF

        request = ApplyOrderDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("10.00"),
            reason="Törzsvásárlói kedvezmény"
        )

        result = DiscountService.apply_order_discount(
            db=db_session,
            order_id=sample_order.id,
            discount_request=request,
            applied_by_user_id=1
        )

        assert result.order_id == sample_order.id
        assert result.calculation.original_amount == Decimal("2500.00")
        assert result.calculation.discount_amount == Decimal("250.00")
        assert result.calculation.final_amount == Decimal("2250.00")
        assert result.updated_total == Decimal("2250.00")
        assert result.calculation.discount_details.type == DiscountTypeEnum.PERCENTAGE
        assert result.calculation.discount_details.value == Decimal("10.00")
        assert result.calculation.discount_details.applied_by_user_id == 1

    def test_apply_fixed_discount_to_order(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test applying fixed amount discount to entire order."""
        # Order total: 2500 HUF
        # Apply 500 HUF discount, final = 2000 HUF

        request = ApplyOrderDiscountRequest(
            discount_type=DiscountTypeEnum.FIXED,
            discount_value=Decimal("500.00"),
            reason="Manager által engedélyezett"
        )

        result = DiscountService.apply_order_discount(
            db=db_session,
            order_id=sample_order.id,
            discount_request=request,
            applied_by_user_id=2
        )

        assert result.order_id == sample_order.id
        assert result.calculation.original_amount == Decimal("2500.00")
        assert result.calculation.discount_amount == Decimal("500.00")
        assert result.calculation.final_amount == Decimal("2000.00")
        assert result.updated_total == Decimal("2000.00")

    def test_cannot_apply_discount_to_closed_order(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test that discount cannot be applied to closed orders."""
        # Close the order
        sample_order.status = "LEZART"
        db_session.commit()

        request = ApplyOrderDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("10.00"),
            reason="Test"
        )

        with pytest.raises(HTTPException) as exc_info:
            DiscountService.apply_order_discount(
                db=db_session,
                order_id=sample_order.id,
                discount_request=request,
                applied_by_user_id=1
            )

        assert exc_info.value.status_code == 400
        assert "LEZART" in str(exc_info.value.detail)

    def test_cannot_apply_discount_to_cancelled_order(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test that discount cannot be applied to cancelled orders."""
        # Cancel the order
        sample_order.status = "SZTORNÓ"
        db_session.commit()

        request = ApplyOrderDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("10.00"),
            reason="Test"
        )

        with pytest.raises(HTTPException) as exc_info:
            DiscountService.apply_order_discount(
                db=db_session,
                order_id=sample_order.id,
                discount_request=request,
                applied_by_user_id=1
            )

        assert exc_info.value.status_code == 400

    def test_apply_discount_to_nonexistent_order(self, db_session: Session):
        """Test that applying discount to non-existent order raises 404."""
        request = ApplyOrderDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("10.00"),
            reason="Test"
        )

        with pytest.raises(HTTPException) as exc_info:
            DiscountService.apply_order_discount(
                db=db_session,
                order_id=99999,
                discount_request=request,
                applied_by_user_id=1
            )

        assert exc_info.value.status_code == 404


# ============================================================================
# Item-Level Discount Tests
# ============================================================================

class TestItemLevelDiscounts:
    """Test item-level discount application."""

    def test_apply_percentage_discount_to_item(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test applying percentage discount to a single item."""
        # First item: 2 x 1000 = 2000 HUF
        # Apply 10% discount = 200 HUF off, item final = 1800 HUF
        # Order total: 1800 + 500 = 2300 HUF

        item = sample_order_items[0]

        request = ApplyItemDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("10.00"),
            reason="Hibás készítés"
        )

        result = DiscountService.apply_item_discount(
            db=db_session,
            item_id=item.id,
            discount_request=request,
            applied_by_user_id=1
        )

        assert result.item_id == item.id
        assert result.order_id == sample_order.id
        assert result.calculation.original_amount == Decimal("2000.00")
        assert result.calculation.discount_amount == Decimal("200.00")
        assert result.calculation.final_amount == Decimal("1800.00")
        assert result.updated_item_total == Decimal("1800.00")
        assert result.updated_order_total == Decimal("2300.00")

    def test_apply_fixed_discount_to_item(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test applying fixed amount discount to a single item."""
        # Second item: 1 x 500 = 500 HUF
        # Apply 100 HUF discount, item final = 400 HUF
        # Order total: 2000 + 400 = 2400 HUF

        item = sample_order_items[1]

        request = ApplyItemDiscountRequest(
            discount_type=DiscountTypeEnum.FIXED,
            discount_value=Decimal("100.00"),
            reason="Kompenzáció"
        )

        result = DiscountService.apply_item_discount(
            db=db_session,
            item_id=item.id,
            discount_request=request,
            applied_by_user_id=2
        )

        assert result.calculation.original_amount == Decimal("500.00")
        assert result.calculation.discount_amount == Decimal("100.00")
        assert result.calculation.final_amount == Decimal("400.00")
        assert result.updated_order_total == Decimal("2400.00")

    def test_item_discount_recalculates_order_total(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test that applying item discount recalculates order total."""
        # Apply discount to first item
        item1 = sample_order_items[0]

        request = ApplyItemDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("20.00"),
            reason="Test"
        )

        result = DiscountService.apply_item_discount(
            db=db_session,
            item_id=item1.id,
            discount_request=request,
            applied_by_user_id=1
        )

        # Item1: 2000 - 400 (20%) = 1600
        # Item2: 500
        # Total: 2100
        assert result.updated_order_total == Decimal("2100.00")

        # Verify order total was updated in database
        db_session.refresh(sample_order)
        assert sample_order.total_amount == Decimal("2100.00")

    def test_cannot_apply_discount_to_nonexistent_item(self, db_session: Session):
        """Test that applying discount to non-existent item raises 404."""
        request = ApplyItemDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("10.00"),
            reason="Test"
        )

        with pytest.raises(HTTPException) as exc_info:
            DiscountService.apply_item_discount(
                db=db_session,
                item_id=99999,
                discount_request=request,
                applied_by_user_id=1
            )

        assert exc_info.value.status_code == 404


# ============================================================================
# Order Total Recalculation Tests
# ============================================================================

class TestOrderTotalRecalculation:
    """Test order total recalculation with various discount combinations."""

    def test_recalculate_order_with_no_discounts(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test recalculating order total without any discounts."""
        # Item1: 2 x 1000 = 2000
        # Item2: 1 x 500 = 500
        # Total: 2500

        total = DiscountService.recalculate_order_total(db_session, sample_order)
        assert total == Decimal("2500.00")

    def test_recalculate_order_with_item_discounts(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test recalculating order total with item-level discounts."""
        # Apply 10% discount to item1
        item1 = sample_order_items[0]
        item1.discount_details = {
            "type": "percentage",
            "value": 10.0,
            "reason": "Test",
            "applied_by_user_id": 1
        }

        # Apply 50 HUF discount to item2
        item2 = sample_order_items[1]
        item2.discount_details = {
            "type": "fixed",
            "value": 50.0,
            "reason": "Test",
            "applied_by_user_id": 1
        }

        db_session.commit()

        # Item1: 2000 - 200 (10%) = 1800
        # Item2: 500 - 50 = 450
        # Total: 2250

        total = DiscountService.recalculate_order_total(db_session, sample_order)
        assert total == Decimal("2250.00")

    def test_recalculate_order_with_order_and_item_discounts(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test recalculating order total with both item and order discounts."""
        # Apply 10% discount to item1
        item1 = sample_order_items[0]
        item1.discount_details = {
            "type": "percentage",
            "value": 10.0,
            "reason": "Item discount",
            "applied_by_user_id": 1
        }

        # Apply 5% order-level discount
        sample_order.discount_details = {
            "type": "percentage",
            "value": 5.0,
            "reason": "Order discount",
            "applied_by_user_id": 1
        }

        db_session.commit()

        # Item1: 2000 - 200 (10%) = 1800
        # Item2: 500 (no discount)
        # Subtotal: 2300
        # Order discount: 2300 - 115 (5%) = 2185

        total = DiscountService.recalculate_order_total(db_session, sample_order)
        assert total == Decimal("2185.00")


# ============================================================================
# Edge Cases and Validation Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and validation."""

    def test_zero_amount_order(self, db_session: Session, sample_order: Order):
        """Test handling of order with zero amount."""
        # Create an order with no items
        request = ApplyOrderDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("10.00"),
            reason="Test"
        )

        result = DiscountService.apply_order_discount(
            db=db_session,
            order_id=sample_order.id,
            discount_request=request,
            applied_by_user_id=1
        )

        # Discount on 0 should be 0
        assert result.calculation.original_amount == Decimal("0.00")
        assert result.calculation.discount_amount == Decimal("0.00")
        assert result.calculation.final_amount == Decimal("0.00")

    def test_100_percent_discount(
        self,
        db_session: Session,
        sample_order: Order,
        sample_order_items: list[OrderItem]
    ):
        """Test 100% discount (free order)."""
        request = ApplyOrderDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("100.00"),
            reason="Manager approval"
        )

        result = DiscountService.apply_order_discount(
            db=db_session,
            order_id=sample_order.id,
            discount_request=request,
            applied_by_user_id=1
        )

        assert result.calculation.final_amount == Decimal("0.00")
        assert result.updated_total == Decimal("0.00")
