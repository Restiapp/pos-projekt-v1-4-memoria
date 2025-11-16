"""
Category Service - Business Logic Layer
Module 0: Terméktörzs és Menü

Ez a modul tartalmazza a kategóriák kezelésére szolgáló üzleti logikát.
CRUD műveletek megvalósítása a Category modellhez.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.service_menu.models import Category
from backend.service_menu.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)


class CategoryService:
    """
    Kategória kezelő szolgáltatás.

    Felelősségek:
    - Kategóriák létrehozása, módosítása, törlése
    - Kategóriák lekérdezése (egyedi, lista, hierarchikus)
    - Adatvalidáció és üzleti logika végrehajtása
    """

    @staticmethod
    def create_category(
        db: Session,
        category_data: CategoryCreate
    ) -> CategoryResponse:
        """
        Új kategória létrehozása.

        Args:
            db: Database session
            category_data: Kategória adatok (CategoryCreate schema)

        Returns:
            CategoryResponse: Létrehozott kategória

        Raises:
            HTTPException:
                - 404 ha a parent_id nem létezik
                - 400 ha már létezik ilyen nevű kategória ugyanazon parent alatt
        """
        # Ellenőrizzük, hogy a parent_id létezik-e (ha van megadva)
        if category_data.parent_id is not None:
            parent = db.query(Category).filter(
                Category.id == category_data.parent_id
            ).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category with id {category_data.parent_id} not found"
                )

        # Ellenőrizzük, hogy nincs-e már ilyen nevű kategória ugyanazzal a parent_id-val
        existing = db.query(Category).filter(
            Category.name == category_data.name,
            Category.parent_id == category_data.parent_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_data.name}' already exists under the same parent"
            )

        # Új kategória létrehozása
        db_category = Category(**category_data.model_dump())

        try:
            db.add(db_category)
            db.commit()
            db.refresh(db_category)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

        return CategoryResponse.model_validate(db_category)

    @staticmethod
    def get_category(db: Session, category_id: int) -> CategoryResponse:
        """
        Kategória lekérdezése ID alapján.

        Args:
            db: Database session
            category_id: Kategória azonosító

        Returns:
            CategoryResponse: Kategória adatok

        Raises:
            HTTPException: 404 ha a kategória nem található
        """
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )

        return CategoryResponse.model_validate(category)

    @staticmethod
    def get_categories(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[int] = None
    ) -> CategoryListResponse:
        """
        Kategóriák listázása lapozással és szűréssel.

        Args:
            db: Database session
            skip: Kihagyott elemek száma (pagination offset)
            limit: Max visszaadott elemek száma (pagination limit)
            parent_id: Szűrés parent_id alapján (None = összes, 0 = csak root kategóriák)

        Returns:
            CategoryListResponse: Kategória lista lapozási információkkal
        """
        query = db.query(Category)

        # Szűrés parent_id alapján
        if parent_id is not None:
            if parent_id == 0:
                # Root kategóriák (nincs szülő)
                query = query.filter(Category.parent_id.is_(None))
            else:
                # Adott parent alatt lévő kategóriák
                query = query.filter(Category.parent_id == parent_id)

        # Összes elem száma a szűrés után
        total = query.count()

        # Lapozás
        categories = query.offset(skip).limit(limit).all()

        # Response összeállítása
        return CategoryListResponse(
            items=[CategoryResponse.model_validate(cat) for cat in categories],
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            page_size=limit
        )

    @staticmethod
    def update_category(
        db: Session,
        category_id: int,
        category_data: CategoryUpdate
    ) -> CategoryResponse:
        """
        Kategória módosítása.

        Args:
            db: Database session
            category_id: Kategória azonosító
            category_data: Módosítandó adatok (CategoryUpdate schema)

        Returns:
            CategoryResponse: Módosított kategória

        Raises:
            HTTPException:
                - 404 ha a kategória nem található
                - 404 ha a parent_id nem létezik
                - 400 ha ciklikus hivatkozást eredményezne
                - 400 ha a név már foglalt ugyanazon parent alatt
        """
        # Kategória lekérdezése
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )

        # Csak azokat a mezőket frissítjük, amelyek meg vannak adva
        update_data = category_data.model_dump(exclude_unset=True)

        # Ellenőrizzük a parent_id-t (ha változik)
        if 'parent_id' in update_data:
            new_parent_id = update_data['parent_id']

            # Ellenőrizzük, hogy a parent létezik-e
            if new_parent_id is not None:
                parent = db.query(Category).filter(
                    Category.id == new_parent_id
                ).first()

                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Parent category with id {new_parent_id} not found"
                    )

                # Ellenőrizzük, hogy nem ciklikus-e a hivatkozás
                # (egy kategória nem lehet saját maga szülője vagy leszármazottja)
                if CategoryService._is_circular_reference(db, category_id, new_parent_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Circular reference detected: a category cannot be its own ancestor"
                    )

        # Ellenőrizzük a név egyediségét (ha változik)
        if 'name' in update_data:
            new_name = update_data['name']
            check_parent_id = update_data.get('parent_id', category.parent_id)

            existing = db.query(Category).filter(
                Category.name == new_name,
                Category.parent_id == check_parent_id,
                Category.id != category_id  # Kivéve önmaga
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with name '{new_name}' already exists under the same parent"
                )

        # Módosítások alkalmazása
        for field, value in update_data.items():
            setattr(category, field, value)

        try:
            db.commit()
            db.refresh(category)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

        return CategoryResponse.model_validate(category)

    @staticmethod
    def delete_category(db: Session, category_id: int, force: bool = False) -> dict:
        """
        Kategória törlése.

        Args:
            db: Database session
            category_id: Kategória azonosító
            force: Ha True, akkor a kapcsolódó elemeket is törli (cascade)

        Returns:
            dict: Törlés megerősítése

        Raises:
            HTTPException:
                - 404 ha a kategória nem található
                - 400 ha vannak kapcsolódó termékek vagy alkategóriák és force=False
        """
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )

        # Ellenőrizzük, hogy vannak-e alkategóriák
        subcategories_count = db.query(Category).filter(
            Category.parent_id == category_id
        ).count()

        if subcategories_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category has {subcategories_count} subcategories. Use force=True to delete."
            )

        # Ellenőrizzük, hogy vannak-e kapcsolódó termékek
        products_count = len(category.products) if category.products else 0

        if products_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category has {products_count} associated products. Use force=True to delete."
            )

        # Ha force=True, először töröljük az alkategóriákat és termékeket
        if force:
            # Alkategóriák rekurzív törlése
            subcategories = db.query(Category).filter(
                Category.parent_id == category_id
            ).all()
            for subcat in subcategories:
                CategoryService.delete_category(db, subcat.id, force=True)

            # Termékek parent_id-jának nullázása vagy törlése
            # (itt feltételezzük, hogy NULL-ra állítjuk)
            for product in category.products:
                product.category_id = None

        # Kategória törlése
        try:
            db.delete(category)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category: {str(e)}"
            )

        return {
            "message": f"Category {category_id} deleted successfully",
            "deleted_id": category_id
        }

    @staticmethod
    def _is_circular_reference(db: Session, category_id: int, new_parent_id: int) -> bool:
        """
        Ellenőrzi, hogy ciklikus hivatkozást eredményezne-e a parent_id változtatása.

        Args:
            db: Database session
            category_id: Az aktuális kategória ID-ja
            new_parent_id: Az új parent kategória ID-ja

        Returns:
            bool: True ha ciklikus hivatkozás lenne, különben False
        """
        # Ha önmagának állítjuk be parent-nek
        if category_id == new_parent_id:
            return True

        # Felfelé haladva a hierarchiában ellenőrizzük
        current_parent_id = new_parent_id
        visited = set()

        while current_parent_id is not None:
            if current_parent_id in visited:
                # Végtelen ciklus az adatbázisban
                return True

            if current_parent_id == category_id:
                # Az új parent valamelyik őse az aktuális kategória
                return True

            visited.add(current_parent_id)

            parent = db.query(Category).filter(
                Category.id == current_parent_id
            ).first()

            if not parent:
                break

            current_parent_id = parent.parent_id

        return False

    @staticmethod
    def get_category_tree(db: Session, root_id: Optional[int] = None) -> List[dict]:
        """
        Kategória fa hierarchia lekérdezése.

        Args:
            db: Database session
            root_id: Gyökér kategória ID (None = összes root kategória)

        Returns:
            List[dict]: Hierarchikus kategória struktúra
        """
        def build_tree(parent_id: Optional[int]) -> List[dict]:
            """Rekurzív fa építés."""
            query = db.query(Category)

            if parent_id is None:
                query = query.filter(Category.parent_id.is_(None))
            else:
                query = query.filter(Category.parent_id == parent_id)

            categories = query.all()
            result = []

            for category in categories:
                cat_dict = CategoryResponse.model_validate(category).model_dump()
                cat_dict['children'] = build_tree(category.id)
                result.append(cat_dict)

            return result

        return build_tree(root_id)
