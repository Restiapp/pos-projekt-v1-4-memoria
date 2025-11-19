"""
Daily Closure Revenue Fields Migration - V3.0 Task A8
======================================================

Hozzáadja a bevételek aggregálásához szükséges mezőket a daily_closures táblához:
- total_cash: Készpénzes fizetések összege
- total_card: Bankkártyás fizetések összege
- total_szep_card: SZÉP kártya fizetések összege
- total_revenue: Összes bevétel

Használat:
    python -m backend.service_admin.migrations.add_daily_closure_revenue_fields

Ez a szkript idempotens - újrafuttatható, nem okoz hibát ha már léteznek a mezők.
"""

import sys
import logging
from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError

# Import database models
from backend.service_admin.models.database import SessionLocal, init_db, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# MIGRATION SQL
# ============================================================================

MIGRATION_SQL = """
-- Add revenue aggregation fields to daily_closures table
ALTER TABLE daily_closures
ADD COLUMN IF NOT EXISTS total_cash DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS total_card DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS total_szep_card DECIMAL(10, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS total_revenue DECIMAL(10, 2) DEFAULT 0.00;

-- Add comments for documentation
COMMENT ON COLUMN daily_closures.total_cash IS 'Készpénzes fizetések összege';
COMMENT ON COLUMN daily_closures.total_card IS 'Bankkártyás fizetések összege';
COMMENT ON COLUMN daily_closures.total_szep_card IS 'SZÉP kártya fizetések összege';
COMMENT ON COLUMN daily_closures.total_revenue IS 'Összes bevétel';
"""

ROLLBACK_SQL = """
-- Rollback: Remove revenue aggregation fields
ALTER TABLE daily_closures
DROP COLUMN IF EXISTS total_cash,
DROP COLUMN IF EXISTS total_card,
DROP COLUMN IF EXISTS total_szep_card,
DROP COLUMN IF EXISTS total_revenue;
"""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_column_exists(table_name: str, column_name: str) -> bool:
    """
    Ellenőrzi, hogy egy oszlop létezik-e egy táblában.

    Args:
        table_name: Tábla neve
        column_name: Oszlop neve

    Returns:
        bool: True ha létezik, False különben
    """
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def apply_migration():
    """
    Alkalmazza a migrációt - hozzáadja az új mezőket.
    """
    logger.info("=" * 70)
    logger.info("🚀 Daily Closure Revenue Fields Migration - V3.0 Task A8")
    logger.info("=" * 70)

    try:
        # 1. Adatbázis kapcsolat
        logger.info("\n1️⃣  Adatbázis kapcsolat ellenőrzése...")
        init_db()
        logger.info("✅ Adatbázis kapcsolat OK")

        # 2. Ellenőrizzük hogy létezik-e a tábla
        logger.info("\n2️⃣  Tábla ellenőrzése...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if 'daily_closures' not in tables:
            logger.error("❌ A 'daily_closures' tábla nem létezik!")
            sys.exit(1)

        logger.info("✅ daily_closures tábla létezik")

        # 3. Ellenőrizzük az oszlopokat
        logger.info("\n3️⃣  Oszlopok ellenőrzése...")
        columns_to_add = ['total_cash', 'total_card', 'total_szep_card', 'total_revenue']
        existing_columns = []
        missing_columns = []

        for column in columns_to_add:
            if check_column_exists('daily_closures', column):
                existing_columns.append(column)
                logger.info(f"  ⏭️  Oszlop már létezik: {column}")
            else:
                missing_columns.append(column)
                logger.info(f"  ➕ Oszlop hozzáadásra kerül: {column}")

        if not missing_columns:
            logger.info("\n✅ Minden oszlop már létezik - nincs mit migrálni")
            return

        # 4. Migráció alkalmazása
        logger.info("\n4️⃣  Migráció alkalmazása...")
        db = SessionLocal()

        try:
            # PostgreSQL esetén használjuk az ADD COLUMN IF NOT EXISTS-et
            for column in missing_columns:
                sql = f"""
                ALTER TABLE daily_closures
                ADD COLUMN {column} DECIMAL(10, 2) DEFAULT 0.00;
                """
                db.execute(text(sql))
                logger.info(f"  ✅ Oszlop hozzáadva: {column}")

            db.commit()
            logger.info("✅ Migráció sikeresen alkalmazva")

        except OperationalError as e:
            db.rollback()
            logger.error(f"❌ Hiba a migráció során: {str(e)}")
            raise

        finally:
            db.close()

        # 5. Ellenőrzés
        logger.info("\n5️⃣  Ellenőrzés...")
        for column in columns_to_add:
            if check_column_exists('daily_closures', column):
                logger.info(f"  ✅ {column} - OK")
            else:
                logger.error(f"  ❌ {column} - HIÁNYZIK!")

        logger.info("\n" + "=" * 70)
        logger.info("🎉 MIGRÁCIÓ SIKERES!")
        logger.info("=" * 70)
        logger.info(f"\n📊 ÖSSZESÍTÉS:")
        logger.info(f"  • Hozzáadott oszlopok: {len(missing_columns)}")
        logger.info(f"  • Meglévő oszlopok: {len(existing_columns)}")
        logger.info("")

    except Exception as e:
        logger.error(f"❌ HIBA a migráció során: {str(e)}")
        logger.exception(e)
        sys.exit(1)


def rollback_migration():
    """
    Visszavonja a migrációt - eltávolítja az új mezőket.
    """
    logger.info("=" * 70)
    logger.info("⏪ Daily Closure Revenue Fields Migration - ROLLBACK")
    logger.info("=" * 70)

    try:
        logger.info("\n⚠️  FIGYELEM: Ez a művelet ELTÁVOLÍTJA az alábbi oszlopokat:")
        logger.info("  - total_cash")
        logger.info("  - total_card")
        logger.info("  - total_szep_card")
        logger.info("  - total_revenue")
        logger.info("\nFolytatás? (yes/no): ")

        confirmation = input().strip().lower()
        if confirmation != 'yes':
            logger.info("❌ Rollback megszakítva")
            return

        logger.info("\n1️⃣  Rollback alkalmazása...")
        db = SessionLocal()

        try:
            columns_to_drop = ['total_cash', 'total_card', 'total_szep_card', 'total_revenue']

            for column in columns_to_drop:
                if check_column_exists('daily_closures', column):
                    sql = f"ALTER TABLE daily_closures DROP COLUMN {column};"
                    db.execute(text(sql))
                    logger.info(f"  ✅ Oszlop eltávolítva: {column}")
                else:
                    logger.info(f"  ⏭️  Oszlop nem létezik: {column}")

            db.commit()
            logger.info("✅ Rollback sikeresen alkalmazva")

        except OperationalError as e:
            db.rollback()
            logger.error(f"❌ Hiba a rollback során: {str(e)}")
            raise

        finally:
            db.close()

        logger.info("\n✅ ROLLBACK SIKERES!")

    except Exception as e:
        logger.error(f"❌ HIBA a rollback során: {str(e)}")
        logger.exception(e)
        sys.exit(1)


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Fő migráció folyamat.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Daily Closure Revenue Fields Migration'
    )
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback the migration (remove columns)'
    )

    args = parser.parse_args()

    if args.rollback:
        rollback_migration()
    else:
        apply_migration()


if __name__ == "__main__":
    main()
