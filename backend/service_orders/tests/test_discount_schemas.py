"""
Unit Tests for Discount Schemas
Module 1: Rendeléskezelés - Kedvezmények

Tesztek a kedvezmény sémák validálásához, beleértve:
- DiscountDetails séma validálása
- ApplyDiscountRequest séma validálása
- Értékhatárok ellenőrzése (0-100% percentage, >= 0 fixed)

V3.0 Feature: Task A4 - Discount Schema Validation Tests
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.service_orders.schemas.discount import (
    DiscountTypeEnum,
    DiscountDetails,
    ApplyDiscountRequest,
    ApplyOrderDiscountRequest,
    ApplyItemDiscountRequest,
    DiscountCalculationResult
)


class TestDiscountDetailsSchema:
    """Test DiscountDetails schema validation."""

    def test_valid_percentage_discount(self):
        """Test creating valid percentage discount details."""
        discount = DiscountDetails(
            type=DiscountTypeEnum.PERCENTAGE,
            value=Decimal("10.00"),
            reason="Törzsvásárlói kedvezmény",
            applied_by_user_id=1,
            applied_at=datetime.now(timezone.utc)
        )

        assert discount.type == DiscountTypeEnum.PERCENTAGE
        assert discount.value == Decimal("10.00")
        assert discount.reason == "Törzsvásárlói kedvezmény"
        assert discount.applied_by_user_id == 1

    def test_valid_fixed_discount(self):
        """Test creating valid fixed amount discount details."""
        discount = DiscountDetails(
            type=DiscountTypeEnum.FIXED,
            value=Decimal("500.00"),
            reason="Manager által engedélyezett",
            applied_by_user_id=2,
            coupon_code="WELCOME500"
        )

        assert discount.type == DiscountTypeEnum.FIXED
        assert discount.value == Decimal("500.00")
        assert discount.coupon_code == "WELCOME500"

    def test_percentage_discount_value_limits(self):
        """Test percentage discount value validation (0-100)."""
        # Valid: 0%
        discount = DiscountDetails(
            type=DiscountTypeEnum.PERCENTAGE,
            value=Decimal("0.00"),
            reason="Test",
            applied_by_user_id=1
        )
        assert discount.value == Decimal("0.00")

        # Valid: 100%
        discount = DiscountDetails(
            type=DiscountTypeEnum.PERCENTAGE,
            value=Decimal("100.00"),
            reason="Test",
            applied_by_user_id=1
        )
        assert discount.value == Decimal("100.00")

        # Valid: 50.5%
        discount = DiscountDetails(
            type=DiscountTypeEnum.PERCENTAGE,
            value=Decimal("50.50"),
            reason="Test",
            applied_by_user_id=1
        )
        assert discount.value == Decimal("50.50")

        # Invalid: > 100%
        with pytest.raises(ValidationError) as exc_info:
            DiscountDetails(
                type=DiscountTypeEnum.PERCENTAGE,
                value=Decimal("150.00"),
                reason="Test",
                applied_by_user_id=1
            )
        assert "between 0 and 100" in str(exc_info.value)

        # Invalid: < 0%
        with pytest.raises(ValidationError) as exc_info:
            DiscountDetails(
                type=DiscountTypeEnum.PERCENTAGE,
                value=Decimal("-10.00"),
                reason="Test",
                applied_by_user_id=1
            )
        assert "between 0 and 100" in str(exc_info.value)

    def test_fixed_discount_value_limits(self):
        """Test fixed discount value validation (>= 0)."""
        # Valid: 0 HUF
        discount = DiscountDetails(
            type=DiscountTypeEnum.FIXED,
            value=Decimal("0.00"),
            reason="Test",
            applied_by_user_id=1
        )
        assert discount.value == Decimal("0.00")

        # Valid: 1000 HUF
        discount = DiscountDetails(
            type=DiscountTypeEnum.FIXED,
            value=Decimal("1000.00"),
            reason="Test",
            applied_by_user_id=1
        )
        assert discount.value == Decimal("1000.00")

        # Invalid: negative amount
        with pytest.raises(ValidationError) as exc_info:
            DiscountDetails(
                type=DiscountTypeEnum.FIXED,
                value=Decimal("-500.00"),
                reason="Test",
                applied_by_user_id=1
            )
        assert "must be >= 0" in str(exc_info.value)


class TestApplyDiscountRequestSchema:
    """Test ApplyDiscountRequest schema validation."""

    def test_valid_order_discount_request(self):
        """Test creating valid order discount request."""
        request = ApplyOrderDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("15.00"),
            reason="Törzsvásárlói kedvezmény",
            coupon_code="LOYAL15"
        )

        assert request.discount_type == DiscountTypeEnum.PERCENTAGE
        assert request.discount_value == Decimal("15.00")
        assert request.reason == "Törzsvásárlói kedvezmény"
        assert request.coupon_code == "LOYAL15"

    def test_valid_item_discount_request(self):
        """Test creating valid item discount request."""
        request = ApplyItemDiscountRequest(
            discount_type=DiscountTypeEnum.FIXED,
            discount_value=Decimal("300.00"),
            reason="Hibás készítés"
        )

        assert request.discount_type == DiscountTypeEnum.FIXED
        assert request.discount_value == Decimal("300.00")
        assert request.reason == "Hibás készítés"
        assert request.coupon_code is None

    def test_reason_is_required(self):
        """Test that reason field is required."""
        with pytest.raises(ValidationError) as exc_info:
            ApplyDiscountRequest(
                discount_type=DiscountTypeEnum.PERCENTAGE,
                discount_value=Decimal("10.00"),
                reason=""  # Empty reason should fail
            )
        assert "reason" in str(exc_info.value).lower()

    def test_percentage_discount_request_value_validation(self):
        """Test percentage discount request value validation."""
        # Valid: 25%
        request = ApplyDiscountRequest(
            discount_type=DiscountTypeEnum.PERCENTAGE,
            discount_value=Decimal("25.00"),
            reason="Test"
        )
        assert request.discount_value == Decimal("25.00")

        # Invalid: > 100%
        with pytest.raises(ValidationError) as exc_info:
            ApplyDiscountRequest(
                discount_type=DiscountTypeEnum.PERCENTAGE,
                discount_value=Decimal("120.00"),
                reason="Test"
            )
        assert "between 0 and 100" in str(exc_info.value)

    def test_fixed_discount_request_value_validation(self):
        """Test fixed discount request value validation."""
        # Valid: 1000 HUF
        request = ApplyDiscountRequest(
            discount_type=DiscountTypeEnum.FIXED,
            discount_value=Decimal("1000.00"),
            reason="Test"
        )
        assert request.discount_value == Decimal("1000.00")

        # Invalid: negative amount
        with pytest.raises(ValidationError) as exc_info:
            ApplyDiscountRequest(
                discount_type=DiscountTypeEnum.FIXED,
                discount_value=Decimal("-200.00"),
                reason="Test"
            )
        assert "must be >= 0" in str(exc_info.value)


class TestDiscountCalculationResultSchema:
    """Test DiscountCalculationResult schema."""

    def test_valid_calculation_result(self):
        """Test creating valid calculation result."""
        discount_details = DiscountDetails(
            type=DiscountTypeEnum.PERCENTAGE,
            value=Decimal("10.00"),
            reason="Test",
            applied_by_user_id=1
        )

        result = DiscountCalculationResult(
            original_amount=Decimal("1000.00"),
            discount_amount=Decimal("100.00"),
            final_amount=Decimal("900.00"),
            discount_details=discount_details
        )

        assert result.original_amount == Decimal("1000.00")
        assert result.discount_amount == Decimal("100.00")
        assert result.final_amount == Decimal("900.00")
        assert result.discount_details.value == Decimal("10.00")


class TestDiscountTypeEnum:
    """Test DiscountTypeEnum enumeration."""

    def test_discount_type_values(self):
        """Test discount type enumeration values."""
        assert DiscountTypeEnum.PERCENTAGE.value == "percentage"
        assert DiscountTypeEnum.FIXED.value == "fixed"

    def test_discount_type_from_string(self):
        """Test creating discount type from string."""
        assert DiscountTypeEnum("percentage") == DiscountTypeEnum.PERCENTAGE
        assert DiscountTypeEnum("fixed") == DiscountTypeEnum.FIXED

    def test_invalid_discount_type(self):
        """Test that invalid discount type raises error."""
        with pytest.raises(ValueError):
            DiscountTypeEnum("invalid_type")
