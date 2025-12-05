"""
Menu Seed Data Import Script
Sprint D6: Menu Model V1 Implementation

Import menu data from C:\Codex\resti-menu\data\menu.json into new Menu V1 tables.
Best-effort mapping - fine-tuning can be done later via admin interface.

Usage:
    cd backend/service_menu
    python -m scripts.import_menu_seed_data
"""

import json
import sys
import os
from decimal import Decimal
from typing import Dict, List, Any

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy.orm import Session
from backend.service_menu.database import SessionLocal, engine
from backend.service_menu.models.menu import (
    MenuCategory,
    MenuItem,
    MenuItemVariant,
    ModifierGroup,
    ModifierOption,
    ModifierAssignment,
    SelectionType,
)


# Path to menu.json
MENU_JSON_PATH = r"C:\Codex\resti-menu\data\menu.json"


def load_menu_json() -> Dict[str, Any]:
    """Load menu.json file"""
    print(f"Loading menu data from {MENU_JSON_PATH}...")
    with open(MENU_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def import_categories(db: Session, categories_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Import categories and return mapping of old ID to new ID

    Args:
        db: Database session
        categories_data: List of category dicts from menu.json

    Returns:
        Dict mapping old category IDs to new database IDs
    """
    print(f"\nImporting {len(categories_data)} categories...")
    category_map = {}

    for idx, cat_data in enumerate(categories_data):
        old_id = cat_data.get("id")
        name_dict = cat_data.get("name", {})
        name = name_dict.get("hu", old_id)  # Default to Hungarian name

        # Create category
        category = MenuCategory(
            name=name,
            description=f"Imported from menu.json: {old_id}",
            parent_id=None,  # Flat structure for now
            position=idx,
            is_active=True
        )
        db.add(category)
        db.flush()  # Get the ID without committing

        category_map[old_id] = category.id
        print(f"  - Created category: {name} (old: {old_id}, new: {category.id})")

    db.commit()
    print(f"✓ Imported {len(category_map)} categories")
    return category_map


def import_items(db: Session, categories_data: List[Dict[str, Any]], category_map: Dict[str, int]) -> Dict[str, int]:
    """
    Import menu items and return mapping of old ID to new ID

    Args:
        db: Database session
        categories_data: List of category dicts from menu.json
        category_map: Mapping of old category IDs to new database IDs

    Returns:
        Dict mapping old item IDs to new database IDs
    """
    print(f"\nImporting menu items...")
    item_map = {}
    total_items = 0

    for cat_data in categories_data:
        cat_old_id = cat_data.get("id")
        cat_new_id = category_map.get(cat_old_id)

        items = cat_data.get("items", [])
        for item_data in items:
            old_id = item_data.get("id")
            name_dict = item_data.get("name", {})
            name = name_dict.get("hu", old_id)

            desc_dict = item_data.get("description", {})
            description = desc_dict.get("hu", None)

            # Get price (convert from integer cents to decimal)
            price_data = item_data.get("price", {})
            price_value = price_data.get("value", 0)
            price_gross = Decimal(price_value) / Decimal(100) if price_value else Decimal("0.00")

            # Determine channel flags (default: dine_in only)
            group = item_data.get("group", "food")
            channel_flags = {
                "dine_in": True,
                "takeaway": True,
                "delivery": False  # Default: no delivery
            }

            # Store original data in metadata
            metadata_json = {
                "old_id": old_id,
                "subtitle": item_data.get("subtitle", {}),
                "image": item_data.get("image", {}),
                "tags": item_data.get("tags", []),
                "allergens": item_data.get("allergens", []),
                "available_extras": item_data.get("available_extras", []),
                "option_groups": item_data.get("option_groups", []),
                "homepage_featured": item_data.get("homepage_featured", False),
            }

            # Create item
            item = MenuItem(
                category_id=cat_new_id,
                name=name,
                description=description,
                base_price_gross=price_gross,
                vat_rate_dine_in=Decimal("5.00"),  # Hungary dine-in VAT
                vat_rate_takeaway=Decimal("27.00"),  # Hungary takeaway VAT
                is_active=item_data.get("active", True),
                channel_flags=channel_flags,
                metadata_json=metadata_json
            )
            db.add(item)
            db.flush()

            item_map[old_id] = item.id
            total_items += 1

            if total_items % 50 == 0:
                print(f"  - Imported {total_items} items...")

    db.commit()
    print(f"✓ Imported {total_items} menu items")
    return item_map


def import_sample_modifiers(db: Session) -> None:
    """
    Import sample modifier groups and options
    (Since menu.json doesn't have explicit modifier data, create some common examples)

    Args:
        db: Database session
    """
    print(f"\nCreating sample modifier groups...")

    # 1. Bun Type (Required Single)
    bun_group = ModifierGroup(
        name="Zsemle típus",
        description="Válassz hamburger zsemlét",
        selection_type=SelectionType.REQUIRED_SINGLE,
        min_select=1,
        max_select=1,
        position=0,
        is_active=True
    )
    db.add(bun_group)
    db.flush()

    bun_options = [
        ("Normál Resti Burger Zsemle", Decimal("0.00"), True),
        ("Szezámmagos Zsemle", Decimal("0.00"), False),
        ("Édes Hamburger Zsemle", Decimal("0.00"), False),
        ("Gluténmentes Zsemle", Decimal("500.00"), False),
    ]
    for name, price_delta, is_default in bun_options:
        option = ModifierOption(
            group_id=bun_group.id,
            name=name,
            price_delta_gross=price_delta,
            is_default=is_default,
            is_active=True
        )
        db.add(option)

    print(f"  - Created group: {bun_group.name} with {len(bun_options)} options")

    # 2. Extra Toppings (Optional Multiple)
    extras_group = ModifierGroup(
        name="Extra feltétek",
        description="Válassz extra feltéteket",
        selection_type=SelectionType.OPTIONAL_MULTIPLE,
        min_select=0,
        max_select=None,  # Unlimited
        position=1,
        is_active=True
    )
    db.add(extras_group)
    db.flush()

    extra_options = [
        ("Extra húspogácsa", Decimal("650.00"), False),
        ("Extra bacon", Decimal("350.00"), False),
        ("Extra cheddar sajt", Decimal("250.00"), False),
        ("Extra camembert sajt", Decimal("400.00"), False),
        ("Grillezett ananász", Decimal("200.00"), False),
    ]
    for name, price_delta, is_default in extra_options:
        option = ModifierOption(
            group_id=extras_group.id,
            name=name,
            price_delta_gross=price_delta,
            is_default=is_default,
            is_active=True
        )
        db.add(option)

    print(f"  - Created group: {extras_group.name} with {len(extra_options)} options")

    # 3. Side Dish (Optional Single)
    side_group = ModifierGroup(
        name="Köret választás",
        description="Válassz köretet",
        selection_type=SelectionType.OPTIONAL_SINGLE,
        min_select=0,
        max_select=1,
        position=2,
        is_active=True
    )
    db.add(side_group)
    db.flush()

    side_options = [
        ("Nincs köret", Decimal("0.00"), True),
        ("Sült krumpli", Decimal("500.00"), False),
        ("Édesburgonyás hasáb", Decimal("600.00"), False),
        ("Rizs", Decimal("400.00"), False),
    ]
    for name, price_delta, is_default in side_options:
        option = ModifierOption(
            group_id=side_group.id,
            name=name,
            price_delta_gross=price_delta,
            is_default=is_default,
            is_active=True
        )
        db.add(option)

    print(f"  - Created group: {side_group.name} with {len(side_options)} options")

    db.commit()
    print(f"✓ Created 3 sample modifier groups with options")


def main():
    """Main import function"""
    print("=" * 60)
    print("Menu V1 Seed Data Import")
    print("=" * 60)

    # Check if menu.json exists
    if not os.path.exists(MENU_JSON_PATH):
        print(f"ERROR: menu.json not found at {MENU_JSON_PATH}")
        print("Please ensure the file exists and try again.")
        sys.exit(1)

    # Load menu data
    try:
        menu_data = load_menu_json()
    except Exception as e:
        print(f"ERROR loading menu.json: {e}")
        sys.exit(1)

    # Create database session
    db = SessionLocal()

    try:
        # Import categories
        categories_data = menu_data.get("categories", [])
        category_map = import_categories(db, categories_data)

        # Import items
        item_map = import_items(db, categories_data, category_map)

        # Import sample modifiers
        import_sample_modifiers(db)

        print("\n" + "=" * 60)
        print("Import Summary:")
        print(f"  - Categories: {len(category_map)}")
        print(f"  - Items: {len(item_map)}")
        print(f"  - Modifier Groups: 3 (sample)")
        print("=" * 60)
        print("\n✓ Import completed successfully!")
        print("\nNote: This is a best-effort import.")
        print("You can fine-tune data via admin interface later.")

    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
