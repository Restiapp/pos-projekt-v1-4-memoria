"""
Allergen Service - Business Logic Layer
Module 0: Terméktörzs és Menü

Ez a modul tartalmazza az allergének kezelésére szolgáló üzleti logikát.
CRUD műveletek megvalósítása az Allergen modellhez.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.service_menu.models import Allergen, Product
from backend.service_menu.schemas import (
    AllergenCreate,
    AllergenUpdate,
    AllergenResponse,
    AllergenListResponse,
)


class AllergenService:
    """
    Allergén kezelő szolgáltatás.

    Felelősségek:
    - Allergének létrehozása, módosítása, törlése
    - Allergének lekérdezése (egyedi, lista)
    - Allergének hozzárendelése termékekhez
    - Adatvalidáció és üzleti logika végrehajtása
    """

    @staticmethod
    def create_allergen(
        db: Session,
        allergen_data: AllergenCreate
    ) -> AllergenResponse:
        """
        Új allergén létrehozása.

        Args:
            db: Database session
            allergen_data: Allergén adatok (AllergenCreate schema)

        Returns:
            AllergenResponse: Létrehozott allergén

        Raises:
            HTTPException:
                - 400 ha már létezik ilyen kódú allergén
        """
        # Ellenőrizzük, hogy nincs-e már ilyen kódú allergén
        existing = db.query(Allergen).filter(
            Allergen.code == allergen_data.code.upper()
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Allergen with code '{allergen_data.code}' already exists"
            )

        # Új allergén létrehozása (code normalizálása nagybetűsre)
        allergen_dict = allergen_data.model_dump()
        allergen_dict['code'] = allergen_dict['code'].upper()
        db_allergen = Allergen(**allergen_dict)

        try:
            db.add(db_allergen)
            db.commit()
            db.refresh(db_allergen)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

        return AllergenResponse.model_validate(db_allergen)

    @staticmethod
    def get_allergen(db: Session, allergen_id: int) -> AllergenResponse:
        """
        Allergén lekérdezése ID alapján.

        Args:
            db: Database session
            allergen_id: Allergén azonosító

        Returns:
            AllergenResponse: Allergén adatok

        Raises:
            HTTPException: 404 ha nem található
        """
        db_allergen = db.query(Allergen).filter(
            Allergen.id == allergen_id
        ).first()

        if not db_allergen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allergen with id {allergen_id} not found"
            )

        return AllergenResponse.model_validate(db_allergen)

    @staticmethod
    def get_allergens(
        db: Session,
        page: int = 1,
        page_size: int = 20
    ) -> AllergenListResponse:
        """
        Allergének lekérdezése lapozással.

        Args:
            db: Database session
            page: Oldalszám (1-től kezdődik)
            page_size: Elemek száma oldalanként (max 100)

        Returns:
            AllergenListResponse: Allergének listája lapozási metaadatokkal
        """
        # Validáljuk a lapozási paramétereket
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        # Lekérdezés
        query = db.query(Allergen).order_by(Allergen.code)

        total = query.count()
        offset = (page - 1) * page_size
        allergens = query.offset(offset).limit(page_size).all()

        # Konvertálás AllergenResponse listára
        allergen_responses = [
            AllergenResponse.model_validate(allergen)
            for allergen in allergens
        ]

        return AllergenListResponse(
            items=allergen_responses,
            total=total,
            page=page,
            page_size=page_size
        )

    @staticmethod
    def update_allergen(
        db: Session,
        allergen_id: int,
        allergen_data: AllergenUpdate
    ) -> AllergenResponse:
        """
        Allergén módosítása.

        Args:
            db: Database session
            allergen_id: Allergén azonosító
            allergen_data: Módosítandó adatok (AllergenUpdate schema)

        Returns:
            AllergenResponse: Módosított allergén

        Raises:
            HTTPException:
                - 404 ha nem található
                - 400 ha a kód már foglalt
        """
        db_allergen = db.query(Allergen).filter(
            Allergen.id == allergen_id
        ).first()

        if not db_allergen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allergen with id {allergen_id} not found"
            )

        # Frissítjük a mezőket (csak azokat, amik nem None)
        update_data = allergen_data.model_dump(exclude_unset=True)

        # Kód normalizálása, ha módosítva van
        if 'code' in update_data:
            new_code = update_data['code'].upper()
            # Ellenőrizzük, hogy nem ütközik-e más allergénnel
            existing = db.query(Allergen).filter(
                Allergen.code == new_code,
                Allergen.id != allergen_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Allergen with code '{new_code}' already exists"
                )
            update_data['code'] = new_code

        for key, value in update_data.items():
            setattr(db_allergen, key, value)

        try:
            db.commit()
            db.refresh(db_allergen)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

        return AllergenResponse.model_validate(db_allergen)

    @staticmethod
    def delete_allergen(db: Session, allergen_id: int) -> None:
        """
        Allergén törlése.

        Args:
            db: Database session
            allergen_id: Allergén azonosító

        Raises:
            HTTPException: 404 ha nem található
        """
        db_allergen = db.query(Allergen).filter(
            Allergen.id == allergen_id
        ).first()

        if not db_allergen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allergen with id {allergen_id} not found"
            )

        try:
            db.delete(db_allergen)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete allergen: {str(e)}"
            )

    @staticmethod
    def assign_allergens_to_product(
        db: Session,
        product_id: int,
        allergen_ids: List[int]
    ) -> List[AllergenResponse]:
        """
        Allergének hozzárendelése termékhez.
        Ez felülírja a meglévő allergéneket!

        Args:
            db: Database session
            product_id: Termék azonosító
            allergen_ids: Allergén azonosítók listája

        Returns:
            List[AllergenResponse]: Hozzárendelt allergének

        Raises:
            HTTPException:
                - 404 ha a termék vagy valamelyik allergén nem található
        """
        # Ellenőrizzük, hogy a termék létezik-e
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )

        # Ellenőrizzük, hogy az összes allergén létezik-e
        allergens = db.query(Allergen).filter(Allergen.id.in_(allergen_ids)).all()
        if len(allergens) != len(allergen_ids):
            found_ids = {a.id for a in allergens}
            missing_ids = set(allergen_ids) - found_ids
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allergens with ids {missing_ids} not found"
            )

        # Töröljük a régi hozzárendeléseket és hozzáadjuk az újakat
        product.allergens = allergens

        try:
            db.commit()
            db.refresh(product)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

        return [AllergenResponse.model_validate(a) for a in product.allergens]
