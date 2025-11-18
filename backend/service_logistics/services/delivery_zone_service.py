"""
DeliveryZone Service - Business Logic Layer
V3.0 Module: Logistics Service - Phase 2.A

This module handles business logic for delivery zones.
CRUD operations and validation logic for delivery zones.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.service_logistics.models.delivery_zone import DeliveryZone
from backend.service_logistics.schemas.delivery_zone import (
    DeliveryZoneCreate,
    DeliveryZoneUpdate,
)


class DeliveryZoneService:
    """
    Service class for managing delivery zones.

    Supported operations:
    - Create new delivery zone
    - Get delivery zone by ID
    - Get delivery zone by zone name
    - List all delivery zones (with pagination)
    - Update delivery zone
    - Delete delivery zone
    """

    @staticmethod
    def create_delivery_zone(db: Session, zone_data: DeliveryZoneCreate) -> DeliveryZone:
        """
        Create a new delivery zone in the database.

        Args:
            db: SQLAlchemy session
            zone_data: DeliveryZoneCreate schema with zone data

        Returns:
            DeliveryZone: The created delivery zone object

        Raises:
            ValueError: If the zone_name already exists
        """
        db_zone = DeliveryZone(
            zone_name=zone_data.zone_name,
            description=zone_data.description,
            delivery_fee=zone_data.delivery_fee,
            min_order_value=zone_data.min_order_value,
            estimated_delivery_time_minutes=zone_data.estimated_delivery_time_minutes,
            is_active=zone_data.is_active,
        )

        db.add(db_zone)
        try:
            db.commit()
            db.refresh(db_zone)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Delivery zone '{zone_data.zone_name}' already exists in the database."
            ) from e

        return db_zone

    @staticmethod
    def get_delivery_zone(db: Session, zone_id: int) -> Optional[DeliveryZone]:
        """
        Get delivery zone by ID.

        Args:
            db: SQLAlchemy session
            zone_id: The delivery zone's unique identifier

        Returns:
            DeliveryZone | None: The delivery zone object or None if not found
        """
        return db.query(DeliveryZone).filter(DeliveryZone.id == zone_id).first()

    @staticmethod
    def get_delivery_zone_by_name(db: Session, zone_name: str) -> Optional[DeliveryZone]:
        """
        Get delivery zone by zone name.

        Args:
            db: SQLAlchemy session
            zone_name: The delivery zone's name/identifier

        Returns:
            DeliveryZone | None: The delivery zone object or None if not found
        """
        return db.query(DeliveryZone).filter(DeliveryZone.zone_name == zone_name).first()

    @staticmethod
    def list_delivery_zones(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> tuple[List[DeliveryZone], int]:
        """
        List all delivery zones with pagination support.

        Args:
            db: SQLAlchemy session
            skip: How many records to skip (offset)
            limit: Maximum number of records to return (page size)
            active_only: If True, only return active zones

        Returns:
            tuple: (list of zones, total count)
        """
        query = db.query(DeliveryZone)

        if active_only:
            query = query.filter(DeliveryZone.is_active == True)

        # Get total count
        total = query.count()

        # Get paginated list
        zones = query.offset(skip).limit(limit).all()

        return zones, total

    @staticmethod
    def update_delivery_zone(
        db: Session,
        zone_id: int,
        zone_data: DeliveryZoneUpdate
    ) -> Optional[DeliveryZone]:
        """
        Update existing delivery zone data.

        Args:
            db: SQLAlchemy session
            zone_id: The delivery zone's unique identifier
            zone_data: DeliveryZoneUpdate schema with fields to update

        Returns:
            DeliveryZone | None: The updated delivery zone object or None if not found

        Raises:
            ValueError: If the zone_name update causes a conflict
        """
        db_zone = db.query(DeliveryZone).filter(DeliveryZone.id == zone_id).first()

        if not db_zone:
            return None

        # Only update fields that are not None
        update_data = zone_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_zone, field, value)

        try:
            db.commit()
            db.refresh(db_zone)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Failed to update delivery zone. Possible cause: "
                f"zone_name '{zone_data.zone_name}' is already in use."
            ) from e

        return db_zone

    @staticmethod
    def delete_delivery_zone(db: Session, zone_id: int) -> bool:
        """
        Delete delivery zone from database.

        Args:
            db: SQLAlchemy session
            zone_id: The delivery zone's unique identifier to delete

        Returns:
            bool: True if deletion was successful, False if zone not found
        """
        db_zone = db.query(DeliveryZone).filter(DeliveryZone.id == zone_id).first()

        if not db_zone:
            return False

        db.delete(db_zone)
        db.commit()

        return True

    @staticmethod
    def count_delivery_zones(db: Session, active_only: bool = False) -> int:
        """
        Get total count of delivery zones.

        Args:
            db: SQLAlchemy session
            active_only: If True, only count active zones

        Returns:
            int: The number of delivery zones
        """
        query = db.query(DeliveryZone)

        if active_only:
            query = query.filter(DeliveryZone.is_active == True)

        return query.count()

    @staticmethod
    def get_active_zones(db: Session) -> List[DeliveryZone]:
        """
        Get all active delivery zones.

        Args:
            db: SQLAlchemy session

        Returns:
            List[DeliveryZone]: List of active delivery zones
        """
        return db.query(DeliveryZone).filter(
            DeliveryZone.is_active == True
        ).all()


# Singleton instance for export
delivery_zone_service = DeliveryZoneService()
