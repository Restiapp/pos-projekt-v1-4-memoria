"""
OrderItem Service - Business Logic Layer
Module 1: Rendeléskezelés és Asztalok

Ez a modul felelős a rendelési tételek (order items) kezeléséért.
Támogatja a CRUD műveleteket, a selected_modifiers JSONB mező
helyes kezelését, valamint a KDS (Kitchen Display System) integrációt.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from backend.service_orders.models.order_item import OrderItem, KDSStatus
from backend.service_orders.schemas.order_item import (
    OrderItemCreate,
    OrderItemUpdate,
    OrderItemResponse,
    SelectedModifierSchema,
    KDSStatusEnum
)


class OrderItemService:
    """
    Service osztály a rendelési tételek kezeléséhez.

    Támogatja:
    - Új tétel hozzáadása rendeléshez
    - Tételek lekérdezése rendelés alapján
    - Tétel módosítása
    - Tétel törlése
    - Selected modifiers JSONB kezelése
    """

    @staticmethod
    def add_item_to_order(
        db: Session,
        order_item_data: OrderItemCreate
    ) -> OrderItemResponse:
        """
        Új tétel hozzáadása egy rendeléshez.

        A selected_modifiers JSONB mező helyesen kerül mentésre:
        - Pydantic lista objektumokat dict formátumra konvertáljuk
        - PostgreSQL JSONB típusként tárolja az adatokat

        Args:
            db: SQLAlchemy database session
            order_item_data: Új tétel adatai (OrderItemCreate schema)

        Returns:
            OrderItemResponse: A létrehozott tétel adatai

        Raises:
            SQLAlchemyError: Adatbázis hiba esetén
        """
        try:
            # Selected modifiers konvertálása dict formátumra (JSONB tároláshoz)
            selected_modifiers_dict = None
            if order_item_data.selected_modifiers:
                selected_modifiers_dict = [
                    modifier.model_dump() for modifier in order_item_data.selected_modifiers
                ]

            # Convert KDSStatusEnum to KDSStatus if needed
            kds_status_value = order_item_data.kds_status
            if kds_status_value:
                # Convert from schema enum to model enum
                kds_status_value = KDSStatus(kds_status_value.value)
            else:
                kds_status_value = KDSStatus.WAITING

            # Új OrderItem létrehozása
            new_order_item = OrderItem(
                order_id=order_item_data.order_id,
                product_id=order_item_data.product_id,
                seat_id=order_item_data.seat_id,
                quantity=order_item_data.quantity,
                unit_price=order_item_data.unit_price,
                selected_modifiers=selected_modifiers_dict,
                course=order_item_data.course,
                notes=order_item_data.notes,
                kds_station=order_item_data.kds_station,
                kds_status=kds_status_value
            )

            # Adatbázisba mentés
            db.add(new_order_item)
            db.commit()
            db.refresh(new_order_item)

            return OrderItemResponse.model_validate(new_order_item)

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def update_item_flags(
        db: Session,
        item_id: int,
        flags: Dict[str, Any]
    ) -> OrderItem:
        """
        Update item-level flags (is_urgent, course_tag, sync_with_course).
        Stores them in metadata_json.
        """
        item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Order item not found")

        # Initialize metadata if None
        if item.metadata_json is None:
            item.metadata_json = {}

        # Update flags in metadata
        # We explicitly handle the allowed flags to prevent pollution
        allowed_flags = ["is_urgent", "course_tag", "sync_with_course"]

        # Make a copy to ensure SQLAlchemy detects change
        new_metadata = dict(item.metadata_json)

        for flag in allowed_flags:
            if flag in flags:
                new_metadata[flag] = flags[flag]

        item.metadata_json = new_metadata

        # Also update `course` column if course_tag is present (for backward compat/indexing)
        if "course_tag" in flags:
            item.course = flags["course_tag"]

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get_items_by_order(
        db: Session,
        order_id: int
    ) -> List[OrderItemResponse]:
        """
        Egy rendeléshez tartozó összes tétel lekérdezése.

        Args:
            db: SQLAlchemy database session
            order_id: A rendelés azonosítója

        Returns:
            List[OrderItemResponse]: A rendeléshez tartozó tételek listája
        """
        try:
            order_items = db.query(OrderItem).filter(
                OrderItem.order_id == order_id
            ).all()

            return [
                OrderItemResponse.model_validate(item) for item in order_items
            ]

        except SQLAlchemyError as e:
            raise e

    @staticmethod
    def get_item_by_id(
        db: Session,
        item_id: int
    ) -> Optional[OrderItemResponse]:
        """
        Egy konkrét tétel lekérdezése ID alapján.

        Args:
            db: SQLAlchemy database session
            item_id: A tétel azonosítója

        Returns:
            Optional[OrderItemResponse]: A tétel adatai, vagy None ha nem található
        """
        try:
            order_item = db.query(OrderItem).filter(
                OrderItem.id == item_id
            ).first()

            if order_item:
                return OrderItemResponse.model_validate(order_item)
            return None

        except SQLAlchemyError as e:
            raise e

    @staticmethod
    def update_order_item(
        db: Session,
        item_id: int,
        update_data: OrderItemUpdate
    ) -> Optional[OrderItemResponse]:
        """
        Egy létező tétel módosítása.

        Csak a megadott mezőket frissíti (partial update).
        A selected_modifiers JSONB mezőt is helyesen kezeli.

        Args:
            db: SQLAlchemy database session
            item_id: A módosítandó tétel azonosítója
            update_data: A frissítendő mezők (OrderItemUpdate schema)

        Returns:
            Optional[OrderItemResponse]: A frissített tétel adatai, vagy None ha nem található

        Raises:
            SQLAlchemyError: Adatbázis hiba esetén
        """
        try:
            # Tétel lekérdezése
            order_item = db.query(OrderItem).filter(
                OrderItem.id == item_id
            ).first()

            if not order_item:
                return None

            # Csak a megadott mezők frissítése
            update_dict = update_data.model_dump(exclude_unset=True)

            # Selected modifiers konvertálása dict formátumra (ha van)
            if 'selected_modifiers' in update_dict and update_dict['selected_modifiers'] is not None:
                update_dict['selected_modifiers'] = [
                    modifier.model_dump() for modifier in update_data.selected_modifiers
                ]

            # Mezők frissítése
            for field, value in update_dict.items():
                setattr(order_item, field, value)

            # Adatbázisba mentés
            db.commit()
            db.refresh(order_item)

            return OrderItemResponse.model_validate(order_item)

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def delete_order_item(
        db: Session,
        item_id: int
    ) -> bool:
        """
        Egy tétel törlése a rendelésből.

        Args:
            db: SQLAlchemy database session
            item_id: A törlendő tétel azonosítója

        Returns:
            bool: True ha a törlés sikeres volt, False ha a tétel nem található

        Raises:
            SQLAlchemyError: Adatbázis hiba esetén
        """
        try:
            # Tétel lekérdezése
            order_item = db.query(OrderItem).filter(
                OrderItem.id == item_id
            ).first()

            if not order_item:
                return False

            # Tétel törlése
            db.delete(order_item)
            db.commit()

            return True

        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_items_by_seat(
        db: Session,
        seat_id: int
    ) -> List[OrderItemResponse]:
        """
        Egy székhelyhez tartozó összes tétel lekérdezése.

        Hasznos személyenkénti számla felosztáshoz.

        Args:
            db: SQLAlchemy database session
            seat_id: A székhely azonosítója

        Returns:
            List[OrderItemResponse]: A székhelyhez tartozó tételek listája
        """
        try:
            order_items = db.query(OrderItem).filter(
                OrderItem.seat_id == seat_id
            ).all()

            return [
                OrderItemResponse.model_validate(item) for item in order_items
            ]

        except SQLAlchemyError as e:
            raise e

    @staticmethod
    def get_items_by_kds_station(
        db: Session,
        kds_station: str,
        kds_status: Optional[str] = None
    ) -> List[OrderItemResponse]:
        """
        KDS állomáshoz tartozó tételek lekérdezése.

        Hasznos a Kitchen Display System integrációhoz.

        Args:
            db: SQLAlchemy database session
            kds_station: KDS állomás neve (pl. 'Konyha', 'Pizza', 'Pult')
            kds_status: Opcionális státusz szűrés (pl. 'VÁRAKOZIK', 'KÉSZÜL', 'KÉSZ')

        Returns:
            List[OrderItemResponse]: A szűrési feltételeknek megfelelő tételek listája
        """
        try:
            query = db.query(OrderItem).filter(
                OrderItem.kds_station == kds_station
            )

            if kds_status:
                query = query.filter(OrderItem.kds_status == kds_status)

            order_items = query.all()

            return [
                OrderItemResponse.model_validate(item) for item in order_items
            ]

        except SQLAlchemyError as e:
            raise e

    @staticmethod
    def update_kds_status(
        db: Session,
        item_id: int,
        new_status: str
    ) -> Optional[OrderItemResponse]:
        """
        Egy tétel KDS státuszának frissítése.

        Hasznos a Kitchen Display System munkafolyamatához
        (WAITING -> PREPARING -> READY -> SERVED).

        Args:
            db: SQLAlchemy database session
            item_id: A tétel azonosítója
            new_status: Az új KDS státusz (must be valid KDSStatus value)

        Returns:
            Optional[OrderItemResponse]: A frissített tétel adatai, vagy None ha nem található

        Raises:
            ValueError: If status is invalid
            SQLAlchemyError: Adatbázis hiba esetén
        """
        try:
            # Validate the status
            try:
                validated_status = KDSStatus(new_status)
            except ValueError:
                raise ValueError(
                    f"Invalid KDS status: {new_status}. "
                    f"Valid values: {', '.join([s.value for s in KDSStatus])}"
                )

            order_item = db.query(OrderItem).filter(
                OrderItem.id == item_id
            ).first()

            if not order_item:
                return None

            order_item.kds_status = validated_status
            db.commit()
            db.refresh(order_item)

            return OrderItemResponse.model_validate(order_item)

        except SQLAlchemyError as e:
            db.rollback()
            raise e
