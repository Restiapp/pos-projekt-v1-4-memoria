"""
Discount Service - Business Logic Layer
Module 1: Rendeléskezelés - Kedvezmények

Ez a service layer felelős a kedvezmények üzleti logikájáért, beleértve:
- Kedvezmény számítások (százalékos és fix összegű)
- Rendelés-szintű kedvezmények alkalmazása
- Tétel-szintű kedvezmények alkalmazása
- Végösszeg újraszámítása kedvezmények után

V3.0 Feature: Task A4 - Discount Model
"""

from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from backend.service_orders.models.order import Order
from backend.service_orders.models.order_item import OrderItem
from backend.service_orders.schemas.discount import (
    DiscountTypeEnum,
    DiscountDetails,
    ApplyOrderDiscountRequest,
    ApplyItemDiscountRequest,
    DiscountCalculationResult,
    OrderDiscountResponse,
    ItemDiscountResponse,
)

logger = logging.getLogger(__name__)


class DiscountService:
    """
    Service osztály a kedvezmények kezeléséhez.

    Felelősségek:
    - Kedvezmények számítása és validálása
    - Rendelés-szintű kedvezmények alkalmazása
    - Tétel-szintű kedvezmények alkalmazása
    - Végösszegek újraszámítása
    """

    @staticmethod
    def calculate_discount_amount(
        original_amount: Decimal,
        discount_type: DiscountTypeEnum,
        discount_value: Decimal
    ) -> Decimal:
        """
        Számítja a kedvezmény összegét az eredeti összeg alapján.

        Args:
            original_amount: Eredeti összeg
            discount_type: Kedvezmény típusa (percentage vagy fixed)
            discount_value: Kedvezmény értéke

        Returns:
            Decimal: Kedvezmény összege

        Raises:
            ValueError: Ha az eredmény negatív vagy érvénytelen

        Example:
            >>> # 10% kedvezmény 1000 Ft-ról
            >>> DiscountService.calculate_discount_amount(
            ...     Decimal("1000"), DiscountTypeEnum.PERCENTAGE, Decimal("10")
            ... )
            Decimal("100.00")

            >>> # 500 Ft fix kedvezmény
            >>> DiscountService.calculate_discount_amount(
            ...     Decimal("1000"), DiscountTypeEnum.FIXED, Decimal("500")
            ... )
            Decimal("500.00")
        """
        if original_amount < 0:
            raise ValueError("Az eredeti összeg nem lehet negatív")

        if discount_type == DiscountTypeEnum.PERCENTAGE:
            # Százalékos kedvezmény: amount * (value / 100)
            discount_amount = original_amount * (discount_value / Decimal("100"))
        elif discount_type == DiscountTypeEnum.FIXED:
            # Fix összegű kedvezmény
            discount_amount = discount_value
        else:
            raise ValueError(f"Ismeretlen kedvezmény típus: {discount_type}")

        # Biztosítjuk, hogy a kedvezmény nem lehet nagyobb az eredeti összegnél
        if discount_amount > original_amount:
            logger.warning(
                f"Kedvezmény ({discount_amount}) nagyobb mint az eredeti összeg ({original_amount}). "
                f"Kedvezmény limitálva az eredeti összegre."
            )
            discount_amount = original_amount

        # Kerekítés 2 tizedesjegyre
        return round(discount_amount, 2)

    @staticmethod
    def calculate_final_amount(
        original_amount: Decimal,
        discount_amount: Decimal
    ) -> Decimal:
        """
        Számítja a végső összeget kedvezmény után.

        Args:
            original_amount: Eredeti összeg
            discount_amount: Kedvezmény összege

        Returns:
            Decimal: Végső összeg kedvezmény után (minimum 0)
        """
        final_amount = original_amount - discount_amount

        # Biztosítjuk, hogy a végösszeg nem lehet negatív
        if final_amount < 0:
            final_amount = Decimal("0.00")

        return round(final_amount, 2)

    @staticmethod
    def recalculate_order_total(db: Session, order: Order) -> Decimal:
        """
        Újraszámolja a rendelés végösszegét az összes tételből,
        figyelembe véve a tétel-szintű kedvezményeket.

        Args:
            db: SQLAlchemy session
            order: A rendelés objektum

        Returns:
            Decimal: Az újraszámított végösszeg

        Example:
            >>> total = DiscountService.recalculate_order_total(db, order)
        """
        total = Decimal("0.00")

        for item in order.order_items:
            # Alap összeg: unit_price * quantity
            item_subtotal = item.unit_price * item.quantity

            # Ha van tétel-szintű kedvezmény, alkalmazzuk
            if item.discount_details:
                discount_data = item.discount_details
                discount_amount = DiscountService.calculate_discount_amount(
                    item_subtotal,
                    DiscountTypeEnum(discount_data.get("type")),
                    Decimal(str(discount_data.get("value", 0)))
                )
                item_subtotal = DiscountService.calculate_final_amount(
                    item_subtotal, discount_amount
                )

            total += item_subtotal

        # Ha van rendelés-szintű kedvezmény, alkalmazzuk a teljes összegre
        if order.discount_details:
            discount_data = order.discount_details
            discount_amount = DiscountService.calculate_discount_amount(
                total,
                DiscountTypeEnum(discount_data.get("type")),
                Decimal(str(discount_data.get("value", 0)))
            )
            total = DiscountService.calculate_final_amount(total, discount_amount)

        return round(total, 2)

    @staticmethod
    def apply_order_discount(
        db: Session,
        order_id: int,
        discount_request: ApplyOrderDiscountRequest,
        applied_by_user_id: int
    ) -> OrderDiscountResponse:
        """
        Alkalmaz egy kedvezményt a teljes rendelésre.

        Args:
            db: SQLAlchemy session
            order_id: A rendelés azonosítója
            discount_request: Kedvezmény alkalmazási kérés
            applied_by_user_id: A kedvezményt alkalmazó felhasználó ID-ja

        Returns:
            OrderDiscountResponse: Kedvezmény alkalmazásának eredménye

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha a rendelés már lezárt vagy a kedvezmény érvénytelen

        Example:
            >>> response = DiscountService.apply_order_discount(
            ...     db,
            ...     order_id=42,
            ...     discount_request=ApplyOrderDiscountRequest(
            ...         discount_type="percentage",
            ...         discount_value=10.0,
            ...         reason="Törzsvásárlói kedvezmény"
            ...     ),
            ...     applied_by_user_id=5
            ... )
        """
        # Rendelés lekérése
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelés nem található: ID={order_id}"
            )

        # Ellenőrizzük, hogy a rendelés nem lezárt-e
        if order.status in ["LEZART", "SZTORNÓ"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nem lehet kedvezményt alkalmazni {order.status} státuszú rendelésre"
            )

        # Eredeti összeg számítása (tétel-szintű kedvezmények nélkül)
        original_amount = Decimal("0.00")
        for item in order.order_items:
            item_subtotal = item.unit_price * item.quantity

            # Ha van tétel-szintű kedvezmény, alkalmazzuk
            if item.discount_details:
                discount_data = item.discount_details
                item_discount = DiscountService.calculate_discount_amount(
                    item_subtotal,
                    DiscountTypeEnum(discount_data.get("type")),
                    Decimal(str(discount_data.get("value", 0)))
                )
                item_subtotal = DiscountService.calculate_final_amount(
                    item_subtotal, item_discount
                )

            original_amount += item_subtotal

        # Kedvezmény összegének számítása
        discount_amount = DiscountService.calculate_discount_amount(
            original_amount,
            discount_request.discount_type,
            discount_request.discount_value
        )

        # Végső összeg számítása
        final_amount = DiscountService.calculate_final_amount(
            original_amount, discount_amount
        )

        # Kedvezmény részletek létrehozása
        discount_details = DiscountDetails(
            type=discount_request.discount_type,
            value=discount_request.discount_value,
            reason=discount_request.reason,
            applied_by_user_id=applied_by_user_id,
            applied_at=datetime.now(timezone.utc),
            coupon_code=discount_request.coupon_code
        )

        # Rendelés frissítése
        try:
            order.discount_details = discount_details.model_dump(mode='json')
            order.total_amount = final_amount
            order.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(order)

            # Válasz összeállítása
            calculation = DiscountCalculationResult(
                original_amount=original_amount,
                discount_amount=discount_amount,
                final_amount=final_amount,
                discount_details=discount_details
            )

            return OrderDiscountResponse(
                order_id=order.id,
                message="Kedvezmény sikeresen alkalmazva a rendelésre",
                calculation=calculation,
                updated_total=final_amount
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Hiba a rendelés kedvezmény alkalmazása során: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Hiba a kedvezmény alkalmazása során: {str(e)}"
            )

    @staticmethod
    def apply_item_discount(
        db: Session,
        item_id: int,
        discount_request: ApplyItemDiscountRequest,
        applied_by_user_id: int
    ) -> ItemDiscountResponse:
        """
        Alkalmaz egy kedvezményt egy rendelési tételre.

        Args:
            db: SQLAlchemy session
            item_id: A rendelési tétel azonosítója
            discount_request: Kedvezmény alkalmazási kérés
            applied_by_user_id: A kedvezményt alkalmazó felhasználó ID-ja

        Returns:
            ItemDiscountResponse: Kedvezmény alkalmazásának eredménye

        Raises:
            HTTPException 404: Ha a tétel nem található
            HTTPException 400: Ha a rendelés már lezárt vagy a kedvezmény érvénytelen

        Example:
            >>> response = DiscountService.apply_item_discount(
            ...     db,
            ...     item_id=123,
            ...     discount_request=ApplyItemDiscountRequest(
            ...         discount_type="fixed",
            ...         discount_value=500.0,
            ...         reason="Reklamáció"
            ...     ),
            ...     applied_by_user_id=5
            ... )
        """
        # Tétel lekérése
        item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelési tétel nem található: ID={item_id}"
            )

        # Rendelés ellenőrzése
        order = item.order
        if order.status in ["LEZART", "SZTORNÓ"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nem lehet kedvezményt alkalmazni {order.status} státuszú rendelés tételére"
            )

        # Eredeti tétel összeg
        original_item_amount = item.unit_price * item.quantity

        # Kedvezmény számítása
        discount_amount = DiscountService.calculate_discount_amount(
            original_item_amount,
            discount_request.discount_type,
            discount_request.discount_value
        )

        # Végső tétel összeg
        final_item_amount = DiscountService.calculate_final_amount(
            original_item_amount, discount_amount
        )

        # Kedvezmény részletek létrehozása
        discount_details = DiscountDetails(
            type=discount_request.discount_type,
            value=discount_request.discount_value,
            reason=discount_request.reason,
            applied_by_user_id=applied_by_user_id,
            applied_at=datetime.now(timezone.utc),
            coupon_code=discount_request.coupon_code
        )

        # Tétel frissítése
        try:
            item.discount_details = discount_details.model_dump(mode='json')

            # Rendelés végösszegének újraszámítása
            updated_order_total = DiscountService.recalculate_order_total(db, order)
            order.total_amount = updated_order_total
            order.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(item)
            db.refresh(order)

            # Válasz összeállítása
            calculation = DiscountCalculationResult(
                original_amount=original_item_amount,
                discount_amount=discount_amount,
                final_amount=final_item_amount,
                discount_details=discount_details
            )

            return ItemDiscountResponse(
                item_id=item.id,
                order_id=order.id,
                message="Kedvezmény sikeresen alkalmazva a tételre",
                calculation=calculation,
                updated_item_total=final_item_amount,
                updated_order_total=updated_order_total
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Hiba a tétel kedvezmény alkalmazása során: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Hiba a kedvezmény alkalmazása során: {str(e)}"
            )

    @staticmethod
    def remove_order_discount(db: Session, order_id: int) -> Dict[str, Any]:
        """
        Eltávolítja a kedvezményt egy rendelésről.

        Args:
            db: SQLAlchemy session
            order_id: A rendelés azonosítója

        Returns:
            Dict: Eltávolítás eredménye

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha nincs alkalmazott kedvezmény
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelés nem található: ID={order_id}"
            )

        if not order.discount_details:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nincs alkalmazott kedvezmény ezen a rendelésen"
            )

        try:
            previous_discount = order.discount_details.copy()
            order.discount_details = None

            # Végösszeg újraszámítása
            updated_total = DiscountService.recalculate_order_total(db, order)
            order.total_amount = updated_total
            order.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(order)

            return {
                "message": "Kedvezmény sikeresen eltávolítva",
                "previous_discount": previous_discount,
                "updated_total": updated_total
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Hiba a kedvezmény eltávolítása során: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Hiba a kedvezmény eltávolítása során: {str(e)}"
            )

    @staticmethod
    def remove_item_discount(db: Session, item_id: int) -> Dict[str, Any]:
        """
        Eltávolítja a kedvezményt egy rendelési tételről.

        Args:
            db: SQLAlchemy session
            item_id: A tétel azonosítója

        Returns:
            Dict: Eltávolítás eredménye

        Raises:
            HTTPException 404: Ha a tétel nem található
            HTTPException 400: Ha nincs alkalmazott kedvezmény
        """
        item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelési tétel nem található: ID={item_id}"
            )

        if not item.discount_details:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nincs alkalmazott kedvezmény ezen a tételen"
            )

        try:
            previous_discount = item.discount_details.copy()
            item.discount_details = None

            # Rendelés végösszegének újraszámítása
            order = item.order
            updated_total = DiscountService.recalculate_order_total(db, order)
            order.total_amount = updated_total
            order.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(item)
            db.refresh(order)

            return {
                "message": "Kedvezmény sikeresen eltávolítva",
                "previous_discount": previous_discount,
                "updated_total": updated_total
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Hiba a kedvezmény eltávolítása során: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Hiba a kedvezmény eltávolítása során: {str(e)}"
            )
