"""
Database Seeding Script - RBAC (Module 6)
==========================================

Ez a script feltölti az adatbázist az alapvető RBAC struktúrával:
- Permissions (Jogosultságok)
- Roles (Szerepkörök: Admin, Pultos, Szakács)
- Default Admin Employee (PIN kóddal)

Használat:
    python -m backend.service_admin.seed_rbac

FIGYELEM: Ez a script development/testing célokra készült.
Production környezetben használj Alembic migration-öket!
"""

import sys
import logging
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Import database models and services
from backend.service_admin.models.database import init_db, SessionLocal, Base, engine
from backend.service_admin.models.employee import Employee
from backend.service_admin.models.role import Role
from backend.service_admin.models.permission import Permission

# Password/PIN hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# PERMISSION DEFINITIONS
# ============================================================================

SYSTEM_PERMISSIONS = [
    # Orders Management
    {
        "name": "orders:manage",
        "display_name": "Rendelések kezelése",
        "description": "Rendelések létrehozása, módosítása, törlése, megtekintése",
        "resource": "orders",
        "action": "manage",
        "is_system": True
    },
    {
        "name": "orders:view",
        "display_name": "Rendelések megtekintése",
        "description": "Rendelések és rendelési tételek megtekintése",
        "resource": "orders",
        "action": "view",
        "is_system": True
    },
    {
        "name": "orders:create",
        "display_name": "Rendelés létrehozása",
        "description": "Új rendelések felvétele",
        "resource": "orders",
        "action": "create",
        "is_system": True
    },

    # Menu Management
    {
        "name": "menu:manage",
        "display_name": "Menü kezelése",
        "description": "Termékek, kategóriák, módosítók kezelése",
        "resource": "menu",
        "action": "manage",
        "is_system": True
    },
    {
        "name": "menu:view",
        "display_name": "Menü megtekintése",
        "description": "Termékek és kategóriák megtekintése",
        "resource": "menu",
        "action": "view",
        "is_system": True
    },

    # Inventory Management
    {
        "name": "inventory:manage",
        "display_name": "Készlet kezelése",
        "description": "Készlet, alapanyagok, receptúrák, számlák kezelése",
        "resource": "inventory",
        "action": "manage",
        "is_system": True
    },
    {
        "name": "inventory:view",
        "display_name": "Készlet megtekintése",
        "description": "Készletadatok és receptúrák megtekintése",
        "resource": "inventory",
        "action": "view",
        "is_system": True
    },

    # Kitchen Display System
    {
        "name": "kds:view",
        "display_name": "Konyhai kijelző megtekintése",
        "description": "Konyhai rendelések megtekintése és státusz frissítése",
        "resource": "kds",
        "action": "view",
        "is_system": True
    },

    # Reports & Analytics
    {
        "name": "reports:view",
        "display_name": "Riportok megtekintése",
        "description": "Eladási és készlet riportok megtekintése",
        "resource": "reports",
        "action": "view",
        "is_system": True
    },
    {
        "name": "reports:manage",
        "display_name": "Riportok kezelése",
        "description": "Riportok generálása és exportálása",
        "resource": "reports",
        "action": "manage",
        "is_system": True
    },

    # Employee & RBAC Management
    {
        "name": "employees:manage",
        "display_name": "Munkatársak kezelése",
        "description": "Munkatársak létrehozása, módosítása, törlése",
        "resource": "employees",
        "action": "manage",
        "is_system": True
    },
    {
        "name": "roles:manage",
        "display_name": "Szerepkörök kezelése",
        "description": "Szerepkörök és jogosultságok kezelése",
        "resource": "roles",
        "action": "manage",
        "is_system": True
    },

    # NTAK Integration
    {
        "name": "ntak:send",
        "display_name": "NTAK adatküldés",
        "description": "NTAK adatcsomagok küldése és kezelése",
        "resource": "ntak",
        "action": "send",
        "is_system": True
    },

    # System Administration
    {
        "name": "admin:all",
        "display_name": "Teljes admin hozzáférés",
        "description": "Korlátlan hozzáférés minden funkcióhoz",
        "resource": "admin",
        "action": "all",
        "is_system": True
    },
]


# ============================================================================
# ROLE DEFINITIONS
# ============================================================================

