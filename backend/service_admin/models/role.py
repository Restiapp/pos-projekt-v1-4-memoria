"""
Role Model - SQLAlchemy ORM
Module 6: RBAC (Role-Based Access Control) - Role Management

Szerepkörök (role) kezelése jogosultságokkal (permissions).
RBAC rendszer alapja: Employee -> Role -> Permission hierarchia.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_admin.models.database import Base


# Asszociációs tábla: Role <-> Permission (Many-to-Many)
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
)


class Role(Base):
    """
    Role (Szerepkör) modell - RBAC.

    Támogatja:
    - Szerepkör alapú jogosultság-kezelés
    - Many-to-Many kapcsolat Employee és Permission modellekkel
    - Előre definiált szerepkörök (Admin, Manager, Waiter, Chef, etc.)
    - Szerepkörök aktiválása/deaktiválása

    Példa szerepkörök:
    - Admin: Teljes hozzáférés minden funkcióhoz
    - Manager: Menedzsment műveletek (riportok, beállítások)
    - Waiter: Rendelések felvétele, számlázás
    - Chef: Konyhai rendelések kezelése
    - Cashier: Kasszaműveletek
    """
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Szerepkör neve (egyedi)
    # Pl: 'Admin', 'Manager', 'Waiter', 'Chef', 'Cashier'
    name = Column(String(100), nullable=False, unique=True, index=True)

    # Megjelenítési név (felhasználóbarát)
    display_name = Column(String(255), nullable=True)

    # Leírás a szerepkörről
    description = Column(Text, nullable=True)

    # Aktív státusz
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    # Rendszer szerepkör jelölő (nem törölhető/nem módosítható)
    is_system = Column(Boolean, nullable=False, default=False)

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

    # Many-to-Many kapcsolat az Employee modellel
    employees = relationship(
        'Employee',
        secondary='employee_roles',  # Reference by table name string
        back_populates='roles',
        lazy='selectin'
    )

    # Many-to-Many kapcsolat a Permission modellel
    permissions = relationship(
        'Permission',
        secondary=role_permissions,
        back_populates='roles',
        lazy='selectin'
    )

    def __repr__(self):
        return (
            f"<Role(id={self.id}, "
            f"name='{self.name}', "
            f"is_active={self.is_active}, "
            f"is_system={self.is_system})>"
        )

    def has_permission(self, permission_name: str) -> bool:
        """
        Ellenőrzi, hogy a szerepkörnek van-e adott jogosultsága.

        Args:
            permission_name: A jogosultság neve (pl. 'create_order')

        Returns:
            bool: True ha van jogosultsága, False ha nincs
        """
        return any(
            perm.name == permission_name
            for perm in self.permissions
        )

    def add_permission(self, permission):
        """
        Jogosultság hozzáadása a szerepkörhöz.

        Args:
            permission: Permission objektum
        """
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission):
        """
        Jogosultság eltávolítása a szerepkörből.

        Args:
            permission: Permission objektum
        """
        if permission in self.permissions:
            self.permissions.remove(permission)


# Indexek a gyakori lekérdezésekhez
Index('idx_role_name_active', Role.name, Role.is_active)
Index('idx_role_active_system', Role.is_active, Role.is_system)
