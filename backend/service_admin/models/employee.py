"""
Employee Model - SQLAlchemy ORM
Module 6: RBAC (Role-Based Access Control) - Employee Management

Munkatársak (alkalmazottak) kezelése PIN kóddal történő hitelesítéssel.
Támogatja a szerepkör alapú hozzáférés-vezérlést (RBAC).
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.service_admin.models.database import Base


# Asszociációs tábla: Employee <-> Role (Many-to-Many)
employee_roles = Table(
    'employee_roles',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
)


class Employee(Base):
    """
    Employee (Munkatárs) modell - RBAC és autentikáció.

    Támogatja:
    - PIN kóddal történő bejelentkezést (pin_code_hash)
    - Szerepkör alapú hozzáférés-vezérlés (RBAC) via roles relationship
    - Aktív/inaktív státusz kezelés
    - Audit trail (created_at, updated_at)
    """
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Munkatárs neve (teljes név)
    name = Column(String(255), nullable=False)

    # Felhasználónév (egyedi azonosító a bejelentkezéshez)
    username = Column(String(100), nullable=False, unique=True, index=True)

    # PIN kód hash (bcrypt/argon2 hash tárolása)
    # FIGYELEM: Soha ne tárold a PIN kódot nyílt szövegben!
    pin_code_hash = Column(String(255), nullable=False)

    # Email cím (opcionális, értesítésekhez)
    email = Column(String(255), nullable=True)

    # Telefonszám (opcionális, értesítésekhez)
    phone = Column(String(20), nullable=True)

    # Aktív státusz (True = aktív, False = inaktív/felfüggesztett)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    # Automatikus időbélyegek
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
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
        secondary=employee_roles,
        back_populates='employees',
        lazy='selectin'
    )

    def __repr__(self):
        return (
            f"<Employee(id={self.id}, "
            f"username='{self.username}', "
            f"name='{self.name}', "
            f"is_active={self.is_active})>"
        )

    @property
    def permissions(self):
        """
        Összegyűjti az összes jogosultságot az alkalmazott szerepköreiből.

        Returns:
            set: Egyedi Permission objektumok halmaza
        """
        perms = set()
        for role in self.roles:
            perms.update(role.permissions)
        return perms

    def has_permission(self, permission_name: str) -> bool:
        """
        Ellenőrzi, hogy az alkalmazottnak van-e adott jogosultsága.

        Args:
            permission_name: A jogosultság neve (pl. 'create_order')

        Returns:
            bool: True ha van jogosultsága, False ha nincs
        """
        return any(
            perm.name == permission_name
            for perm in self.permissions
        )


# Indexek a gyakori lekérdezésekhez
Index('idx_employee_username_active', Employee.username, Employee.is_active)
Index('idx_employee_active_created', Employee.is_active, Employee.created_at.desc())