SYSTEM_ROLES = [
    {
        "name": "Admin",
        "display_name": "Rendszergazda",
        "description": "Teljes hozzáférés minden funkcióhoz és beállításhoz",
        "is_system": True,
        "permissions": [
            "admin:all",
            "orders:manage",
            "menu:manage",
            "inventory:manage",
            "reports:manage",
            "employees:manage",
            "roles:manage",
            "ntak:send",
        ]
    },
    {
        "name": "Pultos",
        "display_name": "Pincér / Pultos",
        "description": "Rendelések felvétele, menü megtekintése, alapvető műveletek",
        "is_system": True,
        "permissions": [
            "orders:manage",
            "menu:view",
            "inventory:view",
        ]
    },
    {
        "name": "Szakács",
        "display_name": "Szakács / Konyha",
        "description": "Konyhai kijelző, rendelések megtekintése",
        "is_system": True,
        "permissions": [
            "kds:view",
            "orders:view",
            "menu:view",
        ]
    },
]


# ============================================================================
# DEFAULT ADMIN EMPLOYEE
# ============================================================================

DEFAULT_ADMIN = {
    "name": "Rendszergazda",
    "username": "admin",
    "pin_code": "1234",  # FIGYELEM: Production-ben változtasd meg!
    "email": "admin@restiapp.com",
    "is_active": True,
    "is_admin": True,
    "roles": ["Admin"]  # Szerepkör név
}


# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================

def seed_permissions(db: Session) -> Dict[str, Permission]:
    """
    Feltölti az adatbázist az alapvető jogosultságokkal (permissions).

    Args:
        db: SQLAlchemy Session

    Returns:
        Dict[str, Permission]: Permission objektumok name alapján indexelve
    """
    logger.info("🔐 Jogosultságok (Permissions) feltöltése...")

    permissions_map = {}

    for perm_data in SYSTEM_PERMISSIONS:
        # Ellenőrizzük, hogy már létezik-e
        existing = db.query(Permission).filter(
            Permission.name == perm_data["name"]
        ).first()

        if existing:
            logger.info(f"  ⏭️  Permission már létezik: {perm_data['name']}")
            permissions_map[perm_data["name"]] = existing
            continue

        # Új permission létrehozása
        permission = Permission(
            name=perm_data["name"],
            display_name=perm_data["display_name"],
            description=perm_data["description"],
            resource=perm_data["resource"],
            action=perm_data["action"],
            is_system=perm_data["is_system"]
        )

        db.add(permission)
        permissions_map[perm_data["name"]] = permission
        logger.info(f"  ✅ Létrehozva: {perm_data['name']}")

    db.commit()
    logger.info(f"✅ {len(permissions_map)} jogosultság feltöltve")

    return permissions_map


def seed_roles(db: Session, permissions_map: Dict[str, Permission]) -> Dict[str, Role]:
    """
    Feltölti az adatbázist az alapvető szerepkörökkel (roles).

    Args:
        db: SQLAlchemy Session
        permissions_map: Permission objektumok name alapján indexelve

    Returns:
        Dict[str, Role]: Role objektumok name alapján indexelve
    """
    logger.info("👥 Szerepkörök (Roles) feltöltése...")

    roles_map = {}

    for role_data in SYSTEM_ROLES:
        # Ellenőrizzük, hogy már létezik-e
        existing = db.query(Role).filter(
            Role.name == role_data["name"]
        ).first()

        if existing:
            logger.info(f"  ⏭️  Role már létezik: {role_data['name']}")
            roles_map[role_data["name"]] = existing
            continue

        # Új role létrehozása
        role = Role(
            name=role_data["name"],
            display_name=role_data["display_name"],
            description=role_data["description"],
            is_system=role_data["is_system"]
        )

        # Jogosultságok hozzárendelése
        for perm_name in role_data["permissions"]:
            if perm_name in permissions_map:
                role.permissions.append(permissions_map[perm_name])
            else:
                logger.warning(f"  ⚠️  Hiányzó permission: {perm_name}")

        db.add(role)
        roles_map[role_data["name"]] = role
        logger.info(f"  ✅ Létrehozva: {role_data['name']} ({len(role.permissions)} jogosultsággal)")

    db.commit()
    logger.info(f"✅ {len(roles_map)} szerepkör feltöltve")

    return roles_map


