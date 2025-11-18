"""
Database Seeding Script - Demo Data
====================================

Ez a script feltölti az adatbázist demo adatokkal:
- Tables (Asztalok) - service_orders
- Categories (Kategóriák) - service_menu
- Products (Termékek) - service_menu

Használat:
    python seed_demo_data.py

Előfeltétel:
    - Docker Compose fut (docker-compose up -d)
    - PostgreSQL adatbázis elérhető (localhost:5432)
    - seed_rbac.py már lefutott (Admin felhasználó létezik)

FIGYELEM: Ez a script development/testing célokra készült.
Production környezetben használj Alembic migration-öket!
"""

import sys
import os
import logging
from typing import List, Dict
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import models from respective services
from backend.service_orders.models.table import Table
from backend.service_orders.models.database import Base as OrdersBase

from backend.service_menu.models.category import Category
from backend.service_menu.models.product import Product
from backend.service_menu.models.base import Base as MenuBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database URL - from environment or default
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://pos_user:pos_password_dev@localhost:5432/pos_db'
)

# SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

# SessionLocal factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================================
# DEMO DATA DEFINITIONS
# ============================================================================

DEMO_TABLES = [
    {
        "table_number": "A1",
        "position_x": 100,
        "position_y": 100,
        "capacity": 4
    },
    {
        "table_number": "A2",
        "position_x": 250,
        "position_y": 100,
        "capacity": 4
    },
    {
        "table_number": "A3",
        "position_x": 400,
        "position_y": 100,
        "capacity": 6
    },
    {
        "table_number": "A4",
        "position_x": 100,
        "position_y": 300,
        "capacity": 2
    },
    {
        "table_number": "Terasz 1",
        "position_x": 600,
        "position_y": 100,
        "capacity": 6
    },
    {
        "table_number": "Terasz 2",
        "position_x": 600,
        "position_y": 300,
        "capacity": 8
    },
    {
        "table_number": "Terasz 3",
        "position_x": 750,
        "position_y": 100,
        "capacity": 4
    },
    {
        "table_number": "VIP 1",
        "position_x": 900,
        "position_y": 200,
        "capacity": 6
    },
    {
        "table_number": "VIP 2",
        "position_x": 900,
        "position_y": 400,
        "capacity": 8
    },
]

DEMO_CATEGORIES = [
    {
        "name": "Levesek",
        "parent_id": None
    },
    {
        "name": "Főételek",
        "parent_id": None
    },
    {
        "name": "Hamburgerek",
        "parent_id": None
    },
    {
        "name": "Italok",
        "parent_id": None
    },
    {
        "name": "Desszertek",
        "parent_id": None
    },
]

