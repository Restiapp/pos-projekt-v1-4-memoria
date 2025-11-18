"""
Coupon Service - Business Logic Layer
Module 5: Customer Relationship Management (CRM)

Ez a service layer felelős a kuponok üzleti logikájáért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- Kupon validáció (érvényesség, használati limit, minimum rendelési érték)
- Kedvezmény számítás
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
import logging

from backend.service_crm.models.coupon import Coupon
from backend.service_crm.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
    CouponValidationRequest,
    DiscountTypeEnum
)

logger = logging.getLogger(__name__)


class CouponService:
    """
    Service osztály a kuponok kezeléséhez.

    Felelősségek:
    - Kuponok létrehozása, lekérdezése, módosítása, törlése
    - Kupon érvényesség validálása
    - Kedvezmény összegének számítása
    - Használati statisztikák kezelése
    """

    @staticmethod
    def create_coupon(db: Session, coupon_data: CouponCreate) -> Coupon:
        """
        Új kupon létrehozása.

        Args:
            db: SQLAlchemy session
            coupon_data: CouponCreate schema a bemeneti adatokkal

        Returns:
            Coupon: Az újonnan létrehozott kupon

        Raises:
            HTTPException 400: Ha a kupon kód már létezik vagy az adatok érvénytelenek

        Example:
            >>> coupon_data = CouponCreate(
            ...     code="WELCOME10",
            ...     discount_type="PERCENTAGE",
            ...     discount_value=Decimal("10.00"),
            ...     valid_from=datetime.now()
            ... )
            >>> new_coupon = CouponService.create_coupon(db, coupon_data)
        """
        # Ellenőrizzük, hogy a kupon kód már létezik-e
        existing_coupon = db.query(Coupon).filter(
            Coupon.code == coupon_data.code
        ).first()

        if existing_coupon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ez a kupon kód már létezik: {coupon_data.code}"
            )

        try:
            # Új Coupon objektum létrehozása
            db_coupon = Coupon(
                code=coupon_data.code,
                description=coupon_data.description,
                discount_type=coupon_data.discount_type.value,
                discount_value=coupon_data.discount_value,
                min_purchase_amount=coupon_data.min_purchase_amount,
                usage_limit=coupon_data.usage_limit,
                valid_from=coupon_data.valid_from,
                valid_until=coupon_data.valid_until,
                is_active=coupon_data.is_active,
                customer_id=coupon_data.customer_id
            )

            db.add(db_coupon)
            db.commit()
            db.refresh(db_coupon)

            logger.info(f"Coupon created: {db_coupon.id} - {db_coupon.code}")
            return db_coupon

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating coupon: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a kupon létrehozása során: {str(e)}"
            )

    @staticmethod
    def get_coupon(db: Session, coupon_id: int) -> Coupon:
        """
        Egy kupon lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            coupon_id: A kupon azonosítója

        Returns:
            Coupon: A lekérdezett kupon

        Raises:
            HTTPException 404: Ha a kupon nem található

        Example:
            >>> coupon = CouponService.get_coupon(db, coupon_id=42)
        """
        coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()

        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kupon nem található: ID={coupon_id}"
            )

        return coupon

    @staticmethod
    def get_coupon_by_code(db: Session, code: str) -> Optional[Coupon]:
        """
        Kupon keresése kód alapján.

        Args:
            db: SQLAlchemy session
            code: Kupon kód

        Returns:
            Optional[Coupon]: A kupon vagy None

        Example:
            >>> coupon = CouponService.get_coupon_by_code(db, "WELCOME10")
        """
        return db.query(Coupon).filter(Coupon.code == code).first()

    @staticmethod
    def get_coupons(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        customer_id: Optional[int] = None,
        discount_type: Optional[str] = None
    ) -> List[Coupon]:
        """
        Kuponok listájának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            skip: Kihagyandó elemek száma (pagination)
            limit: Maximum visszaadott elemek száma
            is_active: Szűrés aktív/inaktív kuponokra
            customer_id: Szűrés ügyfél-specifikus kuponokra (None = publikus)
            discount_type: Szűrés kedvezmény típusra

        Returns:
            List[Coupon]: Kuponok listája

        Example:
            >>> coupons = CouponService.get_coupons(
            ...     db,
            ...     skip=0,
            ...     limit=20,
            ...     is_active=True
            ... )
        """
        query = db.query(Coupon)

        # Szűrők alkalmazása
        if is_active is not None:
            query = query.filter(Coupon.is_active == is_active)

        if customer_id is not None:
            query = query.filter(Coupon.customer_id == customer_id)

        if discount_type:
            query = query.filter(Coupon.discount_type == discount_type)

        # Rendezés: legutóbb létrehozott először
        query = query.order_by(desc(Coupon.created_at))

        # Pagination
        coupons = query.offset(skip).limit(limit).all()

        return coupons

    @staticmethod
    def update_coupon(
        db: Session,
        coupon_id: int,
        coupon_data: CouponUpdate
    ) -> Coupon:
        """
        Kupon adatainak módosítása.

        Args:
            db: SQLAlchemy session
            coupon_id: A módosítandó kupon azonosítója
            coupon_data: CouponUpdate schema a módosítandó mezőkkel

        Returns:
            Coupon: A módosított kupon

        Raises:
            HTTPException 404: Ha a kupon nem található
            HTTPException 400: Ha a módosítás sikertelen

        Example:
            >>> update_data = CouponUpdate(is_active=False)
            >>> updated_coupon = CouponService.update_coupon(db, coupon_id=42, coupon_data=update_data)
        """
        coupon = CouponService.get_coupon(db, coupon_id)

        try:
            # Csak a megadott mezők frissítése (exclude_unset=True)
            update_dict = coupon_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                # Enum értékek kezelése
                if hasattr(value, 'value'):
                    setattr(coupon, field, value.value)
                else:
                    setattr(coupon, field, value)

            db.commit()
            db.refresh(coupon)

            logger.info(f"Coupon updated: {coupon.id}")
            return coupon

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating coupon {coupon_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a kupon módosítása során: {str(e)}"
            )

    @staticmethod
    def delete_coupon(db: Session, coupon_id: int) -> Dict[str, Any]:
        """
        Kupon törlése.

        Args:
            db: SQLAlchemy session
            coupon_id: A törlendő kupon azonosítója

        Returns:
            Dict: Megerősítő üzenet

        Raises:
            HTTPException 404: Ha a kupon nem található

        Example:
            >>> result = CouponService.delete_coupon(db, coupon_id=42)
        """
        coupon = CouponService.get_coupon(db, coupon_id)

        try:
            db.delete(coupon)
            db.commit()

            logger.info(f"Coupon deleted: {coupon_id}")
            return {
                "message": "Kupon sikeresen törölve",
                "coupon_id": coupon_id
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting coupon {coupon_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a kupon törlése során: {str(e)}"
            )

    @staticmethod
    def count_coupons(
        db: Session,
        is_active: Optional[bool] = None,
        customer_id: Optional[int] = None,
        discount_type: Optional[str] = None
    ) -> int:
        """
        Kuponok számának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            is_active: Szűrés aktív/inaktív kuponokra
            customer_id: Szűrés ügyfél-specifikus kuponokra
            discount_type: Szűrés kedvezmény típusra

        Returns:
            int: Kuponok száma

        Example:
            >>> count = CouponService.count_coupons(db, is_active=True)
        """
        query = db.query(Coupon)

        if is_active is not None:
            query = query.filter(Coupon.is_active == is_active)

        if customer_id is not None:
            query = query.filter(Coupon.customer_id == customer_id)

        if discount_type:
            query = query.filter(Coupon.discount_type == discount_type)

        return query.count()

    @staticmethod
    def validate_coupon(
        db: Session,
        validation_request: CouponValidationRequest
    ) -> Dict[str, Any]:
        """
        Kupon validálása és kedvezmény számítása.

        Args:
            db: SQLAlchemy session
            validation_request: CouponValidationRequest schema

        Returns:
            Dict: Validációs eredmény és kedvezmény összege

        Raises:
            HTTPException 404: Ha a kupon nem található

        Example:
            >>> request = CouponValidationRequest(
            ...     code="WELCOME10",
            ...     order_amount=Decimal("5000.00")
            ... )
            >>> result = CouponService.validate_coupon(db, request)
        """
        coupon = CouponService.get_coupon_by_code(db, validation_request.code)

        if not coupon:
            return {
                "valid": False,
                "message": "Érvénytelen kupon kód",
                "discount_amount": None,
                "coupon": None
            }

        # Ellenőrzések
        now = datetime.now()

        # 1. Aktív-e a kupon?
        if not coupon.is_active:
            return {
                "valid": False,
                "message": "Ez a kupon már nem aktív",
                "discount_amount": None,
                "coupon": None
            }

        # 2. Érvényességi időszak ellenőrzése
        if coupon.valid_from and coupon.valid_from > now:
            return {
                "valid": False,
                "message": f"Ez a kupon csak {coupon.valid_from} után érvényes",
                "discount_amount": None,
                "coupon": None
            }

        if coupon.valid_until and coupon.valid_until < now:
            return {
                "valid": False,
                "message": "Ez a kupon már lejárt",
                "discount_amount": None,
                "coupon": None
            }

        # 3. Használati limit ellenőrzése
        if coupon.usage_limit is not None and coupon.usage_count >= coupon.usage_limit:
            return {
                "valid": False,
                "message": "Ez a kupon elérte a maximális használati limitet",
                "discount_amount": None,
                "coupon": None
            }

        # 4. Minimum rendelési érték ellenőrzése
        if coupon.min_purchase_amount and validation_request.order_amount < coupon.min_purchase_amount:
            return {
                "valid": False,
                "message": f"Minimum rendelési érték: {coupon.min_purchase_amount} HUF",
                "discount_amount": None,
                "coupon": None
            }

        # 5. Ügyfél-specifikus kupon ellenőrzése
        if coupon.customer_id is not None:
            if validation_request.customer_id is None:
                return {
                    "valid": False,
                    "message": "Ez a kupon csak bejelentkezett ügyfelek számára érvényes",
                    "discount_amount": None,
                    "coupon": None
                }
            if coupon.customer_id != validation_request.customer_id:
                return {
                    "valid": False,
                    "message": "Ez a kupon nem érvényes az Ön fiókjához",
                    "discount_amount": None,
                    "coupon": None
                }

        # Kedvezmény számítása
        discount_amount = CouponService.calculate_discount(
            coupon,
            validation_request.order_amount
        )

        return {
            "valid": True,
            "message": "A kupon érvényes",
            "discount_amount": discount_amount,
            "coupon": coupon
        }

    @staticmethod
    def calculate_discount(coupon: Coupon, order_amount: Decimal) -> Decimal:
        """
        Kedvezmény összegének kiszámítása.

        Args:
            coupon: Coupon objektum
            order_amount: Rendelés összege (HUF)

        Returns:
            Decimal: Kedvezmény összege HUF-ban

        Example:
            >>> discount = CouponService.calculate_discount(coupon, Decimal("5000.00"))
        """
        if coupon.discount_type == DiscountTypeEnum.PERCENTAGE.value:
            # Százalékos kedvezmény
            discount = order_amount * (coupon.discount_value / Decimal("100"))
        else:
            # Fix összegű kedvezmény
            discount = coupon.discount_value

        # Ne legyen nagyobb a kedvezmény, mint a rendelés összege
        return min(discount, order_amount)

    @staticmethod
    def increment_usage(db: Session, coupon_id: int) -> Coupon:
        """
        Kupon használati számláló növelése.

        Args:
            db: SQLAlchemy session
            coupon_id: A kupon azonosítója

        Returns:
            Coupon: A frissített kupon

        Raises:
            HTTPException 404: Ha a kupon nem található

        Example:
            >>> coupon = CouponService.increment_usage(db, coupon_id=42)
        """
        coupon = CouponService.get_coupon(db, coupon_id)

        try:
            coupon.usage_count += 1
            db.commit()
            db.refresh(coupon)

            logger.info(f"Coupon usage incremented: {coupon_id} (count: {coupon.usage_count})")
            return coupon

        except Exception as e:
            db.rollback()
            logger.error(f"Error incrementing coupon usage {coupon_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a kupon használat növelése során: {str(e)}"
            )
