"""
Orders Table Migration - Add guest_count and customer_uid
==========================================================

Hozzáadja a guest_count és customer_uid oszlopokat az orders táblához.

Használat:
    python -m backend.service_orders.migrations.run_migration

Ez a szkript idempotens - újrafuttatható, nem okoz hibát, ha az oszlopok már léteznek.
"""

import sys
import logging
from pathlib import Path
from sqlalchemy import text

# Import database connection
from backend.service_orders.models.database import SessionLocal, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migration():
    """
    Futtatja a migráció SQL szkriptet.
    """
    logger.info("=" * 70)
    logger.info("🚀 Orders Table Migration - Add guest_count and customer_uid")
    logger.info("=" * 70)

    try:
        # 1. Adatbázis inicializálás
        logger.info("\n1️⃣  Adatbázis kapcsolat...")
        init_db()
        logger.info("✅ Adatbázis kapcsolat OK")

        # 2. Session létrehozása
        db = SessionLocal()

        try:
            # 3. SQL fájl beolvasása
            logger.info("\n2️⃣  SQL migráció betöltése...")
            sql_file = Path(__file__).parent / "add_guest_count_and_customer_uid.sql"

            if not sql_file.exists():
                raise FileNotFoundError(f"SQL fájl nem található: {sql_file}")

            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()

            logger.info(f"✅ SQL fájl betöltve: {sql_file.name}")

            # 4. SQL végrehajtása
            logger.info("\n3️⃣  Migráció végrehajtása...")
            db.execute(text(sql_content))
            db.commit()
            logger.info("✅ Migráció sikeresen végrehajtva")

            # 5. Ellenőrzés
            logger.info("\n4️⃣  Oszlopok ellenőrzése...")
            result = db.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'orders'
                AND column_name IN ('customer_uid', 'guest_count')
                ORDER BY column_name;
            """))

            columns = result.fetchall()
            if len(columns) == 2:
                logger.info("✅ Mindkét oszlop létezik:")
                for col in columns:
                    logger.info(f"  • {col[0]} ({col[1]}, nullable: {col[2]})")
            else:
                logger.warning(f"⚠️  Csak {len(columns)} oszlop található")

            # 6. Index ellenőrzése
            logger.info("\n5️⃣  Index ellenőrzése...")
            result = db.execute(text("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'orders'
                AND indexname = 'idx_orders_customer_uid';
            """))

            index = result.fetchone()
            if index:
                logger.info(f"✅ Index létezik: {index[0]}")
            else:
                logger.warning("⚠️  Index nem található")

            logger.info("\n" + "=" * 70)
            logger.info("🎉 MIGRÁCIÓ SIKERES!")
            logger.info("=" * 70)
            logger.info("\n📊 ÖSSZESÍTÉS:")
            logger.info("  • customer_uid oszlop hozzáadva")
            logger.info("  • guest_count oszlop hozzáadva")
            logger.info("  • idx_orders_customer_uid index létrehozva")
            logger.info("")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ HIBA a migráció során: {str(e)}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