DEMO_PRODUCTS = [
    # Levesek
    {
        "name": "Gulyásleves",
        "description": "Hagyományos magyar gulyásleves marhahúsból, zöldségekkel",
        "base_price": Decimal("1290.00"),
        "category_name": "Levesek",
        "sku": "SOUP-GUL-001",
        "is_active": True
    },
    {
        "name": "Tyúkhúsleves",
        "description": "Házi tyúkhúsleves cérnametélttel és zöldségekkel",
        "base_price": Decimal("1190.00"),
        "category_name": "Levesek",
        "sku": "SOUP-TYU-001",
        "is_active": True
    },
    {
        "name": "Gombakrémleves",
        "description": "Krémes gombakrémleves pirított kenyérkockákkal",
        "base_price": Decimal("990.00"),
        "category_name": "Levesek",
        "sku": "SOUP-GOM-001",
        "is_active": True
    },

    # Főételek
    {
        "name": "Rántott hús burgonyával",
        "description": "Sertés rántott hús hasábburgonyával és tartármártással",
        "base_price": Decimal("2490.00"),
        "category_name": "Főételek",
        "sku": "MAIN-RAN-001",
        "is_active": True
    },
    {
        "name": "Pörkölt galuskával",
        "description": "Marhapörkölt házi galuskával",
        "base_price": Decimal("2690.00"),
        "category_name": "Főételek",
        "sku": "MAIN-POR-001",
        "is_active": True
    },
    {
        "name": "Bécsi szelet",
        "description": "Borjú bécsi szelet burgonyasalátával",
        "base_price": Decimal("3290.00"),
        "category_name": "Főételek",
        "sku": "MAIN-BEC-001",
        "is_active": True
    },
    {
        "name": "Grillezett csirkemell",
        "description": "Grillezett csirkemell zöldségekkel és rizzsel",
        "base_price": Decimal("2390.00"),
        "category_name": "Főételek",
        "sku": "MAIN-CSI-001",
        "is_active": True
    },

    # Hamburgerek
    {
        "name": "Classic Burger",
        "description": "100% marhahús, saláta, paradicsom, lilahagyma, csemegeuborka, majonéz",
        "base_price": Decimal("1990.00"),
        "category_name": "Hamburgerek",
        "sku": "BURG-CLA-001",
        "is_active": True
    },
    {
        "name": "Cheese Burger",
        "description": "Marhahús, dupla cheddar sajt, bacon, BBQ szósz",
        "base_price": Decimal("2290.00"),
        "category_name": "Hamburgerek",
        "sku": "BURG-CHE-001",
        "is_active": True
    },
    {
        "name": "BBQ Burger",
        "description": "Marhahús, karamellizált hagyma, bacon, cheddar, BBQ szósz",
        "base_price": Decimal("2490.00"),
        "category_name": "Hamburgerek",
        "sku": "BURG-BBQ-001",
        "is_active": True
    },
    {
        "name": "Vega Burger",
        "description": "Vegetáriánus burger grillezett zöldségekkel",
        "base_price": Decimal("1790.00"),
        "category_name": "Hamburgerek",
        "sku": "BURG-VEG-001",
        "is_active": True
    },

    # Italok
    {
        "name": "Coca Cola (0.33l)",
        "description": "Üdítőital",
        "base_price": Decimal("490.00"),
        "category_name": "Italok",
        "sku": "DRINK-COLA-033",
        "is_active": True
    },
    {
        "name": "Sprite (0.33l)",
        "description": "Citromos üdítő",
        "base_price": Decimal("490.00"),
        "category_name": "Italok",
        "sku": "DRINK-SPR-033",
        "is_active": True
    },
    {
        "name": "Ásványvíz (0.5l)",
        "description": "Szénsavas ásványvíz",
        "base_price": Decimal("390.00"),
        "category_name": "Italok",
        "sku": "DRINK-WAT-050",
        "is_active": True
    },
    {
        "name": "Soproni sör (0.5l)",
        "description": "Világos sör csapolva",
        "base_price": Decimal("690.00"),
        "category_name": "Italok",
        "sku": "DRINK-BEE-SOP",
        "is_active": True
    },
    {
        "name": "Egri Bikavér (2dl)",
        "description": "Vörösbor pohárban",
        "base_price": Decimal("790.00"),
        "category_name": "Italok",
        "sku": "DRINK-WIN-EGR",
        "is_active": True
    },

    # Desszertek
    {
        "name": "Palacsinta",
        "description": "Házi palacsinta kakaós vagy lekváros töltelékkel",
        "base_price": Decimal("890.00"),
        "category_name": "Desszertek",
        "sku": "DESS-PAL-001",
        "is_active": True
    },
    {
        "name": "Somlói galuska",
        "description": "Klasszikus somlói galuska tejszínhabbal",
        "base_price": Decimal("1190.00"),
        "category_name": "Desszertek",
        "sku": "DESS-SOM-001",
        "is_active": True
    },
    {
        "name": "Tiramisu",
        "description": "Olasz desszert kávéval és mascarponéval",
        "base_price": Decimal("1390.00"),
        "category_name": "Desszertek",
        "sku": "DESS-TIR-001",
        "is_active": True
    },
]


# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================

def seed_tables(db: Session) -> List[Table]:
    """
    Feltölti az adatbázist demo asztalokkal (tables).

    Args:
        db: SQLAlchemy Session

    Returns:
        List[Table]: Létrehozott/meglévő Table objektumok
    """
    logger.info("🪑 Asztalok (Tables) feltöltése...")

    tables_list = []

    for table_data in DEMO_TABLES:
        # Ellenőrizzük, hogy már létezik-e
        existing = db.query(Table).filter(
            Table.table_number == table_data["table_number"]
        ).first()

        if existing:
            logger.info(f"  ⏭️  Asztal már létezik: {table_data['table_number']}")
            tables_list.append(existing)
            continue

        # Új asztal létrehozása
        table = Table(
            table_number=table_data["table_number"],
            position_x=table_data["position_x"],
            position_y=table_data["position_y"],
            capacity=table_data["capacity"]
        )

        db.add(table)
        tables_list.append(table)
        logger.info(f"  ✅ Létrehozva: {table_data['table_number']} (kapacitás: {table_data['capacity']} fő)")

    db.commit()
    logger.info(f"✅ {len(tables_list)} asztal feltöltve")

    return tables_list


def seed_categories(db: Session) -> Dict[str, Category]:
    """
    Feltölti az adatbázist demo kategóriákkal (categories).

    Args:
        db: SQLAlchemy Session

    Returns:
        Dict[str, Category]: Category objektumok name alapján indexelve
    """
    logger.info("📂 Kategóriák (Categories) feltöltése...")

    categories_map = {}

    for cat_data in DEMO_CATEGORIES:
        # Ellenőrizzük, hogy már létezik-e
        existing = db.query(Category).filter(
            Category.name == cat_data["name"]
        ).first()

        if existing:
            logger.info(f"  ⏭️  Kategória már létezik: {cat_data['name']}")
            categories_map[cat_data["name"]] = existing
            continue

        # Új kategória létrehozása
        category = Category(
            name=cat_data["name"],
            parent_id=cat_data["parent_id"]
        )

        db.add(category)
        categories_map[cat_data["name"]] = category
        logger.info(f"  ✅ Létrehozva: {cat_data['name']}")

    db.commit()
    logger.info(f"✅ {len(categories_map)} kategória feltöltve")

    return categories_map