def seed_default_admin(db: Session, roles_map: Dict[str, Role]) -> Optional[Employee]:
    """
    Létrehozza az alapértelmezett admin felhasználót.

    Args:
        db: SQLAlchemy Session
        roles_map: Role objektumok name alapján indexelve

    Returns:
        Optional[Employee]: Az admin Employee objektum vagy None
    """
    logger.info("👤 Alapértelmezett Admin felhasználó létrehozása...")

    # Ellenőrizzük, hogy már létezik-e
    existing = db.query(Employee).filter(
        Employee.username == DEFAULT_ADMIN["username"]
    ).first()

    if existing:
        logger.info(f"  ⏭️  Admin felhasználó már létezik: {DEFAULT_ADMIN['username']}")
        return existing

    # PIN kód hashelése
    pin_hash = pwd_context.hash(DEFAULT_ADMIN["pin_code"])

    # Új admin employee létrehozása
    admin = Employee(
        name=DEFAULT_ADMIN["name"],
        username=DEFAULT_ADMIN["username"],
        pin_code_hash=pin_hash,
        email=DEFAULT_ADMIN["email"],
        is_active=DEFAULT_ADMIN["is_active"],
        is_admin=DEFAULT_ADMIN["is_admin"]
    )

    # Admin szerepkör hozzárendelése
    for role_name in DEFAULT_ADMIN["roles"]:
        if role_name in roles_map:
            admin.roles.append(roles_map[role_name])
        else:
            logger.warning(f"  ⚠️  Hiányzó role: {role_name}")

    db.add(admin)
    db.commit()
    db.refresh(admin)

    logger.info(f"  ✅ Admin felhasználó létrehozva:")
    logger.info(f"     Username: {admin.username}")
    logger.info(f"     PIN kód: {DEFAULT_ADMIN['pin_code']} (VÁLTOZTASD MEG PRODUCTION-BEN!)")
    logger.info(f"     Szerepkörök: {', '.join(DEFAULT_ADMIN['roles'])}")

    return admin


def verify_seeding(db: Session):
    """
    Ellenőrzi, hogy a seeding sikeresen lefutott-e.

    Args:
        db: SQLAlchemy Session
    """
    logger.info("\n📊 Seeding eredmények ellenőrzése...")

    # Permissions count
    perm_count = db.query(Permission).count()
    logger.info(f"  Permissions: {perm_count} db")

    # Roles count
    role_count = db.query(Role).count()
    logger.info(f"  Roles: {role_count} db")

    # Employees count
    emp_count = db.query(Employee).count()
    logger.info(f"  Employees: {emp_count} db")

    # Admin role permissions
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if admin_role:
        logger.info(f"  Admin role jogosultságok: {len(admin_role.permissions)} db")

    # Admin employee
    admin_emp = db.query(Employee).filter(Employee.username == "admin").first()
    if admin_emp:
        logger.info(f"  Admin employee roles: {len(admin_emp.roles)} db")
        logger.info(f"  Admin is_admin flag: {admin_emp.is_admin}")

    logger.info("✅ Seeding ellenőrzés befejezve")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Fő seeding folyamat.

    1. Adatbázis táblák inicializálása (create_all)
    2. Permissions feltöltése
    3. Roles feltöltése
    4. Default Admin employee létrehozása
    5. Eredmények ellenőrzése
    """
    logger.info("=" * 70)
    logger.info("🚀 RBAC Database Seeding - Module 6")
    logger.info("=" * 70)

    try:
        # 1. Adatbázis inicializálás
        logger.info("\n1️⃣  Adatbázis táblák inicializálása...")
        init_db()
        logger.info("✅ Táblák létrehozva (ha még nem léteztek)")

        # 2. Session létrehozása
        db = SessionLocal()

        try:
            # 3. Permissions seeding
            logger.info("\n2️⃣  Permissions seeding...")
            permissions_map = seed_permissions(db)

            # 4. Roles seeding
            logger.info("\n3️⃣  Roles seeding...")
            roles_map = seed_roles(db, permissions_map)

            # 5. Default Admin seeding
            logger.info("\n4️⃣  Default Admin employee seeding...")
            admin = seed_default_admin(db, roles_map)

            # 6. Verification
            logger.info("\n5️⃣  Verification...")
            verify_seeding(db)

            logger.info("\n" + "=" * 70)
            logger.info("🎉 SEEDING SIKERES!")
            logger.info("=" * 70)
            logger.info("\n📝 FONTOS TEENDŐK:")
            logger.info("  1. Változtasd meg az admin PIN kódot production környezetben!")
            logger.info("  2. Ellenőrizd az adatbázis kapcsolatot és a seeding eredményeket")
            logger.info("  3. Teszteld az admin bejelentkezést az API-n keresztül")
            logger.info("")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ HIBA a seeding során: {str(e)}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
