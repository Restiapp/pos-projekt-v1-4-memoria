"""
RBAC Permissions Migration - V3.0 Phase X
==========================================

Hiányzó kritikus jogosultságok hozzáadása a permissions táblához.

Használat:
    python -m backend.service_admin.migrations.add_missing_permissions

Ez a szkript idempotens - újrafuttatható, nem hoz létre duplikátumokat.
"""

import sys
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Import database models
from backend.service_admin.models.database import SessionLocal, init_db
from backend.service_admin.models.permission import Permission
from backend.service_admin.models.role import Role

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# NEW PERMISSIONS TO ADD
# ============================================================================

NEW_PERMISSIONS = [
    # Finance Management
    {
        "name": "finance:manage",
        "display_name": "Pénzügyek kezelése",
        "description": "Számlák, kifizetések, pénzügyi tételek kezelése",
        "resource": "finance",
        "action": "manage",
        "is_system": True
    },
    {
        "name": "finance:view",
        "display_name": "Pénzügyek megtekintése",
        "description": "Pénzügyi adatok és számlák megtekintése",
        "resource": "finance",
        "action": "view",
        "is_system": True
    },

    # Asset Management
    {
        "name": "assets:manage",
        "display_name": "Eszközök kezelése",
        "description": "Eszközök, berendezések, tárgyi eszközök nyilvántartása és kezelése",
        "resource": "assets",
        "action": "manage",
        "is_system": True
    },
    {
        "name": "assets:view",
        "display_name": "Eszközök megtekintése",
        "description": "Eszköznyilvántartás megtekintése",
        "resource": "assets",
        "action": "view",
        "is_system": True
    },

    # Vehicle Management
    {
        "name": "vehicles:manage",
        "display_name": "Járművek kezelése",
        "description": "Járművek, tankolások, karbantartások kezelése",
        "resource": "vehicles",
        "action": "manage",
        "is_system": True
    },
    {
        "name": "vehicles:view",
        "display_name": "Járművek megtekintése",
        "description": "Járművek és kapcsolódó adatok megtekintése",
        "resource": "vehicles",
        "action": "view",
        "is_system": True
    },

    # Logistics Management
    {
        "name": "logistics:manage",
        "display_name": "Logisztika kezelése",
        "description": "Futárok, kiszállítási zónák, szállítások kezelése",
        "resource": "logistics",
        "action": "manage",
        "is_system": True
    },
    {
        "name": "logistics:view",
        "display_name": "Logisztika megtekintése",
        "description": "Logisztikai adatok megtekintése",
        "resource": "logistics",
        "action": "view",
        "is_system": True
    },
]

# Permissions to add to Admin role
ADMIN_PERMISSIONS = [
    "finance:manage",
    "assets:manage",
    "vehicles:manage",
    "logistics:manage"
]


# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def add_permissions(db: Session) -> dict:
    """
    Hozzáadja a hiányzó jogosultságokat.

    Args:
        db: SQLAlchemy Session

    Returns:
        dict: Statisztikák (added, skipped)
    """
    logger.info("🔐 Hiányzó jogosultságok hozzáadása...")

    stats = {"added": 0, "skipped": 0}
    added_permissions = {}

    for perm_data in NEW_PERMISSIONS:
        # Ellenőrizzük, hogy már létezik-e
        existing = db.query(Permission).filter(
            Permission.name == perm_data["name"]
        ).first()

        if existing:
            logger.info(f"  ⏭️  Permission már létezik: {perm_data['name']}")
            stats["skipped"] += 1
            added_permissions[perm_data["name"]] = existing
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
        added_permissions[perm_data["name"]] = permission
        stats["added"] += 1
        logger.info(f"  ✅ Létrehozva: {perm_data['name']}")

    db.commit()
    logger.info(f"✅ Permissions feldolgozva: {stats['added']} új, {stats['skipped']} meglévő")

    return added_permissions, stats


