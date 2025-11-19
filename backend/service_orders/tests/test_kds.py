"""
Unit Tests for KDS (Kitchen Display System) Module
Module 1: Rendeléskezelés és Asztalok

This module contains unit tests for the KDS backend model implementation,
including status transition validation and API endpoint testing.

Task B1: KDS Backend Model - Unit Tests
"""

import pytest
from backend.service_orders.enums import (
    KDSStatus,
    validate_kds_status_transition,
    get_allowed_transitions
)


class TestKDSStatusEnum:
    """Test cases for KDSStatus enum."""

    def test_kds_status_values(self):
        """Test that KDSStatus enum has all required values."""
        assert KDSStatus.WAITING == "WAITING"
        assert KDSStatus.IN_PROGRESS == "IN_PROGRESS"
        assert KDSStatus.READY == "READY"

    def test_kds_status_values_list(self):
        """Test that values() returns all status values."""
        values = KDSStatus.values()
        assert len(values) == 3
        assert "WAITING" in values
        assert "IN_PROGRESS" in values
        assert "READY" in values

    def test_kds_status_is_valid(self):
        """Test status validation."""
        assert KDSStatus.is_valid("WAITING") is True
        assert KDSStatus.is_valid("IN_PROGRESS") is True
        assert KDSStatus.is_valid("READY") is True
        assert KDSStatus.is_valid("INVALID") is False
        assert KDSStatus.is_valid("") is False
        assert KDSStatus.is_valid("waiting") is False  # Case sensitive


class TestKDSStatusTransitions:
    """Test cases for KDS status transition validation."""

    def test_valid_transition_waiting_to_in_progress(self):
        """Test valid transition from WAITING to IN_PROGRESS."""
        assert validate_kds_status_transition("WAITING", "IN_PROGRESS") is True

    def test_valid_transition_in_progress_to_ready(self):
        """Test valid transition from IN_PROGRESS to READY."""
        assert validate_kds_status_transition("IN_PROGRESS", "READY") is True

    def test_valid_transition_in_progress_to_waiting(self):
        """Test valid transition from IN_PROGRESS back to WAITING."""
        assert validate_kds_status_transition("IN_PROGRESS", "WAITING") is True

    def test_valid_transition_ready_to_in_progress(self):
        """Test valid transition from READY back to IN_PROGRESS."""
        assert validate_kds_status_transition("READY", "IN_PROGRESS") is True

    def test_invalid_transition_waiting_to_ready(self):
        """Test invalid transition from WAITING directly to READY."""
        assert validate_kds_status_transition("WAITING", "READY") is False

    def test_invalid_transition_ready_to_waiting(self):
        """Test invalid transition from READY directly to WAITING."""
        assert validate_kds_status_transition("READY", "WAITING") is False

    def test_invalid_transition_same_status(self):
        """Test that same-to-same transitions are invalid."""
        assert validate_kds_status_transition("WAITING", "WAITING") is False
        assert validate_kds_status_transition("IN_PROGRESS", "IN_PROGRESS") is False
        assert validate_kds_status_transition("READY", "READY") is False

    def test_invalid_transition_with_invalid_status(self):
        """Test transitions with invalid status values."""
        assert validate_kds_status_transition("INVALID", "WAITING") is False
        assert validate_kds_status_transition("WAITING", "INVALID") is False
        assert validate_kds_status_transition("", "WAITING") is False

    def test_initial_status_assignment(self):
        """Test that any valid status can be set as initial status (only when current is None)."""
        assert validate_kds_status_transition(None, "WAITING") is True
        assert validate_kds_status_transition(None, "IN_PROGRESS") is True
        assert validate_kds_status_transition(None, "READY") is True
        # Empty string should be treated as invalid, not as None
        assert validate_kds_status_transition("", "WAITING") is False


class TestGetAllowedTransitions:
    """Test cases for getting allowed transitions."""

    def test_allowed_transitions_from_waiting(self):
        """Test allowed transitions from WAITING status."""
        allowed = get_allowed_transitions("WAITING")
        assert len(allowed) == 1
        assert "IN_PROGRESS" in allowed

    def test_allowed_transitions_from_in_progress(self):
        """Test allowed transitions from IN_PROGRESS status."""
        allowed = get_allowed_transitions("IN_PROGRESS")
        assert len(allowed) == 2
        assert "READY" in allowed
        assert "WAITING" in allowed

    def test_allowed_transitions_from_ready(self):
        """Test allowed transitions from READY status."""
        allowed = get_allowed_transitions("READY")
        assert len(allowed) == 1
        assert "IN_PROGRESS" in allowed

    def test_allowed_transitions_from_invalid_status(self):
        """Test that invalid status returns empty list."""
        allowed = get_allowed_transitions("INVALID")
        assert len(allowed) == 0
        assert allowed == []


