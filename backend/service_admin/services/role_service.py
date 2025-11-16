"""
RoleService - Role (Szerepkör) kezelése
Module 6: RBAC (Role-Based Access Control) - Role Management

Ez a service felelős a szerepkörök CRUD műveleteinek kezeléséért,
beleértve a jogosultságok (permissions) hozzárendelését is.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.service_admin.models.role import Role
from backend.service_admin.models.permission import Permission
from backend.service_admin.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    """
    Service osztály a szerepkörök (roles) kezeléséhez.

    Felelősségek:
    - Szerepkörök létrehozása, módosítása, törlése
    - Szerepkörök lekérdezése (egyedi, lista, szűrés)
    - Jogosultságok hozzárendelése/eltávolítása szerepkörökhöz
    - Szerepkör jogosultságainak lekérdezése
    """

    def __init__(self, db: Session):
        """
        Inicializálja a RoleService-t.

        Args:
            db: SQLAlchemy Session objektum dependency injectionből
        """
        self.db = db

    def create_role(self, role_data: RoleCreate) -> Role:
        """
        Létrehoz egy új szerepkört.

        Args:
            role_data: RoleCreate schema az új szerepkör adataival

        Returns:
            Role: A létrehozott szerepkör objektum

        Raises:
            HTTPException: 400 ha már létezik ilyen nevű szerepkör
            HTTPException: 404 ha valamelyik megadott permission_id nem létezik

        Example:
            >>> role_service.create_role(
            ...     RoleCreate(
            ...         name="Manager",
            ...         description="Menedzser szerepkör - vezetői funkciók",
            ...         permission_ids=[1, 2, 3]
            ...     )
            ... )
        """
        # Ellenőrizzük, hogy létezik-e már ilyen nevű szerepkör
        existing_role = self.get_role_by_name(role_data.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with name '{role_data.name}' already exists"
            )

        # Létrehozzuk az új szerepkört
        new_role = Role(
            name=role_data.name,
            description=role_data.description
        )

        # Hozzáadjuk a jogosultságokat, ha meg lettek adva
        if role_data.permission_ids:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()

            if len(permissions) != len(role_data.permission_ids):
                found_ids = {perm.id for perm in permissions}
                missing_ids = set(role_data.permission_ids) - found_ids
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Permissions not found: {missing_ids}"
                )

            new_role.permissions = permissions

        try:
            self.db.add(new_role)
            self.db.commit()
            self.db.refresh(new_role)
            return new_role
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

    def get_role(self, role_id: int) -> Role:
        """
        Lekér egy szerepkört ID alapján.

        Args:
            role_id: A szerepkör egyedi azonosítója

        Returns:
            Role: A szerepkör objektum

        Raises:
            HTTPException: 404 ha nem található a szerepkör
        """
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with id {role_id} not found"
            )
        return role

    def get_role_by_name(self, name: str) -> Optional[Role]:
        """
        Lekér egy szerepkört név alapján.

        Args:
            name: A szerepkör neve

        Returns:
            Optional[Role]: A szerepkör objektum vagy None ha nem található
        """
        return self.db.query(Role).filter(Role.name == name).first()

    def get_all_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        is_system: Optional[bool] = None
    ) -> List[Role]:
        """
        Lekéri a szerepkörök listáját szűrési feltételekkel.

        Args:
            skip: Lapozás kezdőpontja (offset)
            limit: Maximum visszaadott szerepkörök száma
            is_active: Szűrés aktív státuszra (opcionális)
            is_system: Szűrés rendszer szerepkörre (opcionális)

        Returns:
            List[Role]: Szerepkörök listája
        """
        query = self.db.query(Role)

        # Szűrések alkalmazása
        if is_active is not None:
            query = query.filter(Role.is_active == is_active)
        if is_system is not None:
            query = query.filter(Role.is_system == is_system)

        # Rendezés név szerint
        query = query.order_by(Role.name)

        # Lapozás
        roles = query.offset(skip).limit(limit).all()
        return roles

    def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """
        Frissít egy meglévő szerepkört.

        Args:
            role_id: A szerepkör egyedi azonosítója
            role_data: RoleUpdate schema a frissítendő adatokkal

        Returns:
            Role: A frissített szerepkör objektum

        Raises:
            HTTPException: 404 ha nem található a szerepkör
            HTTPException: 400 ha a név már foglalt (más szerepkörnél)
            HTTPException: 404 ha valamelyik megadott permission_id nem létezik
        """
        role = self.get_role(role_id)

        # Ellenőrizzük a név egyediségét (ha meg lett adva új név)
        if role_data.name and role_data.name != role.name:
            existing_role = self.get_role_by_name(role_data.name)
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role with name '{role_data.name}' already exists"
                )
            role.name = role_data.name

        # Frissítjük a mezőket
        if role_data.description is not None:
            role.description = role_data.description

        # Frissítjük a jogosultságokat (ha meg lettek adva)
        if role_data.permission_ids is not None:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()

            if len(permissions) != len(role_data.permission_ids):
                found_ids = {perm.id for perm in permissions}
                missing_ids = set(role_data.permission_ids) - found_ids
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Permissions not found: {missing_ids}"
                )

            # Lecseréljük a jogosultságokat
            role.permissions = permissions

        try:
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

    def delete_role(self, role_id: int) -> bool:
        """
        Töröl egy szerepkört.

        Args:
            role_id: A törölni kívánt szerepkör azonosítója

        Returns:
            bool: True ha a törlés sikeres volt

        Raises:
            HTTPException: 404 ha nem található a szerepkör
            HTTPException: 400 ha rendszer szerepkört próbálunk törölni
        """
        role = self.get_role(role_id)

        # Rendszer szerepköröket nem törölhetünk
        if role.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"System role '{role.name}' cannot be deleted"
            )

        try:
            self.db.delete(role)
            self.db.commit()
            return True
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role: {str(e)}"
            )

    def add_permission_to_role(self, role_id: int, permission_id: int) -> Role:
        """
        Hozzáad egy jogosultságot egy szerepkörhöz.

        Args:
            role_id: A szerepkör azonosítója
            permission_id: A jogosultság azonosítója

        Returns:
            Role: A frissített szerepkör objektum

        Raises:
            HTTPException: 404 ha nem található a szerepkör vagy a jogosultság
            HTTPException: 400 ha a jogosultság már hozzá van rendelve
        """
        role = self.get_role(role_id)

        permission = self.db.query(Permission).filter(
            Permission.id == permission_id
        ).first()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with id {permission_id} not found"
            )

        # Ellenőrizzük, hogy már nincs-e hozzárendelve
        if permission in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission '{permission.name}' already assigned to role '{role.name}'"
            )

        role.add_permission(permission)

        try:
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

    def remove_permission_from_role(self, role_id: int, permission_id: int) -> Role:
        """
        Eltávolít egy jogosultságot egy szerepkörből.

        Args:
            role_id: A szerepkör azonosítója
            permission_id: A jogosultság azonosítója

        Returns:
            Role: A frissített szerepkör objektum

        Raises:
            HTTPException: 404 ha nem található a szerepkör vagy a jogosultság
            HTTPException: 400 ha a jogosultság nincs hozzárendelve
        """
        role = self.get_role(role_id)

        permission = self.db.query(Permission).filter(
            Permission.id == permission_id
        ).first()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with id {permission_id} not found"
            )

        # Ellenőrizzük, hogy hozzá van-e rendelve
        if permission not in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission '{permission.name}' is not assigned to role '{role.name}'"
            )

        role.remove_permission(permission)

        try:
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """
        Lekéri egy szerepkör összes jogosultságát.

        Args:
            role_id: A szerepkör azonosítója

        Returns:
            List[Permission]: A szerepkörhöz tartozó jogosultságok listája

        Raises:
            HTTPException: 404 ha nem található a szerepkör
        """
        role = self.get_role(role_id)
        return role.permissions

    def count_roles(
        self,
        is_active: Optional[bool] = None,
        is_system: Optional[bool] = None
    ) -> int:
        """
        Megszámolja a szerepköröket szűrési feltételekkel.

        Args:
            is_active: Szűrés aktív státuszra (opcionális)
            is_system: Szűrés rendszer szerepkörre (opcionális)

        Returns:
            int: Szerepkörök száma
        """
        query = self.db.query(Role)

        if is_active is not None:
            query = query.filter(Role.is_active == is_active)
        if is_system is not None:
            query = query.filter(Role.is_system == is_system)

        return query.count()

    def deactivate_role(self, role_id: int) -> Role:
        """
        Deaktiválja egy szerepkört (nem törli, csak inaktívra állítja).

        Args:
            role_id: A szerepkör azonosítója

        Returns:
            Role: A frissített szerepkör objektum

        Raises:
            HTTPException: 404 ha nem található a szerepkör
        """
        role = self.get_role(role_id)
        role.is_active = False

        self.db.commit()
        self.db.refresh(role)
        return role

    def activate_role(self, role_id: int) -> Role:
        """
        Aktiválja egy szerepkört.

        Args:
            role_id: A szerepkör azonosítója

        Returns:
            Role: A frissített szerepkör objektum

        Raises:
            HTTPException: 404 ha nem található a szerepkör
        """
        role = self.get_role(role_id)
        role.is_active = True

        self.db.commit()
        self.db.refresh(role)
        return role