def update_admin_role(db: Session, permissions_map: dict) -> int:
    """
    Frissíti az Admin role jogosultságait az újakkal.

    Args:
        db: SQLAlchemy Session
        permissions_map: Permission objektumok name alapján indexelve

    Returns:
        int: Hozzáadott jogosultságok száma
    """
    logger.info("👤 Admin role frissítése...")

    # Admin role lekérése
    admin_role = db.query(Role).filter(Role.name == "Admin").first()

    if not admin_role:
        logger.warning("  ⚠️  Admin role nem található!")
        return 0

    added_count = 0

    # Új jogosultságok hozzáadása
    for perm_name in ADMIN_PERMISSIONS:
        if perm_name not in permissions_map:
            logger.warning(f"  ⚠️  Permission nem található: {perm_name}")
            continue

        permission = permissions_map[perm_name]

        # Ellenőrizzük, hogy már hozzá van-e rendelve
        if permission in admin_role.permissions:
            logger.info(f"  ⏭️  Admin már rendelkezik: {perm_name}")
            continue

        admin_role.permissions.append(permission)
        added_count += 1
        logger.info(f"  ✅ Hozzáadva Admin-hez: {perm_name}")

    db.commit()
    logger.info(f"✅ Admin role frissítve: {added_count} új jogosultság")

    return added_count


def verify_migration(db: Session):
    """
    Ellenőrzi a migráció eredményét.

    Args:
        db: SQLAlchemy Session
    """
    logger.info("\n📊 Migráció eredményeinek ellenőrzése...")

    # Új permissions ellenőrzése
    for perm_data in NEW_PERMISSIONS:
        perm = db.query(Permission).filter(
            Permission.name == perm_data["name"]
        ).first()

        if perm:
            logger.info(f"  ✅ {perm_data['name']} - OK")
        else:
            logger.error(f"  ❌ {perm_data['name']} - HIÁNYZIK!")

    # Admin role ellenőrzése
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if admin_role:
        admin_perm_names = [p.name for p in admin_role.permissions]
        logger.info(f"\n  Admin role jogosultságok ({len(admin_role.permissions)} db):")
        for perm_name in ADMIN_PERMISSIONS:
            if perm_name in admin_perm_names:
                logger.info(f"    ✅ {perm_name}")
            else:
                logger.warning(f"    ⚠️  {perm_name} - HIÁNYZIK!")

    logger.info("\n✅ Migráció ellenőrzés befejezve")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Fő migráció folyamat.
    """
    logger.info("=" * 70)
    logger.info("🚀 RBAC Permissions Migration - V3.0 Phase X")
    logger.info("=" * 70)

    try:
        # 1. Adatbázis inicializálás
        logger.info("\n1️⃣  Adatbázis kapcsolat...")
        init_db()
        logger.info("✅ Adatbázis kapcsolat OK")

        # 2. Session létrehozása
        db = SessionLocal()

        try:
            # 3. Permissions hozzáadása
            logger.info("\n2️⃣  Permissions hozzáadása...")
            permissions_map, stats = add_permissions(db)

            # 4. Admin role frissítése
            logger.info("\n3️⃣  Admin role frissítése...")
            admin_updated = update_admin_role(db, permissions_map)

            # 5. Ellenőrzés
            logger.info("\n4️⃣  Ellenőrzés...")
            verify_migration(db)

            logger.info("\n" + "=" * 70)
            logger.info("🎉 MIGRÁCIÓ SIKERES!")
            logger.info("=" * 70)
            logger.info(f"\n📊 ÖSSZESÍTÉS:")
            logger.info(f"  • Új permissions: {stats['added']}")
            logger.info(f"  • Meglévő permissions: {stats['skipped']}")
            logger.info(f"  • Admin role új jogosultságok: {admin_updated}")
            logger.info("")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ HIBA a migráció során: {str(e)}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