class TestKDSWorkflowScenarios:
    """Integration test scenarios for typical KDS workflows."""

    def test_normal_workflow(self):
        """Test a normal KDS workflow: WAITING -> IN_PROGRESS -> READY."""
        # Start with WAITING
        current_status = "WAITING"

        # Move to IN_PROGRESS
        assert validate_kds_status_transition(current_status, "IN_PROGRESS") is True
        current_status = "IN_PROGRESS"

        # Move to READY
        assert validate_kds_status_transition(current_status, "READY") is True
        current_status = "READY"

        # Should not be able to go back to WAITING directly
        assert validate_kds_status_transition(current_status, "WAITING") is False

    def test_correction_workflow(self):
        """Test workflow with corrections: WAITING -> IN_PROGRESS -> WAITING -> IN_PROGRESS -> READY."""
        # Start with WAITING
        current_status = "WAITING"

        # Move to IN_PROGRESS
        assert validate_kds_status_transition(current_status, "IN_PROGRESS") is True
        current_status = "IN_PROGRESS"

        # Realize mistake, go back to WAITING
        assert validate_kds_status_transition(current_status, "WAITING") is True
        current_status = "WAITING"

        # Start again
        assert validate_kds_status_transition(current_status, "IN_PROGRESS") is True
        current_status = "IN_PROGRESS"

        # Complete
        assert validate_kds_status_transition(current_status, "READY") is True
        current_status = "READY"

    def test_revert_from_ready_workflow(self):
        """Test workflow with reverting from READY: ... -> READY -> IN_PROGRESS -> READY."""
        # Assume we're at READY
        current_status = "READY"

        # Need to make changes, revert to IN_PROGRESS
        assert validate_kds_status_transition(current_status, "IN_PROGRESS") is True
        current_status = "IN_PROGRESS"

        # Complete again
        assert validate_kds_status_transition(current_status, "READY") is True
        current_status = "READY"

    def test_invalid_skip_workflow(self):
        """Test that skipping steps is not allowed."""
        # Cannot skip from WAITING directly to READY
        assert validate_kds_status_transition("WAITING", "READY") is False

        # Cannot skip from READY directly to WAITING
        assert validate_kds_status_transition("READY", "WAITING") is False


# Test data fixtures for API testing (to be used with TestClient)
@pytest.fixture
def sample_order_item_data():
    """Sample order item data for testing."""
    return {
        "order_id": 1,
        "product_id": 101,
        "seat_id": 1,
        "quantity": 2,
        "unit_price": 1500.00,
        "selected_modifiers": [
            {
                "group_name": "Size",
                "modifier_name": "Large",
                "price": 200.00
            }
        ],
        "course": "Main",
        "notes": "Extra spicy",
        "kds_station": "hot_kitchen",
        "kds_status": "WAITING",
        "promised_time": "2025-11-19T14:30:00"
    }


@pytest.fixture
def sample_kds_status_update():
    """Sample KDS status update request."""
    return {
        "status": "IN_PROGRESS"
    }


class TestKDSStatusUpdateRequest:
    """Test cases for KDSStatusUpdateRequest schema."""

    def test_valid_status_update_request(self, sample_kds_status_update):
        """Test that valid status update request is accepted."""
        pytest.importorskip("fastapi")  # Skip if FastAPI is not installed
        from backend.service_orders.routers.kds import KDSStatusUpdateRequest

        request = KDSStatusUpdateRequest(**sample_kds_status_update)
        assert request.status == "IN_PROGRESS"

        # Should not raise exception
        request.validate_status()

    def test_invalid_status_update_request(self):
        """Test that invalid status raises ValueError."""
        pytest.importorskip("fastapi")  # Skip if FastAPI is not installed
        from backend.service_orders.routers.kds import KDSStatusUpdateRequest

        request = KDSStatusUpdateRequest(status="INVALID_STATUS")

        with pytest.raises(ValueError) as exc_info:
            request.validate_status()

        assert "Invalid KDS status" in str(exc_info.value)
        assert "INVALID_STATUS" in str(exc_info.value)


# Note: Full API integration tests would require a test database
# and TestClient setup, which can be added in a separate test file
# if needed (e.g., test_kds_api_integration.py)
