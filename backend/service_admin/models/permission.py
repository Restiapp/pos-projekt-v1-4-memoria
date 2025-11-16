"""
Permission Model - SQLAlchemy ORM
Module 6: RBAC (Role-Based Access Control) - Permission Management

Jogosultságok (permissions) kezelése RBAC rendszerben.
Granulált hozzáférés-vezérlés resource:action alapon.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_admin.models.database import Base


class Permission(Base):
    """
    Permission (Jogosultság) modell - RBAC.

    Támogatja:
    - Granulált jogosultság-kezelés (resource + action)
    - Many-to-Many kapcsolat Role modellel
    - Előre definiált rendszer jogosultságok
    - Dinamikus jogosultságok létrehozása

    Példa jogosultságok:
    - orders:create - Rendelés létrehozása
    - orders:view - Rendelések megtekintése
    - orders:update - Rendelés módosítása
    - orders:delete - Rendelés törlése
    - reports:view - Riportok megtekintése
    - admin:all - Admin teljes hozzáférés
    - inventory:manage - Készletkezelés
    - ntak:send - NTAK adatküldés
    """
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Jogosultság egyedi neve (resource:action formátum)
    # Pl: 'orders:create', 'reports:view', 'admin:all'
    name = Column(String(100), nullable=False, unique=True, index=True)

    # Megjelenítési név (felhasználóbarát)
    display_name = Column(String(255), nullable=True)

    # Leírás a jogosultságról
    description = Column(Text, nullable=True)

    # Resource típus (mi a jogosultság tárgya)
    # Pl: 'orders', 'inventory', 'reports', 'admin', 'ntak'
    resource = Column(String(100), nullable=False, index=True)

    # Action (milyen műveletet engedélyez)
    # Pl: 'create', 'read', 'update', 'delete', 'manage', 'all'
    action = Column(String(100), nullable=False, index=True)

    # Rendszer jogosultság jelölő (nem törölhető/nem módosítható)
    is_system = Column(Boolean, nullable=False, default=False)

    # Aktív státusz
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    # Automatikus időbélyegek
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships

    # Many-to-Many kapcsolat a Role modellel
    roles = relationship(
        'Role',
        secondary='role_permissions',  # Reference by table name string
        back_populates='permissions',
        lazy='selectin'
    )

    def __repr__(self):
        return (
            f"<Permission(id={self.id}, "
            f"name='{self.name}', "
            f"resource='{self.resource}', "
            f"action='{self.action}')>"
        )

    @staticmethod
    def parse_permission_name(name: str) -> tuple[str, str]:
        """
        Jogosultság név szétbontása resource és action részekre.

        Args:
            name: Jogosultság neve 'resource:action' formátumban

        Returns:
            tuple: (resource, action) pár

        Raises:
            ValueError: Ha a formátum nem megfelelő
        """
        parts = name.split(':', 1)
        if len(parts) != 2:
            raise ValueError(
                f"Invalid permission format: '{name}'. "
                f"Expected format: 'resource:action'"
            )
        return parts[0], parts[1]

    @classmethod
    def from_name(cls, name: str, **kwargs):
        """
        Permission objektum létrehozása név alapján.

        Automatikusan szétbontja a resource és action részekre.

        Args:
            name: Jogosultság neve 'resource:action' formátumban
            **kwargs: További opcionális mezők

        Returns:
            Permission: Új Permission objektum

        Example:
            perm = Permission.from_name(
                'orders:create',
                display_name='Rendelés létrehozása',
                description='Új rendelés felvitele a rendszerbe'
            )
        """
        resource, action = cls.parse_permission_name(name)
        return cls(
            name=name,
            resource=resource,
            action=action,
            **kwargs
        )


# Indexek a gyakori lekérdezésekhez
Index('idx_permission_resource_action', Permission.resource, Permission.action)
Index('idx_permission_active_system', Permission.is_active, Permission.is_system)
Index('idx_permission_name_active', Permission.name, Permission.is_active)
