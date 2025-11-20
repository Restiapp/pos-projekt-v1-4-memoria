"""
FinanceService - Pénzügyi (Finance) kezelés
Module 8: Admin - Finance Management (V3.0 Phase 1)

Ez a service felelős a pénzügyi műveletek kezeléséért:
- Készpénz befizetések és kivételek (cash drawer operations)
- Napi pénztárzárás (daily closure)
- Pénzmozgások nyomon követése
"""

from typing import Optional, List, Dict
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
import httpx
import logging

from backend.service_admin.models.finance import (
    CashMovement,
    CashMovementType,
    DailyClosure,
    ClosureStatus
)
from backend.service_admin.config import settings

# Logger inicializálás
logger = logging.getLogger(__name__)


class FinanceService:
    """
    Service osztály a pénzügyi műveletek kezeléséhez.

    Felelősségek:
    - Készpénz befizetések és kivételek kezelése
    - Napi pénztárzárás létrehozása és kezelése
    - Pénzmozgások lekérdezése
    - Pénzügyi egyenlegek számítása
    """

    def __init__(self, db: Session):
        """
        Inicializálja a FinanceService-t.

        Args:
            db: SQLAlchemy Session objektum dependency injectionből
        """
        self.db = db

    # ========================================================================
    # Cash Movement Operations (Pénzmozgások)
    # ========================================================================

    def record_cash_deposit(
        self,
        amount: Decimal,
        description: Optional[str] = None,
        employee_id: Optional[int] = None,
        order_id: Optional[int] = None
    ) -> CashMovement:
        """
        Készpénz befizetés rögzítése.

        Args:
            amount: Befizetés összege (pozitív érték)
            description: Leírás/megjegyzés
            employee_id: Munkatárs aki végrehajtotta
            order_id: Kapcsolódó rendelés azonosító (opcionális)

        Returns:
            CashMovement: Létrehozott pénzmozgás rekord

        Raises:
            ValueError: Ha az összeg nem pozitív
        """
        if amount <= 0:
            raise ValueError("A befizetés összegének pozitívnak kell lennie")

        movement = CashMovement(
            movement_type=CashMovementType.CASH_IN,
            amount=amount,
            description=description or "Készpénz befizetés",
            employee_id=employee_id,
            order_id=order_id
        )

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)

        return movement

    def record_cash_withdrawal(
        self,
        amount: Decimal,
        description: Optional[str] = None,
        employee_id: Optional[int] = None,
        order_id: Optional[int] = None
    ) -> CashMovement:
        """
        Készpénz kivétel rögzítése.

        Args:
            amount: Kivétel összege (pozitív érték, de negatívként lesz tárolva)
            description: Leírás/megjegyzés
            employee_id: Munkatárs aki végrehajtotta
            order_id: Kapcsolódó rendelés azonosító (opcionális)

        Returns:
            CashMovement: Létrehozott pénzmozgás rekord

        Raises:
            ValueError: Ha az összeg nem pozitív vagy nincs elegendő készpénz
        """
        if amount <= 0:
            raise ValueError("A kivétel összegének pozitívnak kell lennie")

        # Ellenőrizzük hogy van-e elegendő készpénz
        current_balance = self.get_current_cash_balance()
        if current_balance < amount:
            raise ValueError(
                f"Nincs elegendő készpénz a kivételhez. "
                f"Aktuális egyenleg: {current_balance}, Kért összeg: {amount}"
            )

        movement = CashMovement(
            movement_type=CashMovementType.CASH_OUT,
            amount=-amount,  # Negatív érték a kivételnél
            description=description or "Készpénz kivétel",
            employee_id=employee_id,
            order_id=order_id
        )

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)

        return movement

    def record_sale(
        self,
        amount: Decimal,
        order_id: int,
        employee_id: Optional[int] = None
    ) -> CashMovement:
        """
        Értékesítési tranzakció rögzítése.

        Args:
            amount: Értékesítés összege
            order_id: Rendelés azonosító
            employee_id: Munkatárs aki az értékesítést végrehajtotta

        Returns:
            CashMovement: Létrehozott pénzmozgás rekord
        """
        movement = CashMovement(
            movement_type=CashMovementType.SALE,
            amount=amount,
            description=f"Értékesítés - Rendelés #{order_id}",
            employee_id=employee_id,
            order_id=order_id
        )

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)

        return movement

    def get_cash_movements(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        movement_type: Optional[CashMovementType] = None,
        employee_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CashMovement]:
        """
        Pénzmozgások lekérdezése szűrési feltételekkel.

        Args:
            start_date: Kezdő dátum (opcionális)
            end_date: Záró dátum (opcionális)
            movement_type: Mozgás típusa (opcionális)
            employee_id: Munkatárs azonosító (opcionális)
            limit: Maximum eredmények száma
            offset: Lapozási eltolás

        Returns:
            List[CashMovement]: Pénzmozgások listája
        """
        query = self.db.query(CashMovement)

        if start_date:
            query = query.filter(CashMovement.created_at >= start_date)

        if end_date:
            query = query.filter(CashMovement.created_at <= end_date)

        if movement_type:
            query = query.filter(CashMovement.movement_type == movement_type)

        if employee_id:
            query = query.filter(CashMovement.employee_id == employee_id)

        query = query.order_by(desc(CashMovement.created_at))
        query = query.limit(limit).offset(offset)

        return query.all()

    def get_current_cash_balance(self) -> Decimal:
        """
        Aktuális készpénz egyenleg lekérdezése.

        Összegzi az összes pénzmozgást ami még nincs lezárt napi záráshoz rendelve.

        Returns:
            Decimal: Aktuális készpénz egyenleg
        """
        result = self.db.query(
            func.sum(CashMovement.amount)
        ).filter(
            CashMovement.daily_closure_id.is_(None)
        ).scalar()

        return result or Decimal("0.00")

    # ========================================================================
    # Daily Closure Operations (Napi Pénztárzárás)
    # ========================================================================

    def create_daily_closure(
        self,
        opening_balance: Decimal,
        closed_by_employee_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> DailyClosure:
        """
        Napi pénztárzárás létrehozása.

        Args:
            opening_balance: Nyitó egyenleg
            closed_by_employee_id: Munkatárs aki a zárást végrehajtja
            notes: Megjegyzések

        Returns:
            DailyClosure: Létrehozott napi zárás rekord

        Raises:
            ValueError: Ha már van nyitott zárás a mai napra
        """
        # Ellenőrizzük hogy van-e már nyitott zárás ma
        today = datetime.now().date()
        existing_closure = self.db.query(DailyClosure).filter(
            and_(
                func.date(DailyClosure.closure_date) == today,
                DailyClosure.status != ClosureStatus.CLOSED
            )
        ).first()

        if existing_closure:
            raise ValueError("Már van nyitott pénztárzárás a mai napra")

        closure = DailyClosure(
            closure_date=datetime.now(),
            status=ClosureStatus.OPEN,
            opening_balance=opening_balance,
            notes=notes,
            closed_by_employee_id=closed_by_employee_id
        )

        self.db.add(closure)
        self.db.commit()
        self.db.refresh(closure)

        return closure

    def close_daily_closure(
        self,
        closure_id: int,
        actual_closing_balance: Decimal,
        notes: Optional[str] = None
    ) -> DailyClosure:
        """
        Napi pénztárzárás lezárása.

        Args:
            closure_id: Zárás azonosító
            actual_closing_balance: Tényleges záró egyenleg
            notes: Megjegyzések az eltéréshez

        Returns:
            DailyClosure: Frissített napi zárás rekord

        Raises:
            ValueError: Ha a zárás nem található vagy már lezárt
        """
        closure = self.db.query(DailyClosure).filter(
            DailyClosure.id == closure_id
        ).first()

        if not closure:
            raise ValueError(f"Napi zárás nem található: {closure_id}")

        if closure.status == ClosureStatus.CLOSED:
            raise ValueError("A zárás már lezárt")

        # Várható záró egyenleg számítása
        movements_sum = self.db.query(
            func.sum(CashMovement.amount)
        ).filter(
            CashMovement.daily_closure_id.is_(None)
        ).scalar() or Decimal("0.00")

        expected_closing_balance = closure.opening_balance + movements_sum

        # Fizetési módok szerinti összegzés lekérése a service_orders-től
        payment_summary = self._fetch_payment_summary(closure.closure_date)

        # Frissítjük a zárást
        closure.expected_closing_balance = expected_closing_balance
        closure.actual_closing_balance = actual_closing_balance
        closure.difference = actual_closing_balance - expected_closing_balance
        closure.payment_summary = payment_summary  # Fizetési módok szerinti bontás
        closure.status = ClosureStatus.CLOSED
        closure.closed_at = datetime.now()

        if notes:
            closure.notes = notes

        # Hozzárendeljük a pénzmozgásokat a záráshoz
        self.db.query(CashMovement).filter(
            CashMovement.daily_closure_id.is_(None)
        ).update({"daily_closure_id": closure_id})

        self.db.commit()
        self.db.refresh(closure)

        return closure

    def _fetch_payment_summary(self, closure_date: datetime) -> Optional[Dict[str, float]]:
        """
        Fizetési módok szerinti összegzés lekérése a service_orders-től.

        Args:
            closure_date: A zárás dátuma

        Returns:
            Optional[Dict[str, float]]: Fizetési módok szerinti összegzés vagy None hiba esetén
        """
        try:
            # Dátum konvertálása ISO formátumra (YYYY-MM-DD)
            target_date = closure_date.date().isoformat()

            # HTTP kérés a service_orders felé
            url = f"{settings.orders_service_url}/api/v1/reports/daily-payments"
            params = {"target_date": target_date}

            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()  # Raise exception for 4xx/5xx responses

            payment_summary = response.json()
            logger.info(f"Fizetési összegzés sikeresen lekérve: {payment_summary}")

            return payment_summary

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP hiba a fizetési összegzés lekérésekor: {e.response.status_code} - {e.response.text}"
            )
            return None
        except httpx.RequestError as e:
            logger.error(f"Hálózati hiba a fizetési összegzés lekérésekor: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Váratlan hiba a fizetési összegzés lekérésekor: {str(e)}")
            return None

    def get_daily_closures(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[ClosureStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DailyClosure]:
        """
        Napi zárások lekérdezése szűrési feltételekkel.

        Args:
            start_date: Kezdő dátum (opcionális)
            end_date: Záró dátum (opcionális)
            status: Státusz (opcionális)
            limit: Maximum eredmények száma
            offset: Lapozási eltolás

        Returns:
            List[DailyClosure]: Napi zárások listája
        """
        query = self.db.query(DailyClosure)

        if start_date:
            query = query.filter(func.date(DailyClosure.closure_date) >= start_date)

        if end_date:
            query = query.filter(func.date(DailyClosure.closure_date) <= end_date)

        if status:
            query = query.filter(DailyClosure.status == status)

        query = query.order_by(desc(DailyClosure.closure_date))
        query = query.limit(limit).offset(offset)

        return query.all()

    def get_daily_closure_by_id(self, closure_id: int) -> Optional[DailyClosure]:
        """
        Napi zárás lekérdezése azonosító alapján.

        Args:
            closure_id: Zárás azonosító

        Returns:
            Optional[DailyClosure]: Napi zárás vagy None
        """
        return self.db.query(DailyClosure).filter(
            DailyClosure.id == closure_id
        ).first()

    def get_current_open_closure(self) -> Optional[DailyClosure]:
        """
        Aktuális nyitott napi zárás lekérdezése.

        Returns:
            Optional[DailyClosure]: Nyitott napi zárás vagy None
        """
        today = datetime.now().date()
        return self.db.query(DailyClosure).filter(
            and_(
                func.date(DailyClosure.closure_date) == today,
                DailyClosure.status == ClosureStatus.OPEN
            )
        ).first()
