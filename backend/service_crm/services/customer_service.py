"""
Customer Service - Business Logic Layer
Module 5: Customer Relationship Management (CRM)

Ez a service layer felelős az ügyfelek üzleti logikájáért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- Törzsvásárlói pontok kezelése
- Vásárlási statisztikák frissítése
"""

from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from fastapi import HTTPException, status
import logging

from backend.service_crm.models.customer import Customer
from backend.service_crm.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    LoyaltyPointsUpdate
)

logger = logging.getLogger(__name__)


class CustomerService:
    """
    Service osztály az ügyfelek kezeléséhez.

    Felelősségek:
    - Ügyfelek létrehozása, lekérdezése, módosítása, törlése
    - Törzsvásárlói pontok kezelése
    - Email egyediség validáció
    """

    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate) -> Customer:
        """
        Új ügyfél létrehozása.

        Args:
            db: SQLAlchemy session
            customer_data: CustomerCreate schema a bemeneti adatokkal

        Returns:
            Customer: Az újonnan létrehozott ügyfél

        Raises:
            HTTPException 400: Ha az email már létezik vagy az adatok érvénytelenek

        Example:
            >>> customer_data = CustomerCreate(
            ...     first_name="János",
            ...     last_name="Nagy",
            ...     email="janos.nagy@example.com",
            ...     phone="+36301234567"
            ... )
            >>> new_customer = CustomerService.create_customer(db, customer_data)
        """
        # Ellenőrizzük, hogy az email már létezik-e
        existing_customer = db.query(Customer).filter(
            Customer.email == customer_data.email
        ).first()

        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ez az email cím már használatban van: {customer_data.email}"
            )

        try:
            # Új Customer objektum létrehozása
            db_customer = Customer(
                first_name=customer_data.first_name,
                last_name=customer_data.last_name,
                email=customer_data.email,
                phone=customer_data.phone,
                marketing_consent=customer_data.marketing_consent,
                sms_consent=customer_data.sms_consent,
                birth_date=customer_data.birth_date,
                notes=customer_data.notes
            )

            db.add(db_customer)
            db.commit()
            db.refresh(db_customer)

            logger.info(f"Customer created: {db_customer.id} - {db_customer.email}")
            return db_customer

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating customer: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az ügyfél létrehozása során: {str(e)}"
            )

    @staticmethod
    def get_customer(db: Session, customer_id: int) -> Customer:
        """
        Egy ügyfél lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            customer_id: Az ügyfél azonosítója

        Returns:
            Customer: A lekérdezett ügyfél

        Raises:
            HTTPException 404: Ha az ügyfél nem található

        Example:
            >>> customer = CustomerService.get_customer(db, customer_id=42)
        """
        customer = db.query(Customer).filter(Customer.id == customer_id).first()

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ügyfél nem található: ID={customer_id}"
            )

        return customer

    @staticmethod
    def get_customer_by_email(db: Session, email: str) -> Optional[Customer]:
        """
        Ügyfél keresése email cím alapján.

        Args:
            db: SQLAlchemy session
            email: Ügyfél email címe

        Returns:
            Optional[Customer]: Az ügyfél vagy None

        Example:
            >>> customer = CustomerService.get_customer_by_email(db, "janos.nagy@example.com")
        """
        return db.query(Customer).filter(Customer.email == email).first()

    @staticmethod
    def get_customers(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Customer]:
        """
        Ügyfelek listájának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            skip: Kihagyandó elemek száma (pagination)
            limit: Maximum visszaadott elemek száma
            search: Keresési kifejezés (név vagy email alapján)
            is_active: Szűrés aktív/inaktív ügyfelekre

        Returns:
            List[Customer]: Ügyfelek listája

        Example:
            >>> customers = CustomerService.get_customers(
            ...     db,
            ...     skip=0,
            ...     limit=20,
            ...     search="nagy",
            ...     is_active=True
            ... )
        """
        query = db.query(Customer)

        # Keresés név vagy email alapján
        if search:
            search_filter = or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Aktív/inaktív szűrés
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)

        # Rendezés: legutóbb létrehozott először
        query = query.order_by(desc(Customer.created_at))

        # Pagination
        customers = query.offset(skip).limit(limit).all()

        return customers

    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        customer_data: CustomerUpdate
    ) -> Customer:
        """
        Ügyfél adatainak módosítása.

        Args:
            db: SQLAlchemy session
            customer_id: A módosítandó ügyfél azonosítója
            customer_data: CustomerUpdate schema a módosítandó mezőkkel

        Returns:
            Customer: A módosított ügyfél

        Raises:
            HTTPException 404: Ha az ügyfél nem található
            HTTPException 400: Ha az email már használatban van vagy a módosítás sikertelen

        Example:
            >>> update_data = CustomerUpdate(phone="+36301111111")
            >>> updated_customer = CustomerService.update_customer(db, customer_id=42, customer_data=update_data)
        """
        # Ügyfél lekérdezése
        customer = CustomerService.get_customer(db, customer_id)

        try:
            # Email egyediség ellenőrzése, ha az email változik
            if customer_data.email and customer_data.email != customer.email:
                existing_customer = db.query(Customer).filter(
                    Customer.email == customer_data.email,
                    Customer.id != customer_id
                ).first()

                if existing_customer:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ez az email cím már használatban van: {customer_data.email}"
                    )

            # Csak a megadott mezők frissítése (exclude_unset=True)
            update_dict = customer_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                setattr(customer, field, value)

            db.commit()
            db.refresh(customer)

            logger.info(f"Customer updated: {customer.id}")
            return customer

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating customer {customer_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az ügyfél módosítása során: {str(e)}"
            )

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> Dict[str, Any]:
        """
        Ügyfél törlése (soft delete - is_active = False).

        Args:
            db: SQLAlchemy session
            customer_id: A törlendő ügyfél azonosítója

        Returns:
            Dict: Megerősítő üzenet

        Raises:
            HTTPException 404: Ha az ügyfél nem található

        Example:
            >>> result = CustomerService.delete_customer(db, customer_id=42)
        """
        customer = CustomerService.get_customer(db, customer_id)

        try:
            # Soft delete: is_active = False
            customer.is_active = False
            db.commit()

            logger.info(f"Customer deactivated: {customer_id}")
            return {
                "message": "Ügyfél sikeresen inaktiválva",
                "customer_id": customer_id
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting customer {customer_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az ügyfél törlése során: {str(e)}"
            )

    @staticmethod
    def count_customers(
        db: Session,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """
        Ügyfelek számának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            search: Keresési kifejezés
            is_active: Szűrés aktív/inaktív ügyfelekre

        Returns:
            int: Ügyfelek száma

        Example:
            >>> count = CustomerService.count_customers(db, is_active=True)
        """
        query = db.query(Customer)

        if search:
            search_filter = or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)

        return query.count()

    @staticmethod
    def update_loyalty_points(
        db: Session,
        customer_id: int,
        points_data: LoyaltyPointsUpdate
    ) -> Customer:
        """
        Ügyfél törzsvásárlói pontjainak módosítása.

        Args:
            db: SQLAlchemy session
            customer_id: Az ügyfél azonosítója
            points_data: LoyaltyPointsUpdate schema a pontokkal

        Returns:
            Customer: A módosított ügyfél

        Raises:
            HTTPException 404: Ha az ügyfél nem található
            HTTPException 400: Ha a pont egyenleg negatívba menne

        Example:
            >>> points = LoyaltyPointsUpdate(points=10.00, reason="Birthday bonus")
            >>> customer = CustomerService.update_loyalty_points(db, customer_id=42, points_data=points)
        """
        customer = CustomerService.get_customer(db, customer_id)

        try:
            new_balance = customer.loyalty_points + points_data.points

            if new_balance < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Nincs elegendő pont. Jelenlegi egyenleg: {customer.loyalty_points}, "
                           f"Levonás: {abs(points_data.points)}"
                )

            customer.loyalty_points = new_balance
            db.commit()
            db.refresh(customer)

            logger.info(f"Loyalty points updated for customer {customer_id}: {points_data.points} ({points_data.reason})")
            return customer

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating loyalty points for customer {customer_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a pontok módosítása során: {str(e)}"
            )

    @staticmethod
    def update_purchase_stats(
        db: Session,
        customer_id: int,
        order_amount: Decimal,
        loyalty_points_ratio: float = 0.01
    ) -> Customer:
        """
        Ügyfél vásárlási statisztikáinak frissítése rendelés után.

        Args:
            db: SQLAlchemy session
            customer_id: Az ügyfél azonosítója
            order_amount: A rendelés összege (HUF)
            loyalty_points_ratio: Pontarány (alapértelmezett: 0.01 = 1%)

        Returns:
            Customer: A frissített ügyfél

        Raises:
            HTTPException 404: Ha az ügyfél nem található

        Example:
            >>> customer = CustomerService.update_purchase_stats(db, customer_id=42, order_amount=Decimal("5000.00"))
        """
        customer = CustomerService.get_customer(db, customer_id)

        try:
            # Vásárlási statisztikák frissítése
            customer.total_spent += order_amount
            customer.total_orders += 1

            # Törzsvásárlói pontok hozzáadása
            earned_points = order_amount * Decimal(str(loyalty_points_ratio))
            customer.loyalty_points += earned_points

            db.commit()
            db.refresh(customer)

            logger.info(f"Purchase stats updated for customer {customer_id}: +{order_amount} HUF, +{earned_points} points")
            return customer

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating purchase stats for customer {customer_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a vásárlási statisztikák frissítése során: {str(e)}"
            )
