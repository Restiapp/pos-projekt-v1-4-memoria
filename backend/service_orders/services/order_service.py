"""
Order Service - Business Logic Layer
Module 1: Rendeléskezelés és Asztalok

Ez a service layer felelős a rendelések üzleti logikájáért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- NTAK-kompatibilis ÁFA váltás (27% -> 5%)
- Státusz validáció és átmenetek

Fázis 4.3 & 4.4: Order Service és NTAK ÁFA logika
"""

from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from backend.service_orders.models.order import Order
from backend.service_orders.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderStatusEnum
)


class OrderService:
    """
    Service osztály a rendelések kezeléséhez.

    Felelősségek:
    - Rendelések létrehozása, lekérdezése, módosítása, törlése
    - NTAK ÁFA váltás logika (27% <-> 5%)
    - Státusz validáció (csak NYITOTT rendeléseknél engedélyezett a módosítás)
    """

    @staticmethod
    def create_order(db: Session, order_data: OrderCreate) -> Order:
        """
        Új rendelés létrehozása.

        Args:
            db: SQLAlchemy session
            order_data: OrderCreate schema a bemeneti adatokkal

        Returns:
            Order: Az újonnan létrehozott rendelés

        Raises:
            HTTPException: Ha az adatok érvénytelenek

        Example:
            >>> order_data = OrderCreate(
            ...     order_type="Helyben",
            ...     status="NYITOTT",
            ...     table_id=5
            ... )
            >>> new_order = OrderService.create_order(db, order_data)
        """
        try:
            # Új Order objektum létrehozása
            db_order = Order(
                order_type=order_data.order_type.value,
                status=order_data.status.value,
                table_id=order_data.table_id,
                total_amount=order_data.total_amount,
                final_vat_rate=order_data.final_vat_rate,
                ntak_data=order_data.ntak_data
            )

            db.add(db_order)
            db.commit()
            db.refresh(db_order)

            return db_order

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a rendelés létrehozása során: {str(e)}"
            )

    @staticmethod
    def get_order(db: Session, order_id: int) -> Order:
        """
        Egy rendelés lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            order_id: A rendelés azonosítója

        Returns:
            Order: A lekérdezett rendelés

        Raises:
            HTTPException 404: Ha a rendelés nem található

        Example:
            >>> order = OrderService.get_order(db, order_id=42)
        """
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rendelés nem található: ID={order_id}"
            )

        return order

    @staticmethod
    def get_orders(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_type: Optional[str] = None,
        status: Optional[str] = None,
        table_id: Optional[int] = None
    ) -> List[Order]:
        """
        Rendelések listájának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            skip: Kihagyandó elemek száma (pagination)
            limit: Maximum visszaadott elemek száma
            order_type: Szűrés rendelés típusra (pl. 'Helyben')
            status: Szűrés státuszra (pl. 'NYITOTT')
            table_id: Szűrés asztal ID-ra

        Returns:
            List[Order]: Rendelések listája

        Example:
            >>> orders = OrderService.get_orders(
            ...     db,
            ...     skip=0,
            ...     limit=20,
            ...     status='NYITOTT'
            ... )
        """
        query = db.query(Order)

        # Szűrők alkalmazása, ha vannak
        if order_type:
            query = query.filter(Order.order_type == order_type)
        if status:
            query = query.filter(Order.status == status)
        if table_id:
            query = query.filter(Order.table_id == table_id)

        # Rendezés: legutóbbi először
        query = query.order_by(desc(Order.created_at))

        # Pagination
        orders = query.offset(skip).limit(limit).all()

        return orders

    @staticmethod
    def update_order(
        db: Session,
        order_id: int,
        order_data: OrderUpdate
    ) -> Order:
        """
        Rendelés módosítása.

        Args:
            db: SQLAlchemy session
            order_id: A módosítandó rendelés azonosítója
            order_data: OrderUpdate schema a módosítandó mezőkkel

        Returns:
            Order: A módosított rendelés

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha a módosítás sikertelen

        Example:
            >>> update_data = OrderUpdate(status="FELDOLGOZVA")
            >>> updated_order = OrderService.update_order(db, order_id=42, order_data=update_data)
        """
        # Rendelés lekérdezése
        order = OrderService.get_order(db, order_id)

        try:
            # Csak a megadott mezők frissítése (exclude_unset=True)
            update_dict = order_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                # Enum értékek kezelése
                if hasattr(value, 'value'):
                    setattr(order, field, value.value)
                else:
                    setattr(order, field, value)

            db.commit()
            db.refresh(order)

            return order

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a rendelés módosítása során: {str(e)}"
            )

    @staticmethod
    def delete_order(db: Session, order_id: int) -> Dict[str, Any]:
        """
        Rendelés törlése.

        Args:
            db: SQLAlchemy session
            order_id: A törlendő rendelés azonosítója

        Returns:
            Dict: Megerősítő üzenet

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha a törlés sikertelen

        Example:
            >>> result = OrderService.delete_order(db, order_id=42)
            >>> print(result)
            {'message': 'Rendelés sikeresen törölve', 'order_id': 42}
        """
        # Rendelés lekérdezése
        order = OrderService.get_order(db, order_id)

        try:
            db.delete(order)
            db.commit()

            return {
                "message": "Rendelés sikeresen törölve",
                "order_id": order_id
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a rendelés törlése során: {str(e)}"
            )

    @staticmethod
    def set_vat_to_local(db: Session, order_id: int) -> Order:
        """
        NTAK ÁFA váltás: 27% -> 5% (helyi felhasználás).

        Ez a funkció a NTAK (Nemzeti Turisztikai Adatszolgáltatási Központ)
        előírások szerint lehetővé teszi az ÁFA kulcs váltását 5%-ra,
        amennyiben a rendelés "helyben" kerül elfogyasztásra.

        FONTOS: Az ÁFA váltás csak NYITOTT státuszú rendeléseknél engedélyezett!

        Args:
            db: SQLAlchemy session
            order_id: A rendelés azonosítója

        Returns:
            Order: A módosított rendelés 5%-os ÁFA kulccsal

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha a rendelés státusza nem 'NYITOTT'

        Example:
            >>> order = OrderService.set_vat_to_local(db, order_id=42)
            >>> print(order.final_vat_rate)
            Decimal('5.00')

        NTAK Szabály:
            - Alapértelmezett ÁFA: 27%
            - Helyi felhasználás ÁFA: 5%
            - Váltás csak NYITOTT rendeléseknél
        """
        # Rendelés lekérdezése
        order = OrderService.get_order(db, order_id)

        # Státusz ellenőrzése - CSAK NYITOTT rendelés módosítható
        if order.status != OrderStatusEnum.NYITOTT.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Az ÁFA kulcs csak NYITOTT státuszú rendeléseknél módosítható. "
                       f"Jelenlegi státusz: {order.status}"
            )

        try:
            # ÁFA kulcs átállítása 5%-ra (NTAK helyi felhasználás)
            order.final_vat_rate = Decimal("5.00")

            # NTAK adatok frissítése (ha van)
            if order.ntak_data is None:
                order.ntak_data = {}

            order.ntak_data["vat_change_reason"] = "Helyi felhasználás (NTAK)"
            order.ntak_data["previous_vat_rate"] = "27.00"
            order.ntak_data["new_vat_rate"] = "5.00"

            db.commit()
            db.refresh(order)

            return order

        except HTTPException:
            # HTTPException-öket tovább dobni
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba az ÁFA kulcs módosítása során: {str(e)}"
            )

    @staticmethod
    def count_orders(
        db: Session,
        order_type: Optional[str] = None,
        status: Optional[str] = None,
        table_id: Optional[int] = None
    ) -> int:
        """
        Rendelések számának lekérdezése szűrési lehetőségekkel.

        Args:
            db: SQLAlchemy session
            order_type: Szűrés rendelés típusra (pl. 'Helyben')
            status: Szűrés státuszra (pl. 'NYITOTT')
            table_id: Szűrés asztal ID-ra

        Returns:
            int: Rendelések száma

        Example:
            >>> count = OrderService.count_orders(db, status='NYITOTT')
            >>> print(f"Nyitott rendelések: {count}")
        """
        query = db.query(Order)

        # Szűrők alkalmazása
        if order_type:
            query = query.filter(Order.order_type == order_type)
        if status:
            query = query.filter(Order.status == status)
        if table_id:
            query = query.filter(Order.table_id == table_id)

        return query.count()
