"""
KDS Service - Kitchen Display System Business Logic
Module 1: Rendeléskezelés és Asztalok / Epic B: Konyha/KDS

Ez a modul felelős a Kitchen Display System (KDS) funkcionalitásért.
Támogatja a rendelési tételek konyhai státuszának kezelését és
az automatikus rendelés státusz frissítést.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from backend.service_orders.models.order_item import OrderItem, KDSStatus
from backend.service_orders.models.order import Order
from backend.service_orders.schemas.order_item import OrderItemResponse, KDSStatusEnum
from backend.service_orders.schemas.order import OrderStatusEnum


class KDSService:
    """
    Service osztály a Kitchen Display System funkcionalitáshoz.

    Támogatja:
    - Aktív tételek lekérdezése (nem SERVED státuszú)
    - Tételek csoportosítása asztal/rendelés szerint
    - KDS állomás szerinti szűrés
    - Tétel státusz frissítése
    - Automatikus rendelés státusz frissítés (ha minden tétel READY)
    """

    @staticmethod
    def get_active_items(
        db: Session,
        station: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Aktív (nem SERVED) tételek lekérdezése, csoportosítva asztal/rendelés szerint.

        Args:
            db: SQLAlchemy database session
            station: Opcionális KDS állomás szűrés (pl. 'GRILL', 'COLD', 'BAR')

        Returns:
            List[Dict]: Csoportosított tételek listája a következő struktúrával:
                [
                    {
                        "order_id": 1,
                        "table_id": 5,
                        "table_number": "T5",
                        "order_type": "Helyben",
                        "created_at": "2024-01-15T14:30:00",
                        "items": [OrderItemResponse, ...]
                    },
                    ...
                ]

        Raises:
            SQLAlchemyError: Adatbázis hiba esetén
        """
        try:
            # Query for active items (not SERVED)
            query = db.query(OrderItem).filter(
                OrderItem.kds_status != KDSStatus.SERVED
            ).options(joinedload(OrderItem.order))

            # Apply station filter if provided
            if station:
                query = query.filter(OrderItem.kds_station == station)

            # Order by creation time (assuming older orders first)
            active_items = query.join(Order).order_by(Order.created_at.asc()).all()

            # Group items by order
            orders_dict = {}
            for item in active_items:
                order = item.order
                if order.id not in orders_dict:
                    orders_dict[order.id] = {
                        "order_id": order.id,
                        "table_id": order.table_id,
                        "table_number": f"T{order.table_id}" if order.table_id else None,
                        "order_type": order.order_type,
                        "order_status": order.status,
                        "created_at": order.created_at.isoformat() if order.created_at else None,
                        "items": []
                    }

                # Convert OrderItem to OrderItemResponse
                orders_dict[order.id]["items"].append(
                    OrderItemResponse.model_validate(item)
                )

            # Convert dict to list
            return list(orders_dict.values())

        except SQLAlchemyError as e:
            raise e

    @staticmethod
    def update_item_status(
        db: Session,
        item_id: int,
        new_status: KDSStatusEnum
    ) -> Optional[OrderItemResponse]:
        """
        Tétel KDS státuszának frissítése és opcionálisan a rendelés státuszának frissítése.

        Ha az összes tétel READY státuszú, a rendelés státusza is FELDOLGOZVA-ra vált.

        Args:
            db: SQLAlchemy database session
            item_id: A tétel azonosítója
            new_status: Az új KDS státusz (KDSStatusEnum)

        Returns:
            Optional[OrderItemResponse]: A frissített tétel adatai, vagy None ha nem található

        Raises:
            ValueError: If status is invalid
            SQLAlchemyError: Adatbázis hiba esetén
        """
        try:
            # Convert KDSStatusEnum to KDSStatus
            status_value = KDSStatus(new_status.value)

            # Get the item
            order_item = db.query(OrderItem).filter(
                OrderItem.id == item_id
            ).first()

            if not order_item:
                return None

            # Update the item status
            old_status = order_item.kds_status
            order_item.kds_status = status_value

            # Get the order to check if all items are READY
            order = db.query(Order).filter(Order.id == order_item.order_id).first()

            if order:
                # Check if all items in this order are READY
                all_items = db.query(OrderItem).filter(
                    OrderItem.order_id == order.id
                ).all()

                # Check if all items are READY
                all_ready = all(item.kds_status == KDSStatus.READY for item in all_items)

                # If all items are READY and order is not already processed/closed, update order status
                if all_ready and order.status == OrderStatusEnum.NYITOTT.value:
                    order.status = OrderStatusEnum.FELDOLGOZVA.value

            db.commit()
            db.refresh(order_item)

            return OrderItemResponse.model_validate(order_item)

        except ValueError as e:
            db.rollback()
            raise ValueError(f"Invalid KDS status: {new_status}")
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_items_by_station_and_status(
        db: Session,
        station: str,
        status: Optional[KDSStatusEnum] = None
    ) -> List[OrderItemResponse]:
        """
        KDS állomáshoz és opcionálisan státuszhoz tartozó tételek lekérdezése.

        Args:
            db: SQLAlchemy database session
            station: KDS állomás neve (pl. 'GRILL', 'COLD', 'BAR')
            status: Opcionális státusz szűrés

        Returns:
            List[OrderItemResponse]: A szűrési feltételeknek megfelelő tételek listája

        Raises:
            SQLAlchemyError: Adatbázis hiba esetén
        """
        try:
            query = db.query(OrderItem).filter(
                OrderItem.kds_station == station
            )

            if status:
                status_value = KDSStatus(status.value)
                query = query.filter(OrderItem.kds_status == status_value)

            order_items = query.all()

            return [
                OrderItemResponse.model_validate(item) for item in order_items
            ]

        except SQLAlchemyError as e:
            raise e

    @staticmethod
    def toggle_urgent_flag(
        db: Session,
        item_id: int,
        is_urgent: bool
    ) -> Optional[OrderItemResponse]:
        """
        Toggle the urgent flag for a KDS item.

        Args:
            db: SQLAlchemy database session
            item_id: The order item ID
            is_urgent: The new urgent flag value (True/False)

        Returns:
            Optional[OrderItemResponse]: Updated item details, or None if not found

        Raises:
            SQLAlchemyError: Database error
        """
        try:
            # Get the item
            order_item = db.query(OrderItem).filter(
                OrderItem.id == item_id
            ).first()

            if not order_item:
                return None

            # Update the urgent flag
            order_item.is_urgent = is_urgent

            db.commit()
            db.refresh(order_item)

            return OrderItemResponse.model_validate(order_item)

        except SQLAlchemyError as e:
            db.rollback()
            raise e