def seed_products(db: Session, categories_map: Dict[str, Category]) -> List[Product]:
    """
    Feltölti az adatbázist demo termékekkel (products).

    Args:
        db: SQLAlchemy Session
        categories_map: Category objektumok name alapján indexelve

    Returns:
        List[Product]: Létrehozott/meglévő Product objektumok
    """
    logger.info("🍔 Termékek (Products) feltöltése...")

    products_list = []

    for prod_data in DEMO_PRODUCTS:
        # Ellenőrizzük, hogy már létezik-e (SKU alapján)
        existing = db.query(Product).filter(
            Product.sku == prod_data["sku"]
        ).first()

        if existing:
            logger.info(f"  ⏭️  Termék már létezik: {prod_data['name']} ({prod_data['sku']})")
            products_list.append(existing)
            continue

        # Kategória lekérdezése
        category = categories_map.get(prod_data["category_name"])
        if not category:
            logger.warning(f"  ⚠️  Hiányzó kategória: {prod_data['category_name']} - termék kihagyva: {prod_data['name']}")
            continue

        # Új termék létrehozása
        product = Product(
            name=prod_data["name"],
            description=prod_data["description"],
            base_price=prod_data["base_price"],
            category_id=category.id,
            sku=prod_data["sku"],
            is_active=prod_data["is_active"]
        )

        db.add(product)
        products_list.append(product)
        logger.info(f"  ✅ Létrehozva: {prod_data['name']} - {prod_data['base_price']} Ft ({prod_data['category_name']})")

    db.commit()
    logger.info(f"✅ {len(products_list)} termék feltöltve")

    return products_list


def verify_seeding(db: Session):
    """
    Ellenőrzi, hogy a seeding sikeresen lefutott-e.

    Args:
        db: SQLAlchemy Session
    """
    logger.info("\n📊 Seeding eredmények ellenőrzése...")

    # Tables count
    table_count = db.query(Table).count()
    logger.info(f"  Asztalok (Tables): {table_count} db")

    # Categories count
    category_count = db.query(Category).count()
    logger.info(f"  Kategóriák (Categories): {category_count} db")

    # Products count
    product_count = db.query(Product).count()
    logger.info(f"  Termékek (Products): {product_count} db")

    # Products by category
    logger.info("\n  Termékek kategóriánként:")
    categories = db.query(Category).all()
    for cat in categories:
        prod_count = db.query(Product).filter(Product.category_id == cat.id).count()
        logger.info(f"    - {cat.name}: {prod_count} termék")

    logger.info("✅ Seeding ellenőrzés befejezve")


def init_tables():
    """
    Adatbázis táblák inicializálása mindkét Base-hez.

    FIGYELEM: Ez csak development/testing során használandó.
    Production környezetben használj Alembic migration-öket!
    """
    logger.info("🔧 Adatbázis táblák inicializálása...")

    # Create tables for both services
    OrdersBase.metadata.create_all(bind=engine)
    MenuBase.metadata.create_all(bind=engine)

    logger.info("✅ Táblák létrehozva (ha még nem léteztek)")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Fő seeding folyamat.

    1. Adatbázis táblák inicializálása (create_all)
    2. Tables (Asztalok) feltöltése
    3. Categories (Kategóriák) feltöltése
    4. Products (Termékek) feltöltése
    5. Eredmények ellenőrzése
    """
    logger.info("=" * 70)
    logger.info("🚀 DEMO DATA Seeding - RestiApp POS System")
    logger.info("=" * 70)

    try:
        # 1. Adatbázis inicializálás
        logger.info("\n1️⃣  Adatbázis kapcsolat ellenőrzése...")
        logger.info(f"   DATABASE_URL: {DATABASE_URL}")
        init_tables()

        # 2. Session létrehozása
        db = SessionLocal()

        try:
            # 3. Tables seeding
            logger.info("\n2️⃣  Asztalok (Tables) seeding...")
            tables = seed_tables(db)

            # 4. Categories seeding
            logger.info("\n3️⃣  Kategóriák (Categories) seeding...")
            categories_map = seed_categories(db)

            # 5. Products seeding
            logger.info("\n4️⃣  Termékek (Products) seeding...")
            products = seed_products(db, categories_map)

            # 6. Verification
            logger.info("\n5️⃣  Verification...")
            verify_seeding(db)

            logger.info("\n" + "=" * 70)
            logger.info("🎉 SEEDING SIKERES!")
            logger.info("=" * 70)
            logger.info("\n📝 KÖVETKEZŐ LÉPÉSEK:")
            logger.info("  1. Ellenőrizd az adatbázis tartalmát:")
            logger.info("     docker exec -it pos-postgres psql -U pos_user -d pos_db")
            logger.info("     SELECT * FROM tables;")
            logger.info("     SELECT * FROM categories;")
            logger.info("     SELECT * FROM products;")
            logger.info("  2. Teszteld az API végpontokat:")
            logger.info("     http://localhost:8002/tables")
            logger.info("     http://localhost:8001/categories")
            logger.info("     http://localhost:8001/products")
            logger.info("")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ HIBA a seeding során: {str(e)}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
