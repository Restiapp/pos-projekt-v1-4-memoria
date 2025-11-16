"""
Modifier Service - Business Logic Layer
Module 0: Terméktörzs és Menü

Ez a service kezeli a ModifierGroup és Modifier entitásokkal kapcsolatos
üzleti logikát, CRUD műveleteket és a termékekkel való asszociációkat.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.service_menu.models import (
    ModifierGroup,
    Modifier,
    Product,
    product_modifier_group_associations
)
from backend.service_menu.schemas.modifier import (
    ModifierGroupCreate,
    ModifierGroupUpdate,
    ModifierCreate,
    ModifierUpdate,
    ModifierGroupResponse,
    ModifierResponse,
    ModifierGroupWithModifiers,
)


class ModifierServiceError(Exception):
    """Base exception for ModifierService errors."""
    pass


class ModifierGroupNotFoundError(ModifierServiceError):
    """Raised when a modifier group is not found."""
    pass


class ModifierNotFoundError(ModifierServiceError):
    """Raised when a modifier is not found."""
    pass


class ProductNotFoundError(ModifierServiceError):
    """Raised when a product is not found."""
    pass


class ModifierService:
    """
    Service osztály a Modifier és ModifierGroup entitások kezeléséhez.

    Ez a service osztály felelős:
    - ModifierGroup létrehozásáért, lekérdezéséért, módosításáért, törléséért
    - Modifier létrehozásáért, lekérdezéséért, módosításáért, törléséért
    - ModifierGroup és Product közötti asszociációk kezeléséért

    Minden metódus Session paramétert vár, amely FastAPI Depends-en keresztül
    injektálható (get_db_connection).
    """

    # ============================================================================
    # ModifierGroup CRUD Operations
    # ============================================================================

    @staticmethod
    def create_modifier_group(
        db: Session,
        modifier_group_data: ModifierGroupCreate
    ) -> ModifierGroupResponse:
        """
        Új ModifierGroup létrehozása.

        Args:
            db: SQLAlchemy session
            modifier_group_data: ModifierGroup adatok (Pydantic schema)

        Returns:
            ModifierGroupResponse: Létrehozott modifier group

        Raises:
            ModifierServiceError: Adatbázis hiba esetén

        Example:
            group_data = ModifierGroupCreate(
                name="Zsemle típusa",
                selection_type=SelectionType.SINGLE_CHOICE_REQUIRED,
                min_selection=1,
                max_selection=1
            )
            group = ModifierService.create_modifier_group(db, group_data)
        """
        try:
            new_group = ModifierGroup(**modifier_group_data.model_dump())
            db.add(new_group)
            db.commit()
            db.refresh(new_group)
            return ModifierGroupResponse.model_validate(new_group)
        except SQLAlchemyError as e:
            db.rollback()
            raise ModifierServiceError(f"Failed to create modifier group: {str(e)}")

    @staticmethod
    def get_modifier_group_by_id(
        db: Session,
        group_id: int,
        include_modifiers: bool = False
    ) -> ModifierGroupResponse | ModifierGroupWithModifiers:
        """
        ModifierGroup lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            group_id: Modifier group azonosító
            include_modifiers: Ha True, betölti a group összes modifier-ét is

        Returns:
            ModifierGroupResponse vagy ModifierGroupWithModifiers

        Raises:
            ModifierGroupNotFoundError: Ha nem található a group

        Example:
            # Alap lekérdezés
            group = ModifierService.get_modifier_group_by_id(db, 1)

            # Modifierekkel együtt
            group = ModifierService.get_modifier_group_by_id(db, 1, include_modifiers=True)
        """
        query = db.query(ModifierGroup)

        if include_modifiers:
            query = query.options(joinedload(ModifierGroup.modifiers))

        group = query.filter(ModifierGroup.id == group_id).first()

        if not group:
            raise ModifierGroupNotFoundError(f"ModifierGroup with id {group_id} not found")

        if include_modifiers:
            return ModifierGroupWithModifiers.model_validate(group)
        return ModifierGroupResponse.model_validate(group)

    @staticmethod
    def get_all_modifier_groups(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        include_modifiers: bool = False
    ) -> List[ModifierGroupResponse | ModifierGroupWithModifiers]:
        """
        Összes ModifierGroup lekérdezése.

        Args:
            db: SQLAlchemy session
            skip: Kihagyandó elemek száma (pagination)
            limit: Maximum visszaadott elemek száma
            include_modifiers: Ha True, betölti minden group összes modifier-ét

        Returns:
            Lista a modifier group-okkal

        Example:
            # Első 50 group
            groups = ModifierService.get_all_modifier_groups(db, skip=0, limit=50)

            # Modifierekkel együtt
            groups = ModifierService.get_all_modifier_groups(
                db,
                include_modifiers=True
            )
        """
        query = db.query(ModifierGroup)

        if include_modifiers:
            query = query.options(joinedload(ModifierGroup.modifiers))

        groups = query.offset(skip).limit(limit).all()

        if include_modifiers:
            return [ModifierGroupWithModifiers.model_validate(g) for g in groups]
        return [ModifierGroupResponse.model_validate(g) for g in groups]

    @staticmethod
    def update_modifier_group(
        db: Session,
        group_id: int,
        update_data: ModifierGroupUpdate
    ) -> ModifierGroupResponse:
        """
        ModifierGroup módosítása.

        Args:
            db: SQLAlchemy session
            group_id: Modifier group azonosító
            update_data: Módosítandó adatok

        Returns:
            ModifierGroupResponse: Frissített modifier group

        Raises:
            ModifierGroupNotFoundError: Ha nem található a group
            ModifierServiceError: Adatbázis hiba esetén

        Example:
            update_data = ModifierGroupUpdate(
                name="Frissített név",
                max_selection=3
            )
            group = ModifierService.update_modifier_group(db, 1, update_data)
        """
        try:
            group = db.query(ModifierGroup).filter(
                ModifierGroup.id == group_id
            ).first()

            if not group:
                raise ModifierGroupNotFoundError(
                    f"ModifierGroup with id {group_id} not found"
                )

            # Csak a megadott mezőket frissítjük
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(group, field, value)

            db.commit()
            db.refresh(group)
            return ModifierGroupResponse.model_validate(group)
        except SQLAlchemyError as e:
            db.rollback()
            raise ModifierServiceError(f"Failed to update modifier group: {str(e)}")

    @staticmethod
    def delete_modifier_group(db: Session, group_id: int) -> bool:
        """
        ModifierGroup törlése.

        Args:
            db: SQLAlchemy session
            group_id: Modifier group azonosító

        Returns:
            bool: True, ha sikeres a törlés

        Raises:
            ModifierGroupNotFoundError: Ha nem található a group
            ModifierServiceError: Adatbázis hiba esetén

        Note:
            A cascade beállítások miatt törli az összes kapcsolódó Modifier-t is.

        Example:
            success = ModifierService.delete_modifier_group(db, 1)
        """
        try:
            group = db.query(ModifierGroup).filter(
                ModifierGroup.id == group_id
            ).first()

            if not group:
                raise ModifierGroupNotFoundError(
                    f"ModifierGroup with id {group_id} not found"
                )

            db.delete(group)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise ModifierServiceError(f"Failed to delete modifier group: {str(e)}")

    # ============================================================================
    # Modifier CRUD Operations
    # ============================================================================

    @staticmethod
    def create_modifier(
        db: Session,
        modifier_data: ModifierCreate
    ) -> ModifierResponse:
        """
        Új Modifier létrehozása.

        Args:
            db: SQLAlchemy session
            modifier_data: Modifier adatok (Pydantic schema)

        Returns:
            ModifierResponse: Létrehozott modifier

        Raises:
            ModifierGroupNotFoundError: Ha nem található a parent group
            ModifierServiceError: Adatbázis hiba esetén

        Example:
            modifier_data = ModifierCreate(
                group_id=1,
                name="Szezámos zsemle",
                price_modifier=0.00,
                is_default=True
            )
            modifier = ModifierService.create_modifier(db, modifier_data)
        """
        try:
            # Ellenőrizzük, hogy létezik-e a parent group
            group_exists = db.query(ModifierGroup).filter(
                ModifierGroup.id == modifier_data.group_id
            ).first()

            if not group_exists:
                raise ModifierGroupNotFoundError(
                    f"ModifierGroup with id {modifier_data.group_id} not found"
                )

            new_modifier = Modifier(**modifier_data.model_dump())
            db.add(new_modifier)
            db.commit()
            db.refresh(new_modifier)
            return ModifierResponse.model_validate(new_modifier)
        except ModifierGroupNotFoundError:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise ModifierServiceError(f"Failed to create modifier: {str(e)}")

    @staticmethod
    def get_modifier_by_id(db: Session, modifier_id: int) -> ModifierResponse:
        """
        Modifier lekérdezése ID alapján.

        Args:
            db: SQLAlchemy session
            modifier_id: Modifier azonosító

        Returns:
            ModifierResponse: A keresett modifier

        Raises:
            ModifierNotFoundError: Ha nem található a modifier

        Example:
            modifier = ModifierService.get_modifier_by_id(db, 1)
        """
        modifier = db.query(Modifier).filter(Modifier.id == modifier_id).first()

        if not modifier:
            raise ModifierNotFoundError(f"Modifier with id {modifier_id} not found")

        return ModifierResponse.model_validate(modifier)

    @staticmethod
    def get_modifiers_by_group(
        db: Session,
        group_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModifierResponse]:
        """
        Egy adott ModifierGroup összes Modifier-ének lekérdezése.

        Args:
            db: SQLAlchemy session
            group_id: Modifier group azonosító
            skip: Kihagyandó elemek száma
            limit: Maximum visszaadott elemek száma

        Returns:
            Lista a modifierekkel

        Raises:
            ModifierGroupNotFoundError: Ha nem található a group

        Example:
            modifiers = ModifierService.get_modifiers_by_group(db, group_id=1)
        """
        # Ellenőrizzük, hogy létezik-e a group
        group_exists = db.query(ModifierGroup).filter(
            ModifierGroup.id == group_id
        ).first()

        if not group_exists:
            raise ModifierGroupNotFoundError(
                f"ModifierGroup with id {group_id} not found"
            )

        modifiers = db.query(Modifier).filter(
            Modifier.group_id == group_id
        ).offset(skip).limit(limit).all()

        return [ModifierResponse.model_validate(m) for m in modifiers]

    @staticmethod
    def update_modifier(
        db: Session,
        modifier_id: int,
        update_data: ModifierUpdate
    ) -> ModifierResponse:
        """
        Modifier módosítása.

        Args:
            db: SQLAlchemy session
            modifier_id: Modifier azonosító
            update_data: Módosítandó adatok

        Returns:
            ModifierResponse: Frissített modifier

        Raises:
            ModifierNotFoundError: Ha nem található a modifier
            ModifierGroupNotFoundError: Ha új group_id-t adunk meg és az nem létezik
            ModifierServiceError: Adatbázis hiba esetén

        Example:
            update_data = ModifierUpdate(
                name="Extra sajt (dupla)",
                price_modifier=300.00
            )
            modifier = ModifierService.update_modifier(db, 1, update_data)
        """
        try:
            modifier = db.query(Modifier).filter(
                Modifier.id == modifier_id
            ).first()

            if not modifier:
                raise ModifierNotFoundError(f"Modifier with id {modifier_id} not found")

            # Ha új group_id-t adunk meg, ellenőrizzük annak létezését
            update_dict = update_data.model_dump(exclude_unset=True)
            if 'group_id' in update_dict:
                group_exists = db.query(ModifierGroup).filter(
                    ModifierGroup.id == update_dict['group_id']
                ).first()

                if not group_exists:
                    raise ModifierGroupNotFoundError(
                        f"ModifierGroup with id {update_dict['group_id']} not found"
                    )

            # Frissítjük a mezőket
            for field, value in update_dict.items():
                setattr(modifier, field, value)

            db.commit()
            db.refresh(modifier)
            return ModifierResponse.model_validate(modifier)
        except (ModifierNotFoundError, ModifierGroupNotFoundError):
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise ModifierServiceError(f"Failed to update modifier: {str(e)}")

    @staticmethod
    def delete_modifier(db: Session, modifier_id: int) -> bool:
        """
        Modifier törlése.

        Args:
            db: SQLAlchemy session
            modifier_id: Modifier azonosító

        Returns:
            bool: True, ha sikeres a törlés

        Raises:
            ModifierNotFoundError: Ha nem található a modifier
            ModifierServiceError: Adatbázis hiba esetén

        Example:
            success = ModifierService.delete_modifier(db, 1)
        """
        try:
            modifier = db.query(Modifier).filter(
                Modifier.id == modifier_id
            ).first()

            if not modifier:
                raise ModifierNotFoundError(f"Modifier with id {modifier_id} not found")

            db.delete(modifier)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise ModifierServiceError(f"Failed to delete modifier: {str(e)}")

    # ============================================================================
    # Product-ModifierGroup Association Operations
    # ============================================================================

    @staticmethod
    def associate_modifier_group_to_product(
        db: Session,
        product_id: int,
        group_id: int
    ) -> bool:
        """
        ModifierGroup hozzárendelése egy Product-hoz.

        Args:
            db: SQLAlchemy session
            product_id: Termék azonosító
            group_id: ModifierGroup azonosító

        Returns:
            bool: True, ha sikeres az asszociáció

        Raises:
            ProductNotFoundError: Ha nem található a termék
            ModifierGroupNotFoundError: Ha nem található a modifier group
            ModifierServiceError: Ha már létezik az asszociáció vagy adatbázis hiba

        Example:
            # "Hamburger" termékhez hozzárendeljük a "Zsemle típusa" csoportot
            ModifierService.associate_modifier_group_to_product(
                db,
                product_id=1,
                group_id=1
            )
        """
        try:
            # Ellenőrizzük, hogy létezik-e a termék
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ProductNotFoundError(f"Product with id {product_id} not found")

            # Ellenőrizzük, hogy létezik-e a modifier group
            group = db.query(ModifierGroup).filter(
                ModifierGroup.id == group_id
            ).first()
            if not group:
                raise ModifierGroupNotFoundError(
                    f"ModifierGroup with id {group_id} not found"
                )

            # Ellenőrizzük, hogy már létezik-e az asszociáció
            if group in product.modifier_groups:
                raise ModifierServiceError(
                    f"ModifierGroup {group_id} is already associated with Product {product_id}"
                )

            # Hozzáadjuk az asszociációt
            product.modifier_groups.append(group)
            db.commit()
            return True
        except (ProductNotFoundError, ModifierGroupNotFoundError, ModifierServiceError):
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise ModifierServiceError(
                f"Failed to associate modifier group to product: {str(e)}"
            )

    @staticmethod
    def remove_modifier_group_from_product(
        db: Session,
        product_id: int,
        group_id: int
    ) -> bool:
        """
        ModifierGroup eltávolítása egy Product-ból.

        Args:
            db: SQLAlchemy session
            product_id: Termék azonosító
            group_id: ModifierGroup azonosító

        Returns:
            bool: True, ha sikeres az eltávolítás

        Raises:
            ProductNotFoundError: Ha nem található a termék
            ModifierGroupNotFoundError: Ha nem található a modifier group
            ModifierServiceError: Ha nincs asszociáció vagy adatbázis hiba

        Example:
            ModifierService.remove_modifier_group_from_product(
                db,
                product_id=1,
                group_id=1
            )
        """
        try:
            # Ellenőrizzük, hogy létezik-e a termék
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ProductNotFoundError(f"Product with id {product_id} not found")

            # Ellenőrizzük, hogy létezik-e a modifier group
            group = db.query(ModifierGroup).filter(
                ModifierGroup.id == group_id
            ).first()
            if not group:
                raise ModifierGroupNotFoundError(
                    f"ModifierGroup with id {group_id} not found"
                )

            # Ellenőrizzük, hogy létezik-e az asszociáció
            if group not in product.modifier_groups:
                raise ModifierServiceError(
                    f"ModifierGroup {group_id} is not associated with Product {product_id}"
                )

            # Eltávolítjuk az asszociációt
            product.modifier_groups.remove(group)
            db.commit()
            return True
        except (ProductNotFoundError, ModifierGroupNotFoundError, ModifierServiceError):
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise ModifierServiceError(
                f"Failed to remove modifier group from product: {str(e)}"
            )

    @staticmethod
    def get_modifier_groups_by_product(
        db: Session,
        product_id: int,
        include_modifiers: bool = False
    ) -> List[ModifierGroupResponse | ModifierGroupWithModifiers]:
        """
        Egy termékhez tartozó összes ModifierGroup lekérdezése.

        Args:
            db: SQLAlchemy session
            product_id: Termék azonosító
            include_modifiers: Ha True, betölti minden group összes modifier-ét

        Returns:
            Lista a modifier group-okkal

        Raises:
            ProductNotFoundError: Ha nem található a termék

        Example:
            # Alap lekérdezés
            groups = ModifierService.get_modifier_groups_by_product(db, product_id=1)

            # Modifierekkel együtt (pl. rendelés összeállításhoz)
            groups = ModifierService.get_modifier_groups_by_product(
                db,
                product_id=1,
                include_modifiers=True
            )
        """
        # Ellenőrizzük, hogy létezik-e a termék
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ProductNotFoundError(f"Product with id {product_id} not found")

        query = db.query(ModifierGroup).join(
            product_modifier_group_associations
        ).filter(
            product_modifier_group_associations.c.product_id == product_id
        )

        if include_modifiers:
            query = query.options(joinedload(ModifierGroup.modifiers))

        groups = query.all()

        if include_modifiers:
            return [ModifierGroupWithModifiers.model_validate(g) for g in groups]
        return [ModifierGroupResponse.model_validate(g) for g in groups]
