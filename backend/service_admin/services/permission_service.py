"""
PermissionService - Permission (Jogosultság) kezelése
Module 6: RBAC (Role-Based Access Control) - Permission Management

Ez a service felelős a jogosultságok CRUD műveleteinek kezeléséért,
granulált hozzáférés-vezérlés támogatásával (resource:action formátum).
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.service_admin.models.permission import Permission
from backend.service_admin.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:
    """
    Service osztály a jogosultságok (permissions) kezeléséhez.

    Felelősségek:
    - Jogosultságok létrehozása, módosítása, törlése
    - Jogosultságok lekérdezése (egyedi, lista, szűrés)
    - Resource-alapú és action-alapú szűrés
    - Granulált jogosultság-kezelés támogatása
    """

    def __init__(self, db: Session):
        """
        Inicializálja a PermissionService-t.

        Args:
            db: SQLAlchemy Session objektum dependency injectionből
        """
        self.db = db

    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """
        Létrehoz egy új jogosultságot.

        Args:
            permission_data: PermissionCreate schema az új jogosultság adataival

        Returns:
            Permission: A létrehozott jogosultság objektum

        Raises:
            HTTPException: 400 ha már létezik ilyen nevű jogosultság

        Example:
            >>> permission_service.create_permission(
            ...     PermissionCreate(
            ...         name="view_orders",
            ...         description="Rendelések megtekintése",
            ...         resource="orders",
            ...         action="view"
            ...     )
            ... )
        """
        # Ellenőrizzük, hogy létezik-e már ilyen nevű jogosultság
        existing_permission = self.get_permission_by_name(permission_data.name)
        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission with name '{permission_data.name}' already exists"
            )

        # Létrehozzuk az új jogosultságot
        new_permission = Permission(
            name=permission_data.name,
            description=permission_data.description,
            resource=permission_data.resource,
            action=permission_data.action
        )

        try:
            self.db.add(new_permission)
            self.db.commit()
            self.db.refresh(new_permission)
            return new_permission
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

    def get_permission(self, permission_id: int) -> Permission:
        """
        Lekér egy jogosultságot ID alapján.

        Args:
            permission_id: A jogosultság egyedi azonosítója

        Returns:
            Permission: A jogosultság objektum

        Raises:
            HTTPException: 404 ha nem található a jogosultság
        """
        permission = self.db.query(Permission).filter(
            Permission.id == permission_id
        ).first()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with id {permission_id} not found"
            )
        return permission

    def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """
        Lekér egy jogosultságot név alapján.

        Args:
            name: A jogosultság neve (pl. 'view_orders')

        Returns:
            Optional[Permission]: A jogosultság objektum vagy None ha nem található
        """
        return self.db.query(Permission).filter(Permission.name == name).first()

    def get_all_permissions(
        self,
        skip: int = 0,
        limit: int = 100,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_system: Optional[bool] = None
    ) -> List[Permission]:
        """
        Lekéri a jogosultságok listáját szűrési feltételekkel.

        Args:
            skip: Lapozás kezdőpontja (offset)
            limit: Maximum visszaadott jogosultságok száma
            resource: Szűrés resource típusra (pl. 'orders', 'employees')
            action: Szűrés action típusra (pl. 'view', 'create', 'delete')
            is_active: Szűrés aktív státuszra (opcionális)
            is_system: Szűrés rendszer jogosultságra (opcionális)

        Returns:
            List[Permission]: Jogosultságok listája
        """
        query = self.db.query(Permission)

        # Szűrések alkalmazása
        if resource:
            query = query.filter(Permission.resource == resource)
        if action:
            query = query.filter(Permission.action == action)
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        if is_system is not None:
            query = query.filter(Permission.is_system == is_system)

        # Rendezés resource és action szerint
        query = query.order_by(Permission.resource, Permission.action)

        # Lapozás
        permissions = query.offset(skip).limit(limit).all()
        return permissions

    def get_permissions_by_resource(self, resource: str) -> List[Permission]:
        """
        Lekéri az összes jogosultságot egy adott resource-hoz.

        Args:
            resource: A resource típusa (pl. 'orders', 'employees')

        Returns:
            List[Permission]: Az adott resource-hoz tartozó jogosultságok listája
        """
        return self.db.query(Permission).filter(
            Permission.resource == resource
        ).order_by(Permission.action).all()

    def get_permissions_by_action(self, action: str) -> List[Permission]:
        """
        Lekéri az összes jogosultságot egy adott action-höz.

        Args:
            action: Az action típusa (pl. 'view', 'create', 'delete')

        Returns:
            List[Permission]: Az adott action-höz tartozó jogosultságok listája
        """
        return self.db.query(Permission).filter(
            Permission.action == action
        ).order_by(Permission.resource).all()

    def update_permission(
        self,
        permission_id: int,
        permission_data: PermissionUpdate
    ) -> Permission:
        """
        Frissít egy meglévő jogosultságot.

        Args:
            permission_id: A jogosultság egyedi azonosítója
            permission_data: PermissionUpdate schema a frissítendő adatokkal

        Returns:
            Permission: A frissített jogosultság objektum

        Raises:
            HTTPException: 404 ha nem található a jogosultság
            HTTPException: 400 ha a név már foglalt (más jogosultságnál)
        """
        permission = self.get_permission(permission_id)

        # Ellenőrizzük a név egyediségét (ha meg lett adva új név)
        if permission_data.name and permission_data.name != permission.name:
            existing_permission = self.get_permission_by_name(permission_data.name)
            if existing_permission:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission with name '{permission_data.name}' already exists"
                )
            permission.name = permission_data.name

        # Frissítjük a mezőket
        if permission_data.description is not None:
            permission.description = permission_data.description
        if permission_data.resource is not None:
            permission.resource = permission_data.resource
        if permission_data.action is not None:
            permission.action = permission_data.action

        try:
            self.db.commit()
            self.db.refresh(permission)
            return permission
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {str(e)}"
            )

    def delete_permission(self, permission_id: int) -> bool:
        """
        Töröl egy jogosultságot.

        Args:
            permission_id: A törölni kívánt jogosultság azonosítója

        Returns:
            bool: True ha a törlés sikeres volt

        Raises:
            HTTPException: 404 ha nem található a jogosultság
            HTTPException: 400 ha rendszer jogosultságot próbálunk törölni
        """
        permission = self.get_permission(permission_id)

        # Rendszer jogosultságokat nem törölhetünk
        if permission.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"System permission '{permission.name}' cannot be deleted"
            )

        try:
            self.db.delete(permission)
            self.db.commit()
            return True
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete permission: {str(e)}"
            )

    def count_permissions(
        self,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_system: Optional[bool] = None
    ) -> int:
        """
        Megszámolja a jogosultságokat szűrési feltételekkel.

        Args:
            resource: Szűrés resource típusra (opcionális)
            action: Szűrés action típusra (opcionális)
            is_active: Szűrés aktív státuszra (opcionális)
            is_system: Szűrés rendszer jogosultságra (opcionális)

        Returns:
            int: Jogosultságok száma
        """
        query = self.db.query(Permission)

        if resource:
            query = query.filter(Permission.resource == resource)
        if action:
            query = query.filter(Permission.action == action)
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        if is_system is not None:
            query = query.filter(Permission.is_system == is_system)

        return query.count()

    def deactivate_permission(self, permission_id: int) -> Permission:
        """
        Deaktiválja egy jogosultságot (nem törli, csak inaktívra állítja).

        Args:
            permission_id: A jogosultság azonosítója

        Returns:
            Permission: A frissített jogosultság objektum

        Raises:
            HTTPException: 404 ha nem található a jogosultság
        """
        permission = self.get_permission(permission_id)
        permission.is_active = False

        self.db.commit()
        self.db.refresh(permission)
        return permission

    def activate_permission(self, permission_id: int) -> Permission:
        """
        Aktiválja egy jogosultságot.

        Args:
            permission_id: A jogosultság azonosítója

        Returns:
            Permission: A frissített jogosultság objektum

        Raises:
            HTTPException: 404 ha nem található a jogosultság
        """
        permission = self.get_permission(permission_id)
        permission.is_active = True

        self.db.commit()
        self.db.refresh(permission)
        return permission

    def get_unique_resources(self) -> List[str]:
        """
        Lekéri az összes egyedi resource típust az adatbázisból.

        Returns:
            List[str]: Egyedi resource nevek listája
        """
        resources = self.db.query(Permission.resource).distinct().all()
        return [r[0] for r in resources]

    def get_unique_actions(self) -> List[str]:
        """
        Lekéri az összes egyedi action típust az adatbázisból.

        Returns:
            List[str]: Egyedi action nevek listája
        """
        actions = self.db.query(Permission.action).distinct().all()
        return [a[0] for a in actions]

    def bulk_create_permissions(
        self,
        permissions_data: List[PermissionCreate]
    ) -> List[Permission]:
        """
        Több jogosultság létrehozása egyszerre (bulk operation).

        Args:
            permissions_data: Lista PermissionCreate schemákból

        Returns:
            List[Permission]: A létrehozott jogosultságok listája

        Raises:
            HTTPException: 400 ha bármelyik jogosultság már létezik vagy hiba van
        """
        created_permissions = []

        try:
            for perm_data in permissions_data:
                # Ellenőrizzük, hogy nem létezik-e már
                existing = self.get_permission_by_name(perm_data.name)
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Permission with name '{perm_data.name}' already exists"
                    )

                new_permission = Permission(
                    name=perm_data.name,
                    description=perm_data.description,
                    resource=perm_data.resource,
                    action=perm_data.action
                )
                self.db.add(new_permission)
                created_permissions.append(new_permission)

            self.db.commit()

            # Refresh all created permissions
            for perm in created_permissions:
                self.db.refresh(perm)

            return created_permissions

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error during bulk creation: {str(e)}"
            )
