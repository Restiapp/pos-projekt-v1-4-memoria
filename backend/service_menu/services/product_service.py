"""
Product Service - Business Logic Layer
Module 0: Terméktörzs és Menü

Ez a service kezeli a Product entitáshoz kapcsolódó üzleti logikát.
Tartalmazza az alapvető CRUD műveleteket és a termékekhez kapcsolódó
speciális lekérdezéseket.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.service_menu.models.product import Product
from backend.service_menu.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """
    Service osztály a Product entitás kezeléséhez.

    Ez az osztály tartalmazza az összes üzleti logikát a termékek
    létrehozásához, lekérdezéséhez, frissítéséhez és törléséhez.
    """

    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> Product:
        """
        Új termék létrehozása.

        Args:
            db: SQLAlchemy database session
            product_data: Termék adatok (ProductCreate schema)

        Returns:
            Product: A létrehozott termék objektum

        Raises:
            IntegrityError: Ha a SKU már létezik az adatbázisban
        """
        # Create Product instance from schema
        db_product = Product(
            name=product_data.name,
            description=product_data.description,
            base_price=product_data.base_price,
            category_id=product_data.category_id,
            sku=product_data.sku,
            is_active=product_data.is_active
        )

        try:
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            return db_product
        except IntegrityError as e:
            db.rollback()
            # Re-raise with more context if it's a SKU uniqueness violation
            if 'sku' in str(e.orig):
                raise ValueError(f"A product with SKU '{product_data.sku}' already exists")
            raise

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """
        Termék lekérdezése ID alapján.

        Args:
            db: SQLAlchemy database session
            product_id: Termék egyedi azonosítója

        Returns:
            Optional[Product]: A termék objektum vagy None, ha nem található
        """
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_all_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = True
    ) -> List[Product]:
        """
        Összes termék lekérdezése lapozással.

        Args:
            db: SQLAlchemy database session
            skip: Kihagyandó rekordok száma (pagination offset)
            limit: Maximum visszaadott rekordok száma
            include_inactive: Ha False, csak az aktív termékeket adja vissza

        Returns:
            List[Product]: Termékek listája
        """
        query = db.query(Product)

        # Filter by active status if needed
        if not include_inactive:
            query = query.filter(Product.is_active == True)

        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        product_data: ProductUpdate
    ) -> Optional[Product]:
        """
        Létező termék frissítése.

        Args:
            db: SQLAlchemy database session
            product_id: Frissítendő termék ID-ja
            product_data: Frissítési adatok (ProductUpdate schema)

        Returns:
            Optional[Product]: A frissített termék objektum vagy None, ha nem található

        Raises:
            IntegrityError: Ha a SKU már létezik az adatbázisban
        """
        db_product = ProductService.get_product_by_id(db, product_id)

        if not db_product:
            return None

        # Update only provided fields (exclude_unset=True)
        update_data = product_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_product, field, value)

        try:
            db.commit()
            db.refresh(db_product)
            return db_product
        except IntegrityError as e:
            db.rollback()
            # Re-raise with more context if it's a SKU uniqueness violation
            if 'sku' in str(e.orig):
                raise ValueError(f"A product with SKU '{product_data.sku}' already exists")
            raise

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """
        Termék törlése.

        Args:
            db: SQLAlchemy database session
            product_id: Törlendő termék ID-ja

        Returns:
            bool: True ha sikeres volt a törlés, False ha a termék nem található
        """
        db_product = ProductService.get_product_by_id(db, product_id)

        if not db_product:
            return False

        db.delete(db_product)
        db.commit()
        return True

    # --- Additional Utility Methods ---

    @staticmethod
    def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
        """
        Termék lekérdezése SKU alapján.

        Args:
            db: SQLAlchemy database session
            sku: Stock Keeping Unit (egyedi termék azonosító)

        Returns:
            Optional[Product]: A termék objektum vagy None, ha nem található
        """
        return db.query(Product).filter(Product.sku == sku).first()

    @staticmethod
    def get_active_products(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Csak az aktív termékek lekérdezése.

        Args:
            db: SQLAlchemy database session
            skip: Kihagyandó rekordok száma
            limit: Maximum visszaadott rekordok száma

        Returns:
            List[Product]: Aktív termékek listája
        """
        return db.query(Product)\
            .filter(Product.is_active == True)\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def get_products_by_category(
        db: Session,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[Product]:
        """
        Termékek lekérdezése kategória alapján.

        Args:
            db: SQLAlchemy database session
            category_id: Kategória ID
            skip: Kihagyandó rekordok száma
            limit: Maximum visszaadott rekordok száma
            include_inactive: Ha False, csak az aktív termékeket adja vissza

        Returns:
            List[Product]: Termékek listája a megadott kategóriából
        """
        query = db.query(Product).filter(Product.category_id == category_id)

        if not include_inactive:
            query = query.filter(Product.is_active == True)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_products(db: Session, include_inactive: bool = True) -> int:
        """
        Termékek számának lekérdezése.

        Args:
            db: SQLAlchemy database session
            include_inactive: Ha False, csak az aktív termékeket számolja

        Returns:
            int: Termékek száma
        """
        query = db.query(Product)

        if not include_inactive:
            query = query.filter(Product.is_active == True)

        return query.count()

    @staticmethod
    def soft_delete_product(db: Session, product_id: int) -> Optional[Product]:
        """
        Termék 'soft delete' - inaktívvá teszi a terméket törlés helyett.

        Args:
            db: SQLAlchemy database session
            product_id: Termék ID

        Returns:
            Optional[Product]: A frissített termék vagy None, ha nem található
        """
        db_product = ProductService.get_product_by_id(db, product_id)

        if not db_product:
            return None

        db_product.is_active = False
        db.commit()
        db.refresh(db_product)
        return db_product
