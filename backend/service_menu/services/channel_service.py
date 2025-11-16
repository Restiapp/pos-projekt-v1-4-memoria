"""
Channel Service - Business Logic Layer
Module 0: Terméktörzs és Menü

Ez a service kezeli az értékesítési csatornák specifikus üzleti logikáját,
beleértve a csatorna láthatóság kezelését és a csatorna-specifikus árképzést.
"""

from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.service_menu.models.channel_visibility import ChannelVisibility
from backend.service_menu.models.product import Product


class ChannelService:
    """
    Service osztály az értékesítési csatornák kezeléséhez.

    Ez az osztály tartalmazza az összes üzleti logikát a csatorna láthatóság
    beállításához és a csatorna-specifikus árak lekérdezéséhez.
    """

    @staticmethod
    def set_channel_visibility(
        db: Session,
        product_id: int,
        channel_name: str,
        is_visible: bool = True,
        price_override: Optional[Decimal] = None
    ) -> ChannelVisibility:
        """
        Beállítja vagy frissíti egy termék láthatóságát egy adott értékesítési csatornán.

        Ha már létezik a csatorna-termék kombináció, frissíti azt.
        Ha nem létezik, létrehozza.

        Args:
            db: SQLAlchemy database session
            product_id: Termék egyedi azonosítója
            channel_name: Értékesítési csatorna neve (pl. 'Pult', 'Kiszállítás', 'Helybeni')
            is_visible: A termék látható-e az adott csatornán (default: True)
            price_override: Opcionális csatorna-specifikus ár (ha eltér az alap ártól)

        Returns:
            ChannelVisibility: A létrehozott vagy frissített csatorna láthatósági objektum

        Raises:
            ValueError: Ha a termék nem létezik
            IntegrityError: Ha adatbázis integritási hiba történik
        """
        # Ellenőrizzük, hogy a termék létezik-e
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

        # Keressük meg, hogy létezik-e már csatorna láthatósági beállítás
        channel_visibility = db.query(ChannelVisibility).filter(
            ChannelVisibility.product_id == product_id,
            ChannelVisibility.channel_name == channel_name
        ).first()

        try:
            if channel_visibility:
                # Frissítjük a meglévő bejegyzést
                channel_visibility.is_visible = is_visible
                channel_visibility.price_override = price_override
            else:
                # Új bejegyzést hozunk létre
                channel_visibility = ChannelVisibility(
                    product_id=product_id,
                    channel_name=channel_name,
                    is_visible=is_visible,
                    price_override=price_override
                )
                db.add(channel_visibility)

            db.commit()
            db.refresh(channel_visibility)
            return channel_visibility

        except IntegrityError as e:
            db.rollback()
            raise IntegrityError(
                f"Database integrity error while setting channel visibility: {str(e)}",
                params=None,
                orig=e.orig
            )

    @staticmethod
    def get_product_price_for_channel(
        db: Session,
        product_id: int,
        channel_name: str
    ) -> Optional[Decimal]:
        """
        Lekéri egy termék árát egy adott értékesítési csatornán.

        Ha a csatornán van ár felülírás (price_override), azt adja vissza.
        Ha nincs felülírás vagy nincs csatorna beállítás, a termék alap árát adja vissza.
        Ha a termék nem látható az adott csatornán, None-t ad vissza.

        Args:
            db: SQLAlchemy database session
            product_id: Termék egyedi azonosítója
            channel_name: Értékesítési csatorna neve

        Returns:
            Optional[Decimal]: A termék ára az adott csatornán, vagy None ha nem látható

        Raises:
            ValueError: Ha a termék nem létezik
        """
        # Ellenőrizzük, hogy a termék létezik-e
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

        # Keressük meg a csatorna láthatósági beállítást
        channel_visibility = db.query(ChannelVisibility).filter(
            ChannelVisibility.product_id == product_id,
            ChannelVisibility.channel_name == channel_name
        ).first()

        # Ha nincs beállítás, a termék alapértelmezés szerint látható és az alap ár érvényes
        if not channel_visibility:
            return product.base_price

        # Ha a termék nem látható az adott csatornán, None-t adunk vissza
        if not channel_visibility.is_visible:
            return None

        # Ha van ár felülírás, azt adjuk vissza, egyébként az alap árat
        if channel_visibility.price_override is not None:
            return channel_visibility.price_override
        else:
            return product.base_price

    @staticmethod
    def get_channel_visibility(
        db: Session,
        product_id: int,
        channel_name: str
    ) -> Optional[ChannelVisibility]:
        """
        Lekéri egy termék csatorna láthatósági beállítását.

        Args:
            db: SQLAlchemy database session
            product_id: Termék egyedi azonosítója
            channel_name: Értékesítési csatorna neve

        Returns:
            Optional[ChannelVisibility]: A csatorna láthatósági objektum vagy None
        """
        return db.query(ChannelVisibility).filter(
            ChannelVisibility.product_id == product_id,
            ChannelVisibility.channel_name == channel_name
        ).first()

    @staticmethod
    def delete_channel_visibility(
        db: Session,
        product_id: int,
        channel_name: str
    ) -> bool:
        """
        Törli egy termék csatorna láthatósági beállítását.

        Args:
            db: SQLAlchemy database session
            product_id: Termék egyedi azonosítója
            channel_name: Értékesítési csatorna neve

        Returns:
            bool: True ha sikeres volt a törlés, False ha nem található a beállítás
        """
        channel_visibility = ChannelService.get_channel_visibility(
            db, product_id, channel_name
        )

        if not channel_visibility:
            return False

        db.delete(channel_visibility)
        db.commit()
        return True
