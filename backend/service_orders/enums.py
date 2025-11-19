"""
Enums for Service Orders Module
Module 1: Rendeléskezelés és Asztalok

This module defines enumerations used throughout the service orders system,
including KDS (Kitchen Display System) status values and validation logic.
"""

from enum import Enum
from typing import Dict, List


class KDSStatus(str, Enum):
    """
    Kitchen Display System status enumeration.

    Defines the lifecycle of an order item in the kitchen workflow:
    - WAITING: Item is waiting to be prepared
    - IN_PROGRESS: Item is currently being prepared
    - READY: Item is ready for serving
    """
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"

    @classmethod
    def values(cls) -> List[str]:
        """Return a list of all valid status values."""
        return [status.value for status in cls]

    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if a status value is valid."""
        return status in cls.values()


# Valid status transitions for KDS workflow
KDS_STATUS_TRANSITIONS: Dict[str, List[str]] = {
    KDSStatus.WAITING: [KDSStatus.IN_PROGRESS],
    KDSStatus.IN_PROGRESS: [KDSStatus.READY, KDSStatus.WAITING],  # Allow reverting to WAITING
    KDSStatus.READY: [KDSStatus.IN_PROGRESS],  # Allow reverting to IN_PROGRESS if needed
}


def validate_kds_status_transition(current_status: str, new_status: str) -> bool:
    """
    Validate if a KDS status transition is allowed.

    Args:
        current_status: Current KDS status
        new_status: Desired new KDS status

    Returns:
        bool: True if transition is valid, False otherwise

    Examples:
        >>> validate_kds_status_transition("WAITING", "IN_PROGRESS")
        True
        >>> validate_kds_status_transition("WAITING", "READY")
        False
    """
    # Allow setting initial status only if current_status is None (not empty string)
    if current_status is None:
        return KDSStatus.is_valid(new_status)

    # Check if both statuses are valid
    if not (KDSStatus.is_valid(current_status) and KDSStatus.is_valid(new_status)):
        return False

    # Check if transition is allowed
    allowed_transitions = KDS_STATUS_TRANSITIONS.get(current_status, [])
    return new_status in allowed_transitions


def get_allowed_transitions(current_status: str) -> List[str]:
    """
    Get list of allowed status transitions from the current status.

    Args:
        current_status: Current KDS status

    Returns:
        List[str]: List of valid next statuses

    Example:
        >>> get_allowed_transitions("WAITING")
        ["IN_PROGRESS"]
    """
    if not KDSStatus.is_valid(current_status):
        return []

    return KDS_STATUS_TRANSITIONS.get(current_status, [])
