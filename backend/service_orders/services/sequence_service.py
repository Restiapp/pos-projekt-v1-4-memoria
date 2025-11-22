"""
Sequence Generator Service
Module: Sequence Number Generation for Orders

Provides unique, sequential order numbers in the format: ORD-NNNN
where NNNN is a zero-padded 4-digit number.
"""

import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.service_orders.models.order import Order


def _generate_next_order_number(db: Session) -> str:
    """
    Generate the next unique order number in sequence.

    Format: ORD-NNNN (e.g., ORD-0001, ORD-0002, ... ORD-9999)

    Strategy:
    1. Find the highest existing order_number
    2. Increment by 1
    3. If collision occurs (rare), retry with next number

    Args:
        db: SQLAlchemy database session

    Returns:
        str: Next order number (e.g., "ORD-0042")
    """
    # Query for the highest order number
    max_order = db.query(Order.order_number).filter(
        Order.order_number.isnot(None),
        Order.order_number.like('ORD-%')
    ).order_by(Order.order_number.desc()).first()

    if max_order and max_order[0]:
        # Extract number from format "ORD-NNNN"
        try:
            current_num = int(max_order[0].split('-')[1])
            next_num = current_num + 1
        except (ValueError, IndexError):
            # If parsing fails, start from 1
            next_num = 1
    else:
        # No existing orders, start from 1
        next_num = 1

    # Generate with zero-padding (4 digits)
    # Wrap around at 10000 (though unlikely in practice)
    next_num = next_num % 10000
    order_number = f"ORD-{next_num:04d}"

    # Double-check uniqueness (collision detection)
    existing = db.query(Order).filter(Order.order_number == order_number).first()
    if existing:
        # Rare case: collision occurred, try next number
        # This recursive call will keep incrementing until unique
        return _generate_next_order_number(db)

    return order_number


def get_next_sequence_number(db: Session) -> str:
    """
    Get the next available sequence number without creating an order.

    This is used by the frontend to display the sequence number
    in the order creation modal before the order is actually submitted.

    Args:
        db: SQLAlchemy database session

    Returns:
        str: Next order number that will be assigned
    """
    return _generate_next_order_number(db)


def assign_order_number(db: Session, order: Order) -> str:
    """
    Assign a unique order number to an existing order.

    This is called during order creation to assign the sequence number.

    Args:
        db: SQLAlchemy database session
        order: Order object to assign number to

    Returns:
        str: Assigned order number
    """
    if order.order_number:
        # Already has a number, don't reassign
        return order.order_number

    order_number = _generate_next_order_number(db)
    order.order_number = order_number
    db.flush()  # Ensure it's persisted to DB

    return order_number


def validate_order_number_format(order_number: str) -> bool:
    """
    Validate that an order number matches the expected format.

    Args:
        order_number: String to validate

    Returns:
        bool: True if valid format, False otherwise
    """
    if not order_number:
        return False

    parts = order_number.split('-')
    if len(parts) != 2:
        return False

    prefix, number_str = parts
    if prefix != 'ORD':
        return False

    try:
        number = int(number_str)
        return 0 <= number < 10000 and len(number_str) == 4
    except ValueError:
        return False
