"""
Payment Service - Business Logic Layer
Module 4: Fizetések és Számla Kezelés

Ez a service layer felelős a fizetések üzleti logikájáért, beleértve:
- Fizetések rögzítése és lekérdezése
- Split-check (számla szétosztás) számítások seat_id alapján
- Rendelések fizetettségi státuszának ellenőrzése
- Összbefizetett összegek kalkulációja

Fázis 4.6: PaymentService implementáció
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from backend.service_orders.models.payment import Payment
from backend.service_orders.models.order import Order
from backend.service_orders.models.order_item import OrderItem
from backend.service_orders.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    SplitCheckResponse,
    SplitCheckItemSchema
)


class PaymentService:
    """
    Service osztály a fizetések kezeléséhez.

    Felelősségek:
    - Fizetések létrehozása és lekérdezése
    - Fizetettségi státusz ellenőrzése
    - Split-check számítások (számla szétosztás személyenként/seat alapján)
    - Összbefizetett összegek kalkulációja
    """

    @staticmethod
    def record_payment(db: Session, payment_data: PaymentCreate) -> Payment:
        """
        Új fizetés rögzítése egy rendeléshez.

        Args:
            db: SQLAlchemy session
            payment_data: PaymentCreate schema a bemeneti adatokkal

        Returns:
            Payment: Az újonnan rögzített fizetés

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha a fizetés rögzítése sikertelen

        Example:
            >>> payment_data = PaymentCreate(
            ...     order_id=42,
            ...     payment_method="Készpénz",
            ...     amount=Decimal("5000.00")
            ... )
            >>> payment = PaymentService.record_payment(db, payment_data)
        """
        # Ellenőrizzük, hogy a rendelés létezik-e
        order = db.query(Order).filter(Order.id == payment_data.order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelés nem található: ID={payment_data.order_id}"
            )

        try:
            # Új Payment objektum létrehozása
            db_payment = Payment(
                order_id=payment_data.order_id,
                payment_method=payment_data.payment_method,
                amount=payment_data.amount,
                status='SIKERES'  # Automatikusan sikeres státusz (később bővíthető)
            )

            db.add(db_payment)
            db.commit()
            db.refresh(db_payment)

            return db_payment

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a fizetés rögzítése során: {str(e)}"
            )

    @staticmethod
    def get_payments_for_order(db: Session, order_id: int) -> List[Payment]:
        """
        Egy rendeléshez tartozó összes fizetés lekérdezése.

        Args:
            db: SQLAlchemy session
            order_id: A rendelés azonosítója

        Returns:
            List[Payment]: A rendeléshez tartozó fizetések listája

        Raises:
            HTTPException 404: Ha a rendelés nem található

        Example:
            >>> payments = PaymentService.get_payments_for_order(db, order_id=42)
            >>> for payment in payments:
            ...     print(f"{payment.payment_method}: {payment.amount} HUF")
        """
        # Ellenőrizzük, hogy a rendelés létezik-e
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelés nem található: ID={order_id}"
            )

        # Fizetések lekérdezése
        payments = db.query(Payment).filter(
            Payment.order_id == order_id,
            Payment.status == 'SIKERES'  # Csak sikeres fizetések
        ).all()

        return payments

    @staticmethod
    def calculate_total_paid(db: Session, order_id: int) -> Decimal:
        """
        Egy rendeléshez eddig befizetett összeg kiszámítása.

        Args:
            db: SQLAlchemy session
            order_id: A rendelés azonosítója

        Returns:
            Decimal: Összesen befizetett összeg (csak sikeres fizetések)

        Raises:
            HTTPException 404: Ha a rendelés nem található

        Example:
            >>> total_paid = PaymentService.calculate_total_paid(db, order_id=42)
            >>> print(f"Befizetett összeg: {total_paid} HUF")
        """
        # Ellenőrizzük, hogy a rendelés létezik-e
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelés nem található: ID={order_id}"
            )

        # Összbefizetett összeg kalkulációja (csak sikeres fizetések)
        total = db.query(func.sum(Payment.amount)).filter(
            Payment.order_id == order_id,
            Payment.status == 'SIKERES'
        ).scalar()

        # Ha nincs egyetlen fizetés sem, térjünk vissza 0-val
        return total if total is not None else Decimal("0.00")

    @staticmethod
    def is_order_fully_paid(db: Session, order_id: int) -> bool:
        """
        Ellenőrzi, hogy egy rendelés teljesen ki van-e fizetve.

        A rendelés akkor tekinthető teljesen kifizetettnek, ha a sikeres
        fizetések összege >= rendelés total_amount értéke.

        Args:
            db: SQLAlchemy session
            order_id: A rendelés azonosítója

        Returns:
            bool: True, ha a rendelés teljesen kifizetve, különben False

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha a rendelés total_amount értéke nincs beállítva

        Example:
            >>> if PaymentService.is_order_fully_paid(db, order_id=42):
            ...     print("A rendelés teljesen kifizetve!")
            ... else:
            ...     print("A rendelés még nincs teljesen kifizetve.")
        """
        # Rendelés lekérdezése
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelés nem található: ID={order_id}"
            )

        # Ellenőrizzük, hogy a rendelésnek van-e total_amount értéke
        if order.total_amount is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A rendelés total_amount értéke nincs beállítva: ID={order_id}"
            )

        # Befizetett összeg lekérdezése
        total_paid = PaymentService.calculate_total_paid(db, order_id)

        # Összehasonlítás: befizetett >= rendelés összege
        return total_paid >= order.total_amount

    @staticmethod
    def calculate_split_check(db: Session, order_id: int) -> SplitCheckResponse:
        """
        Számla szétosztása seat_id alapján (split-check funkció).

        Ez a funkció kiszámolja, hogy az asztalnál ülő egyes személyek
        (seat-ek) mennyi összeget tartoznak a rendelésből, az order_items
        seat_id mezője alapján.

        Args:
            db: SQLAlchemy session
            order_id: A rendelés azonosítója

        Returns:
            SplitCheckResponse: A szétosztott számla részletei

        Raises:
            HTTPException 404: Ha a rendelés nem található

        Example:
            >>> split = PaymentService.calculate_split_check(db, order_id=42)
            >>> for item in split.items:
            ...     print(f"Seat {item.seat_number}: {item.person_amount} HUF ({item.item_count} tétel)")

        Működés:
            - Csoportosítja az order_items-eket seat_id alapján
            - Minden seat-hez kiszámolja az összeget (quantity * unit_price)
            - Visszaadja a szétosztott összegeket
        """
        # Rendelés lekérdezése
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelés nem található: ID={order_id}"
            )

        # Order items lekérdezése
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

        # Csoportosítás seat_id alapján
        seat_totals: Dict[Optional[int], Dict[str, Any]] = {}

        for item in order_items:
            seat_key = item.seat_id  # None, ha nincs hozzárendelve seat-hez

            if seat_key not in seat_totals:
                seat_totals[seat_key] = {
                    'seat_id': seat_key,
                    'total_amount': Decimal("0.00"),
                    'item_count': 0,
                    'seat_number': None  # Később bővíthető a Seat kapcsolattal
                }

            # Összeg hozzáadása: quantity * unit_price
            item_total = Decimal(str(item.quantity)) * item.unit_price
            seat_totals[seat_key]['total_amount'] += item_total
            seat_totals[seat_key]['item_count'] += 1

        # SplitCheckItemSchema objektumok létrehozása
        split_items = []
        for seat_data in seat_totals.values():
            split_item = SplitCheckItemSchema(
                seat_id=seat_data['seat_id'],
                seat_number=seat_data['seat_number'],
                person_amount=seat_data['total_amount'],
                item_count=seat_data['item_count']
            )
            split_items.append(split_item)

        # Összes összeg kiszámítása
        total_amount = sum(item.person_amount for item in split_items)

        # SplitCheckResponse létrehozása
        response = SplitCheckResponse(
            order_id=order_id,
            items=split_items,
            total_amount=total_amount
        )

        return response
