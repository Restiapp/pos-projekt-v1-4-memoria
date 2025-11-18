"""
Gift Card Service - Business Logic Layer
Module 5: Customer Relationship Management (CRM)

Ez a service layer felelős az ajándékkártyák üzleti logikájáért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- Ajándékkártya beváltás (redeem)
- Egyenleg kezelése és módosítása
- Validáció és lejárat kezelés
"""

from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from fastapi import HTTPException, status
import logging

from backend.service_crm.models.gift_card import GiftCard
from backend.service_crm.schemas.gift_card import (
    GiftCardCreate,
    GiftCardUpdate,
    GiftCardRedemption,
    GiftCardBalanceUpdate
)

logger = logging.getLogger(__name__)


class GiftCardService:
    """
    Service osztály az ajándékkártyák kezeléséhez.

    Felelősségek:
    - Ajándékkártyák létrehozása, lekérdezése, módosítása, törlése
    - Beváltás (redeem) kezelése
    - Egyenleg módosítások (refund, bonus)
    - Kód egyediség validáció
    """

    @staticmethod
    def create_gift_card(db: Session, gift_card_data: GiftCardCreate) -> GiftCard:
        """
        Új ajándékkártya létrehozása.

        Args:
            db: SQLAlchemy session
            gift_card_data: GiftCardCreate schema a bemeneti adatokkal

        Returns:
            GiftCard: Az újonnan létrehozott ajándékkártya

        Raises:
            HTTPException 400: Ha a kártya kód már létezik vagy az adatok érvénytelenek

        Example:
            >>> gift_card_data = GiftCardCreate(
            ...     card_code="GIFT-2024-ABC123",
            ...     initial_balance=Decimal("10000.00"),
            ...     valid_until=None
            ... )
            >>> new_gift_card = GiftCardService.create_gift_card(db, gift_card_data)
        """
        # Ellenőrizzük, hogy a kártya kód már létezik-e
        existing_card = db.query(GiftCard).filter(
            GiftCard.card_code == gift_card_data.card_code
        ).first()

        if existing_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ez a kártya kód már használatban van: {gift_card_data.card_code}"
            )

        try:
            # Új GiftCard objektum létrehozása
            db_gift_card = GiftCard(
                card_code=gift_card_data.card_code,
                pin_code=gift_card_data.pin_code,
                initial_balance=gift_card_data.initial_balance,
                current_balance=gift_card_data.initial_balance,  # Kezdetben = initial_balance
                valid_until=gift_card_data.valid_until,
                is_active=gift_card_data.is_active,
                customer_id=gift_card_data.customer_id,
                purchased_by_customer_id=gift_card_data.purchased_by_customer_id,
                purchase_order_id=gift_card_data.purchase_order_id
            )

            db.add(db_gift_card)
            db.commit()
            db.refresh(db_gift_card)

            logger.info(f"Gift card created: {db_gift_card.id} - {db_gift_card.card_code}")
            return db_gift_card

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating gift card: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az ajándékkártya létrehozása során: {str(e)}"
            )

    @staticmethod
    def get_gift_card(db: Session, gift_card_id: int) -> GiftCard:
        """
        Egy ajándékkártya lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            gift_card_id: Az ajándékkártya azonosítója

        Returns:
            GiftCard: A lekérdezett ajándékkártya

        Raises:
            HTTPException 404: Ha az ajándékkártya nem található

        Example:
            >>> gift_card = GiftCardService.get_gift_card(db, gift_card_id=42)
        """
        gift_card = db.query(GiftCard).filter(GiftCard.id == gift_card_id).first()

        if not gift_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ajándékkártya nem található: ID={gift_card_id}"
            )

        return gift_card

    @staticmethod
    def get_gift_card_by_code(db: Session, card_code: str) -> Optional[GiftCard]:
        """
        Ajándékkártya keresése kód alapján.

        Args:
            db: SQLAlchemy session
            card_code: Ajándékkártya kódja

        Returns:
            Optional[GiftCard]: Az ajándékkártya vagy None

        Example:
            >>> gift_card = GiftCardService.get_gift_card_by_code(db, "GIFT-2024-ABC123")
        """
        return db.query(GiftCard).filter(GiftCard.card_code == card_code).first()

    @staticmethod
    def get_gift_cards(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        customer_id: Optional[int] = None,
        is_valid: Optional[bool] = None
    ) -> List[GiftCard]:
        """
        Ajándékkártyák listájának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            skip: Kihagyandó elemek száma (pagination)
            limit: Maximum visszaadott elemek száma
            search: Keresési kifejezés (kártya kód alapján)
            is_active: Szűrés aktív/inaktív kártyákra
            customer_id: Szűrés ügyfél ID alapján
            is_valid: Szűrés érvényes kártyákra (aktív + nem lejárt + van egyenleg)

        Returns:
            List[GiftCard]: Ajándékkártyák listája

        Example:
            >>> gift_cards = GiftCardService.get_gift_cards(
            ...     db,
            ...     skip=0,
            ...     limit=20,
            ...     is_active=True,
            ...     customer_id=42
            ... )
        """
        query = db.query(GiftCard)

        # Keresés kártya kód alapján
        if search:
            query = query.filter(GiftCard.card_code.ilike(f"%{search}%"))

        # Aktív/inaktív szűrés
        if is_active is not None:
            query = query.filter(GiftCard.is_active == is_active)

        # Ügyfél szűrés
        if customer_id is not None:
            query = query.filter(GiftCard.customer_id == customer_id)

        # Érvényesség szűrés
        if is_valid is not None:
            if is_valid:
                # Csak aktív, pozitív egyenlegű és nem lejárt kártyák
                query = query.filter(
                    GiftCard.is_active == True,
                    GiftCard.current_balance > 0
                )
                # Lejárat ellenőrzés
                now = datetime.now()
                query = query.filter(
                    or_(
                        GiftCard.valid_until == None,
                        GiftCard.valid_until > now
                    )
                )

        # Rendezés: legutóbb létrehozott először
        query = query.order_by(desc(GiftCard.created_at))

        # Pagination
        gift_cards = query.offset(skip).limit(limit).all()

        return gift_cards

    @staticmethod
    def update_gift_card(
        db: Session,
        gift_card_id: int,
        gift_card_data: GiftCardUpdate
    ) -> GiftCard:
        """
        Ajándékkártya adatainak módosítása.

        Args:
            db: SQLAlchemy session
            gift_card_id: A módosítandó ajándékkártya azonosítója
            gift_card_data: GiftCardUpdate schema a módosítandó mezőkkel

        Returns:
            GiftCard: A módosított ajándékkártya

        Raises:
            HTTPException 404: Ha az ajándékkártya nem található
            HTTPException 400: Ha a módosítás sikertelen

        Example:
            >>> update_data = GiftCardUpdate(is_active=False)
            >>> updated_card = GiftCardService.update_gift_card(db, gift_card_id=42, gift_card_data=update_data)
        """
        # Ajándékkártya lekérdezése
        gift_card = GiftCardService.get_gift_card(db, gift_card_id)

        try:
            # Csak a megadott mezők frissítése (exclude_unset=True)
            update_dict = gift_card_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                setattr(gift_card, field, value)

            db.commit()
            db.refresh(gift_card)

            logger.info(f"Gift card updated: {gift_card.id}")
            return gift_card

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating gift card {gift_card_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az ajándékkártya módosítása során: {str(e)}"
            )

    @staticmethod
    def delete_gift_card(db: Session, gift_card_id: int) -> Dict[str, Any]:
        """
        Ajándékkártya törlése (soft delete - is_active = False).

        Args:
            db: SQLAlchemy session
            gift_card_id: A törlendő ajándékkártya azonosítója

        Returns:
            Dict: Megerősítő üzenet

        Raises:
            HTTPException 404: Ha az ajándékkártya nem található

        Example:
            >>> result = GiftCardService.delete_gift_card(db, gift_card_id=42)
        """
        gift_card = GiftCardService.get_gift_card(db, gift_card_id)

        try:
            # Soft delete: is_active = False
            gift_card.is_active = False
            db.commit()

            logger.info(f"Gift card deactivated: {gift_card_id}")
            return {
                "message": "Ajándékkártya sikeresen inaktiválva",
                "gift_card_id": gift_card_id
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting gift card {gift_card_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az ajándékkártya törlése során: {str(e)}"
            )

    @staticmethod
    def count_gift_cards(
        db: Session,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        customer_id: Optional[int] = None,
        is_valid: Optional[bool] = None
    ) -> int:
        """
        Ajándékkártyák számának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            search: Keresési kifejezés
            is_active: Szűrés aktív/inaktív kártyákra
            customer_id: Szűrés ügyfél ID alapján
            is_valid: Szűrés érvényes kártyákra

        Returns:
            int: Ajándékkártyák száma

        Example:
            >>> count = GiftCardService.count_gift_cards(db, is_active=True)
        """
        query = db.query(GiftCard)

        if search:
            query = query.filter(GiftCard.card_code.ilike(f"%{search}%"))

        if is_active is not None:
            query = query.filter(GiftCard.is_active == is_active)

        if customer_id is not None:
            query = query.filter(GiftCard.customer_id == customer_id)

        if is_valid is not None:
            if is_valid:
                query = query.filter(
                    GiftCard.is_active == True,
                    GiftCard.current_balance > 0
                )
                now = datetime.now()
                query = query.filter(
                    or_(
                        GiftCard.valid_until == None,
                        GiftCard.valid_until > now
                    )
                )

        return query.count()

    @staticmethod
    def redeem_gift_card(
        db: Session,
        redemption_data: GiftCardRedemption
    ) -> Dict[str, Any]:
        """
        Ajándékkártya beváltása (egyenleg levonás).

        Args:
            db: SQLAlchemy session
            redemption_data: GiftCardRedemption schema a beváltási adatokkal

        Returns:
            Dict: Beváltás eredménye

        Raises:
            HTTPException 404: Ha a kártya nem található
            HTTPException 400: Ha a kártya érvénytelen vagy nincs elegendő egyenleg

        Example:
            >>> redemption = GiftCardRedemption(
            ...     card_code="GIFT-2024-ABC123",
            ...     amount=Decimal("5000.00")
            ... )
            >>> result = GiftCardService.redeem_gift_card(db, redemption)
        """
        # Ajándékkártya keresése kód alapján
        gift_card = GiftCardService.get_gift_card_by_code(db, redemption_data.card_code)

        if not gift_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ajándékkártya nem található: {redemption_data.card_code}"
            )

        # PIN ellenőrzés (ha van)
        if gift_card.pin_code and gift_card.pin_code != redemption_data.pin_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hibás PIN kód"
            )

        # Érvényesség ellenőrzés
        if not gift_card.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Az ajándékkártya inaktív"
            )

        if gift_card.valid_until:
            now = datetime.now()
            if gift_card.valid_until < now:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Az ajándékkártya lejárt: {gift_card.valid_until.strftime('%Y-%m-%d')}"
                )

        # Egyenleg ellenőrzés
        if gift_card.current_balance < redemption_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nincs elegendő egyenleg. Jelenlegi: {gift_card.current_balance} HUF, "
                       f"Beváltani kívánt: {redemption_data.amount} HUF"
            )

        try:
            # Egyenleg levonása
            gift_card.current_balance -= redemption_data.amount
            gift_card.last_used_at = datetime.now()

            db.commit()
            db.refresh(gift_card)

            logger.info(f"Gift card redeemed: {gift_card.id} - {redemption_data.amount} HUF")

            return {
                "success": True,
                "message": "Ajándékkártya sikeresen beváltva",
                "redeemed_amount": redemption_data.amount,
                "remaining_balance": gift_card.current_balance,
                "gift_card_id": gift_card.id
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error redeeming gift card {gift_card.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az ajándékkártya beváltása során: {str(e)}"
            )

    @staticmethod
    def update_balance(
        db: Session,
        gift_card_id: int,
        balance_data: GiftCardBalanceUpdate
    ) -> GiftCard:
        """
        Ajándékkártya egyenlegének módosítása (refund, bonus, correction).

        Args:
            db: SQLAlchemy session
            gift_card_id: Az ajándékkártya azonosítója
            balance_data: GiftCardBalanceUpdate schema az egyenleg módosítással

        Returns:
            GiftCard: A módosított ajándékkártya

        Raises:
            HTTPException 404: Ha az ajándékkártya nem található
            HTTPException 400: Ha az egyenleg negatívba menne

        Example:
            >>> balance_update = GiftCardBalanceUpdate(
            ...     amount=Decimal("1000.00"),
            ...     reason="Refund from cancelled order"
            ... )
            >>> card = GiftCardService.update_balance(db, gift_card_id=42, balance_data=balance_update)
        """
        gift_card = GiftCardService.get_gift_card(db, gift_card_id)

        try:
            new_balance = gift_card.current_balance + balance_data.amount

            if new_balance < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Az egyenleg nem lehet negatív. Jelenlegi: {gift_card.current_balance}, "
                           f"Módosítás: {balance_data.amount}"
                )

            gift_card.current_balance = new_balance
            db.commit()
            db.refresh(gift_card)

            logger.info(f"Gift card balance updated: {gift_card_id} - {balance_data.amount} ({balance_data.reason})")
            return gift_card

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating balance for gift card {gift_card_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az egyenleg módosítása során: {str(e)}"
            )

    @staticmethod
    def validate_gift_card(
        db: Session,
        card_code: str,
        pin_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ajándékkártya validálása (érvényesség ellenőrzés).

        Args:
            db: SQLAlchemy session
            card_code: Ajándékkártya kódja
            pin_code: PIN kód (opcionális)

        Returns:
            Dict: Validációs eredmény

        Raises:
            HTTPException 404: Ha a kártya nem található

        Example:
            >>> result = GiftCardService.validate_gift_card(db, "GIFT-2024-ABC123")
        """
        gift_card = GiftCardService.get_gift_card_by_code(db, card_code)

        if not gift_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ajándékkártya nem található: {card_code}"
            )

        # PIN ellenőrzés
        pin_valid = True
        if gift_card.pin_code:
            pin_valid = (gift_card.pin_code == pin_code)

        # Érvényesség ellenőrzés
        is_valid = gift_card.is_valid and pin_valid

        validation_errors = []
        if not gift_card.is_active:
            validation_errors.append("A kártya inaktív")
        if gift_card.current_balance <= 0:
            validation_errors.append("Nincs egyenleg a kártyán")
        if gift_card.valid_until:
            now = datetime.now()
            if gift_card.valid_until < now:
                validation_errors.append(f"A kártya lejárt: {gift_card.valid_until.strftime('%Y-%m-%d')}")
        if not pin_valid:
            validation_errors.append("Hibás PIN kód")

        return {
            "valid": is_valid,
            "card_code": card_code,
            "current_balance": gift_card.current_balance,
            "is_active": gift_card.is_active,
            "is_assigned": gift_card.is_assigned,
            "valid_until": gift_card.valid_until,
            "errors": validation_errors if validation_errors else None
        }
