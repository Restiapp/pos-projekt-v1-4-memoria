"""
Order Service - Business Logic Layer
Module 1: Rendeléskezelés és Asztalok

Ez a service layer felelős a rendelések üzleti logikájáért, beleértve:
- CRUD műveletek (Create, Read, Update, Delete)
- NTAK-kompatibilis ÁFA váltás (27% -> 5%)
- Státusz validáció és átmenetek
- Rendelés lezárás fizetettségi ellenőrzéssel

Fázis 4.3 & 4.4: Order Service és NTAK ÁFA logika
Fázis 4.7: close_order metódus hozzáadva
"""

from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
import httpx
import logging

from backend.service_orders.models.order import Order
from backend.service_orders.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderStatusEnum
)
from backend.service_orders.config import settings

logger = logging.getLogger(__name__)

# Circular import elkerülése: TYPE_CHECKING használata
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.service_orders.services.payment_service import PaymentService


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
                customer_id=order_data.customer_id,
                total_amount=order_data.total_amount,
                final_vat_rate=order_data.final_vat_rate,
                ntak_data=order_data.ntak_data,
                notes=order_data.notes
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
            # ÁFA kulcs átállítása 18%-ra (NTAK helyi felhasználás/catering)
            order.final_vat_rate = Decimal("18.00")

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

    @staticmethod
    def close_order(db: Session, order_id: int) -> Order:
        """
        Rendelés lezárása.

        Ez a funkció lezárja a rendelést, de előtte ellenőrzi,
        hogy a rendelés teljesen ki van-e fizetve. Csak teljesen
        kifizetett rendelések zárhatók le.

        FONTOS: A rendelés lezárása triggerel további műveleteket:
        - NTAK adatszolgáltatás küldése
        - Készlet levonás (inventory deduction)

        Args:
            db: SQLAlchemy session
            order_id: A lezárandó rendelés azonosítója

        Returns:
            Order: A lezárt rendelés

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha a rendelés nincs teljesen kifizetve
            HTTPException 400: Ha a rendelés lezárása sikertelen

        Example:
            >>> closed_order = OrderService.close_order(db, order_id=42)
            >>> print(closed_order.status)
            'LEZART'

        Fázis 4.7: close_order metódus implementálva
        """
        # Rendelés lekérdezése
        order = OrderService.get_order(db, order_id)

        # Circular import elkerülése: lokális import
        from backend.service_orders.services.payment_service import PaymentService

        # Ellenőrizzük, hogy a rendelés teljesen ki van-e fizetve
        if not PaymentService.is_order_fully_paid(db, order_id):
            total_paid = PaymentService.calculate_total_paid(db, order_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A rendelés nem zárható le, mert nincs teljesen kifizetve. "
                       f"Rendelés összege: {order.total_amount} HUF, "
                       f"Befizetett összeg: {total_paid} HUF"
            )

        try:
            # Státusz átállítása LEZART-ra
            order.status = OrderStatusEnum.LEZART.value

            db.commit()
            db.refresh(order)

            # Trigger NTAK adatszolgáltatás küldése (graceful failure)
            try:
                with httpx.Client() as client:
                    ntak_url = f"{settings.admin_service_url}/internal/report-order/{order_id}"
                    client.post(ntak_url, timeout=5.0)
                    logger.info(f"NTAK trigger sent for order {order_id}")
            except Exception as e:
                # Graceful failure: log but don't block order closure
                # V3.0 Fázis 5: Robusztus hibakezelés (minden Exception típus)
                logger.warning(f"Failed to trigger NTAK for order {order_id}: {str(e)}")

            # Trigger inventory deduction (graceful failure)
            # V3.0/F3.A: Real implementation of stock deduction via service_inventory
            try:
                with httpx.Client() as client:
                    inventory_url = f"{settings.inventory_service_url}/api/v1/inventory/internal/deduct-stock"
                    payload = {"order_id": order_id}
                    response = client.post(inventory_url, json=payload, timeout=5.0)
                    logger.info(f"Inventory deduction triggered for order {order_id}: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(
                            f"Stock deduction result: {result.get('items_processed', 0)} items processed, "
                            f"{len(result.get('ingredients_deducted', []))} ingredients deducted"
                        )
            except Exception as e:
                # Graceful failure: log but don't block order closure
                # V3.0 Fázis 5: Robusztus hibakezelés (minden Exception típus)
                # Catches all possible errors: httpx.HTTPError, DNS, JSON, Timeout, Connection, etc.
                logger.warning(f"Failed to trigger inventory deduction for order {order_id}: {str(e)}")

            return order

        except HTTPException:
            # HTTPException-öket tovább dobni
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a rendelés lezárása során: {str(e)}"
            )

    @staticmethod
    def change_order_type(
        db: Session,
        order_id: int,
        new_order_type: str,
        reason: Optional[str] = None,
        customer_address: Optional[str] = None,
        customer_zip_code: Optional[str] = None
    ) -> tuple[Order, str]:
        """
        Rendelés típusának megváltoztatása (Átültetés).

        Ez a funkció lehetővé teszi a rendelés típusának módosítását
        (pl. Helyben -> Elvitel, Helyben -> Kiszállítás, stb.).

        FONTOS: A típusváltás csak NYITOTT státuszú rendeléseknél engedélyezett!

        V3.0 / Fázis 3.B: Átültetés (Order Type Change) funkció

        Args:
            db: SQLAlchemy session
            order_id: A rendelés azonosítója
            new_order_type: Az új rendelés típus (OrderTypeEnum értéke)
            reason: Opcionális indoklás a változtatáshoz
            customer_address: Opcionális ügyfél cím (Kiszállítás típusnál)
            customer_zip_code: Opcionális ZIP kód (Kiszállítás típusnál)

        Returns:
            tuple[Order, str]: A módosított rendelés és az előző típus

        Raises:
            HTTPException 404: Ha a rendelés nem található
            HTTPException 400: Ha a rendelés státusza nem 'NYITOTT'
            HTTPException 400: Ha a típusváltás sikertelen

        Example:
            >>> order, prev_type = OrderService.change_order_type(
            ...     db,
            ...     order_id=42,
            ...     new_order_type="Kiszállítás",
            ...     reason="Vevő kérésére",
            ...     customer_zip_code="1051"
            ... )
            >>> print(f"Típusváltás: {prev_type} -> {order.order_type}")

        V3.0 / Phase 3.B: Real HTTP calls to service_logistics (ZIP code based).
        """
        # Rendelés lekérdezése
        order = OrderService.get_order(db, order_id)

        # Státusz ellenőrzése - CSAK NYITOTT rendelés típusa módosítható
        if order.status != OrderStatusEnum.NYITOTT.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A rendelés típusa csak NYITOTT státuszú rendeléseknél módosítható. "
                       f"Jelenlegi státusz: {order.status}"
            )

        # Előző típus mentése
        previous_order_type = order.order_type

        # Ellenőrzés: ha az új típus megegyezik a jelenlegi típussal
        if previous_order_type == new_order_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A rendelés típusa már '{new_order_type}'. Nincs szükség változtatásra."
            )

        # V3.0 Fázis 4.C: Ital/Fagyi ellenőrzés (service_menu HTTP hívás)
        # Ellenőrizni kell, hogy a rendelés tartalmaz-e Ital vagy Fagyi kategóriájú terméket
        # V3.0 terv 4.4-es szabály: Ital/Fagyi kategóriájú termékek esetén tilos az átültetés
        try:
            # Order items lekérdezése
            from backend.service_orders.models.order_item import OrderItem
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

            # Minden termék kategóriájának ellenőrzése
            for item in order_items:
                product_id = item.product_id

                # HTTP GET hívás a service_menu felé: termék lekérdezése
                with httpx.Client() as client:
                    product_url = f"{settings.menu_service_url}/api/menu/products/{product_id}"
                    product_response = client.get(product_url, timeout=5.0)

                    if product_response.status_code == 200:
                        product_data = product_response.json()
                        category_id = product_data.get("category_id")

                        if category_id:
                            # HTTP GET hívás a service_menu felé: kategória lekérdezése
                            category_url = f"{settings.menu_service_url}/api/menu/categories/{category_id}"
                            category_response = client.get(category_url, timeout=5.0)

                            if category_response.status_code == 200:
                                category_data = category_response.json()
                                category_name = category_data.get("name")

                                # V3.0 terv 4.4-es szabály: Ital/Fagyi kategória tiltása
                                if category_name in ["Ital", "Fagyi"]:
                                    raise HTTPException(
                                        status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"A rendelés típusa nem módosítható, mert tartalmaz '{category_name}' kategóriájú terméket. "
                                               f"Az Ital és Fagyi kategóriájú termékek esetén tilos az átültetés."
                                    )
                            else:
                                logger.warning(
                                    f"Failed to fetch category {category_id} from service_menu: HTTP {category_response.status_code}"
                                )
                    else:
                        logger.warning(
                            f"Failed to fetch product {product_id} from service_menu: HTTP {product_response.status_code}"
                        )
        except HTTPException:
            # HTTPException-öket tovább dobni (pl. Ital/Fagyi tiltás)
            raise
        except httpx.HTTPError as e:
            # Graceful failure: log but don't block order type change
            # Alternatíva: strict failure (raise HTTPException 503)
            logger.warning(f"Failed to check product categories for order {order_id}: {str(e)}")

        try:
            # V3.0 Fázis 2.C: MOCK HTTP hívás a service_inventory felé
            # (Készlet kezelés értesítése a típusváltásról)
            # TODO (Fázis 3): Valós HTTP hívásra cserélni
            try:
                logger.info(
                    f"[MOCK] Sending order type change notification to service_inventory: "
                    f"order_id={order_id}, previous_type={previous_order_type}, "
                    f"new_type={new_order_type}"
                )
                # MOCK: A valós implementációban itt lenne egy HTTP POST hívás:
                # with httpx.Client() as client:
                #     inventory_url = f"{settings.inventory_service_url}/internal/notify-order-type-change"
                #     payload = {
                #         "order_id": order_id,
                #         "previous_type": previous_order_type,
                #         "new_type": new_order_type
                #     }
                #     client.post(inventory_url, json=payload, timeout=5.0)
                logger.info(f"[MOCK] Inventory notification would be sent (not implemented yet)")
            except Exception as e:
                # Graceful failure: log but don't block order type change
                logger.warning(f"[MOCK] Failed to notify inventory service for order {order_id}: {str(e)}")

            # V3.0 Fázis 3.B: REAL HTTP hívás a service_logistics felé
            # (Szállítási zóna ellenőrzése, ha releváns)
            if new_order_type == "Kiszállítás":
                try:
                    # Ellenőrizzük, hogy van-e ZIP kód vagy cím
                    if customer_zip_code:
                        logger.info(
                            f"Checking delivery zone for order {order_id} with ZIP code: {customer_zip_code}"
                        )
                        # Valós HTTP POST hívás a service_logistics felé (ZIP kód alapú keresés)
                        with httpx.Client() as client:
                            logistics_url = f"{settings.logistics_service_url}/zones/get-by-zip-code"
                            payload = {"zip_code": customer_zip_code}
                            response = client.post(logistics_url, json=payload, timeout=5.0)

                            if response.status_code == 200:
                                zone_data = response.json()
                                if zone_data.get("zone"):
                                    logger.info(
                                        f"Delivery zone found for order {order_id}: {zone_data['zone']['zone_name']}"
                                    )
                                else:
                                    logger.warning(
                                        f"No delivery zone found for ZIP code {customer_zip_code} for order {order_id}"
                                    )
                            else:
                                logger.warning(
                                    f"Failed to check delivery zone for order {order_id}: HTTP {response.status_code}"
                                )
                    else:
                        logger.warning(
                            f"Order {order_id} changed to Kiszállítás but no ZIP code provided"
                        )
                except httpx.HTTPError as e:
                    # Graceful failure: log but don't block order type change
                    logger.warning(f"Failed to check logistics zone for order {order_id}: {str(e)}")

            # Rendelés típusának módosítása
            order.order_type = new_order_type

            # NTAK adatok frissítése (audit trail)
            if order.ntak_data is None:
                order.ntak_data = {}

            order.ntak_data["order_type_change"] = {
                "previous_type": previous_order_type,
                "new_type": new_order_type,
                "reason": reason or "Nincs megadva",
                "changed_at": datetime.now().isoformat()
            }

            # Notes mező frissítése (ha van reason)
            if reason:
                current_notes = order.notes or ""
                order.notes = f"{current_notes}\n[Átültetés] {previous_order_type} -> {new_order_type}: {reason}".strip()

            db.commit()
            db.refresh(order)

            logger.info(
                f"Order type changed successfully: order_id={order_id}, "
                f"{previous_order_type} -> {new_order_type}"
            )

            return order, previous_order_type

        except HTTPException:
            # HTTPException-öket tovább dobni
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hiba a rendelés típusának módosítása során: {str(e)}"
            )
