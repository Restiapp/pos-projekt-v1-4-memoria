"""
Courier Service - Business Logic Layer
V3.0 Module: Logistics Service - Phase 2.A

This module handles business logic for couriers.
CRUD operations and validation logic for couriers.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.service_logistics.models.courier import Courier, CourierStatus
from backend.service_logistics.schemas.courier import (
    CourierCreate,
    CourierUpdate,
)


class CourierService:
    """
    Service class for managing couriers.

    Supported operations:
    - Create new courier
    - Get courier by ID
    - Get courier by phone
    - List all couriers (with pagination and filtering)
    - Update courier
    - Delete courier
    - Update courier status
    """

    @staticmethod
    def create_courier(db: Session, courier_data: CourierCreate) -> Courier:
        """
        Create a new courier in the database.

        Args:
            db: SQLAlchemy session
            courier_data: CourierCreate schema with courier data

        Returns:
            Courier: The created courier object

        Raises:
            ValueError: If the phone or email already exists
        """
        db_courier = Courier(
            courier_name=courier_data.courier_name,
            phone=courier_data.phone,
            email=courier_data.email,
            status=courier_data.status,
            is_active=courier_data.is_active,
        )

        db.add(db_courier)
        try:
            db.commit()
            db.refresh(db_courier)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Courier with phone '{courier_data.phone}' or email '{courier_data.email}' already exists."
            ) from e

        return db_courier

    @staticmethod
    def get_courier(db: Session, courier_id: int) -> Optional[Courier]:
        """
        Get courier by ID.

        Args:
            db: SQLAlchemy session
            courier_id: The courier's unique identifier

        Returns:
            Courier | None: The courier object or None if not found
        """
        return db.query(Courier).filter(Courier.id == courier_id).first()

    @staticmethod
    def get_courier_by_phone(db: Session, phone: str) -> Optional[Courier]:
        """
        Get courier by phone number.

        Args:
            db: SQLAlchemy session
            phone: The courier's phone number

        Returns:
            Courier | None: The courier object or None if not found
        """
        return db.query(Courier).filter(Courier.phone == phone).first()

    @staticmethod
    def list_couriers(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CourierStatus] = None,
        active_only: bool = False
    ) -> tuple[List[Courier], int]:
        """
        List all couriers with pagination and filtering support.

        Args:
            db: SQLAlchemy session
            skip: How many records to skip (offset)
            limit: Maximum number of records to return (page size)
            status: Filter by courier status (optional)
            active_only: If True, only return active couriers

        Returns:
            tuple: (list of couriers, total count)
        """
        query = db.query(Courier)

        # Apply filters
        if status:
            query = query.filter(Courier.status == status)

        if active_only:
            query = query.filter(Courier.is_active == True)

        # Get total count
        total = query.count()

        # Get paginated list
        couriers = query.offset(skip).limit(limit).all()

        return couriers, total

    @staticmethod
    def update_courier(
        db: Session,
        courier_id: int,
        courier_data: CourierUpdate
    ) -> Optional[Courier]:
        """
        Update existing courier data.

        Args:
            db: SQLAlchemy session
            courier_id: The courier's unique identifier
            courier_data: CourierUpdate schema with fields to update

        Returns:
            Courier | None: The updated courier object or None if not found

        Raises:
            ValueError: If the phone or email update causes a conflict
        """
        db_courier = db.query(Courier).filter(Courier.id == courier_id).first()

        if not db_courier:
            return None

        # Only update fields that are not None
        update_data = courier_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_courier, field, value)

        try:
            db.commit()
            db.refresh(db_courier)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Failed to update courier. Possible cause: "
                f"phone '{courier_data.phone}' or email '{courier_data.email}' is already in use."
            ) from e

        return db_courier

    @staticmethod
    def delete_courier(db: Session, courier_id: int) -> bool:
        """
        Delete courier from database.

        Args:
            db: SQLAlchemy session
            courier_id: The courier's unique identifier to delete

        Returns:
            bool: True if deletion was successful, False if courier not found
        """
        db_courier = db.query(Courier).filter(Courier.id == courier_id).first()

        if not db_courier:
            return False

        db.delete(db_courier)
        db.commit()

        return True

    @staticmethod
    def update_courier_status(
        db: Session,
        courier_id: int,
        new_status: CourierStatus
    ) -> Optional[Courier]:
        """
        Update courier status.

        Args:
            db: SQLAlchemy session
            courier_id: The courier's unique identifier
            new_status: The new status to set

        Returns:
            Courier | None: The updated courier object or None if not found
        """
        db_courier = db.query(Courier).filter(Courier.id == courier_id).first()

        if not db_courier:
            return None

        db_courier.status = new_status
        db.commit()
        db.refresh(db_courier)

        return db_courier

    @staticmethod
    def count_couriers(
        db: Session,
        status: Optional[CourierStatus] = None,
        active_only: bool = False
    ) -> int:
        """
        Get total count of couriers.

        Args:
            db: SQLAlchemy session
            status: Filter by courier status (optional)
            active_only: If True, only count active couriers

        Returns:
            int: The number of couriers
        """
        query = db.query(Courier)

        if status:
            query = query.filter(Courier.status == status)

        if active_only:
            query = query.filter(Courier.is_active == True)

        return query.count()

    @staticmethod
    def get_available_couriers(db: Session) -> List[Courier]:
        """
        Get all available couriers (status=AVAILABLE and is_active=True).

        Args:
            db: SQLAlchemy session

        Returns:
            List[Courier]: List of available couriers
        """
        return db.query(Courier).filter(
            Courier.status == CourierStatus.AVAILABLE,
            Courier.is_active == True
        ).all()

    @staticmethod
    def assign_order(
        db: Session,
        courier_id: int,
        order_id: int
    ) -> Optional[Courier]:
        """
        Assign an order to a courier.

        This method:
        - Updates courier status to ON_DELIVERY
        - Stores the order assignment (for now just changes status)
        - In future phases, will integrate with service_orders

        Args:
            db: SQLAlchemy session
            courier_id: The courier's unique identifier
            order_id: The order ID to assign

        Returns:
            Courier | None: The updated courier object or None if not found

        Raises:
            ValueError: If courier is not available for delivery
        """
        db_courier = db.query(Courier).filter(Courier.id == courier_id).first()

        if not db_courier:
            return None

        # Validate courier can accept order
        if not db_courier.is_active:
            raise ValueError(f"Courier (ID: {courier_id}) is not active")

        # Update status to ON_DELIVERY
        db_courier.status = CourierStatus.ON_DELIVERY

        db.commit()
        db.refresh(db_courier)

        return db_courier


# Singleton instance for export
courier_service = CourierService()
