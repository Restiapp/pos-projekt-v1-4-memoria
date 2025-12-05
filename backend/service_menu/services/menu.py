"""
Service layer for Menu V1 operations
Sprint D6: Menu Model V1 Implementation

This module provides business logic and database operations for:
- CRUD operations on menu entities
- Menu tree retrieval with channel filtering
- Modifier assignment management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_

from backend.service_menu.models.menu import (
    MenuCategory,
    MenuItem,
    MenuItemVariant,
    MenuModifierGroup,
    MenuModifierOption,
    MenuModifierAssignment,
)
from backend.service_menu.schemas.menu import (
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemVariantCreate,
    MenuItemVariantUpdate,
    ModifierGroupCreate,
    ModifierGroupUpdate,
    ModifierOptionCreate,
    ModifierOptionUpdate,
    ModifierAssignmentCreate,
    ModifierAssignmentUpdate,
    MenuCategoryTreeOut,
)


# ===========================
# MenuCategory Service
# ===========================

def get_category(db: Session, category_id: int) -> Optional[MenuCategory]:
    """Get category by ID"""
    return db.query(MenuCategory).filter(MenuCategory.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[MenuCategory]:
    """Get all categories with pagination"""
    query = db.query(MenuCategory)
    if active_only:
        query = query.filter(MenuCategory.is_active == True)
    return query.order_by(MenuCategory.position).offset(skip).limit(limit).all()


def create_category(db: Session, category: MenuCategoryCreate) -> MenuCategory:
    """Create a new category"""
    db_category = MenuCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: MenuCategoryUpdate) -> Optional[MenuCategory]:
    """Update an existing category"""
    db_category = get_category(db, category_id)
    if not db_category:
        return None

    update_data = category.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category"""
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    db.delete(db_category)
    db.commit()
    return True


# ===========================
# MenuItem Service
# ===========================

def get_item(db: Session, item_id: int) -> Optional[MenuItem]:
    """Get menu item by ID with variants and modifiers"""
    return (
        db.query(MenuItem)
        .options(
            selectinload(MenuItem.variants),
            selectinload(MenuItem.modifier_assignments).selectinload(MenuModifierAssignment.group)
        )
        .filter(MenuItem.id == item_id)
        .first()
    )


def get_items(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None, active_only: bool = False) -> List[MenuItem]:
    """Get all menu items with pagination and optional filtering"""
    query = db.query(MenuItem)
    if category_id:
        query = query.filter(MenuItem.category_id == category_id)
    if active_only:
        query = query.filter(MenuItem.is_active == True)
    return query.offset(skip).limit(limit).all()


def create_item(db: Session, item: MenuItemCreate) -> MenuItem:
    """Create a new menu item"""
    db_item = MenuItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item: MenuItemUpdate) -> Optional[MenuItem]:
    """Update an existing menu item"""
    db_item = get_item(db, item_id)
    if not db_item:
        return None

    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int) -> bool:
    """Delete a menu item"""
    db_item = get_item(db, item_id)
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True


# ===========================
# MenuItemVariant Service
# ===========================

def get_variant(db: Session, variant_id: int) -> Optional[MenuItemVariant]:
    """Get variant by ID"""
    return db.query(MenuItemVariant).filter(MenuItemVariant.id == variant_id).first()


def get_variants_by_item(db: Session, item_id: int) -> List[MenuItemVariant]:
    """Get all variants for a menu item"""
    return db.query(MenuItemVariant).filter(MenuItemVariant.item_id == item_id).all()


def create_variant(db: Session, variant: MenuItemVariantCreate) -> MenuItemVariant:
    """Create a new menu item variant"""
    db_variant = MenuItemVariant(**variant.model_dump())
    db.add(db_variant)
    db.commit()
    db.refresh(db_variant)
    return db_variant


def update_variant(db: Session, variant_id: int, variant: MenuItemVariantUpdate) -> Optional[MenuItemVariant]:
    """Update an existing variant"""
    db_variant = get_variant(db, variant_id)
    if not db_variant:
        return None

    update_data = variant.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_variant, key, value)

    db.commit()
    db.refresh(db_variant)
    return db_variant


def delete_variant(db: Session, variant_id: int) -> bool:
    """Delete a variant"""
    db_variant = get_variant(db, variant_id)
    if not db_variant:
        return False
    db.delete(db_variant)
    db.commit()
    return True


# ===========================
# ModifierGroup Service
# ===========================

def get_modifier_group(db: Session, group_id: int) -> Optional[MenuModifierGroup]:
    """Get modifier group by ID with options"""
    return (
        db.query(MenuModifierGroup)
        .options(selectinload(MenuModifierGroup.options))
        .filter(MenuModifierGroup.id == group_id)
        .first()
    )


def get_modifier_groups(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[MenuModifierGroup]:
    """Get all modifier groups with pagination"""
    query = db.query(MenuModifierGroup)
    if active_only:
        query = query.filter(MenuModifierGroup.is_active == True)
    return query.order_by(MenuModifierGroup.position).offset(skip).limit(limit).all()


def create_modifier_group(db: Session, group: ModifierGroupCreate) -> MenuModifierGroup:
    """Create a new modifier group"""
    db_group = MenuModifierGroup(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def update_modifier_group(db: Session, group_id: int, group: ModifierGroupUpdate) -> Optional[MenuModifierGroup]:
    """Update an existing modifier group"""
    db_group = get_modifier_group(db, group_id)
    if not db_group:
        return None

    update_data = group.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_group, key, value)

    db.commit()
    db.refresh(db_group)
    return db_group


def delete_modifier_group(db: Session, group_id: int) -> bool:
    """Delete a modifier group"""
    db_group = get_modifier_group(db, group_id)
    if not db_group:
        return False
    db.delete(db_group)
    db.commit()
    return True


# ===========================
# ModifierOption Service
# ===========================

def get_modifier_option(db: Session, option_id: int) -> Optional[MenuModifierOption]:
    """Get modifier option by ID"""
    return db.query(MenuModifierOption).filter(MenuModifierOption.id == option_id).first()


def get_modifier_options_by_group(db: Session, group_id: int) -> List[MenuModifierOption]:
    """Get all options for a modifier group"""
    return db.query(MenuModifierOption).filter(MenuModifierOption.group_id == group_id).all()


def create_modifier_option(db: Session, option: ModifierOptionCreate) -> MenuModifierOption:
    """Create a new modifier option"""
    db_option = MenuModifierOption(**option.model_dump())
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    return db_option


def update_modifier_option(db: Session, option_id: int, option: ModifierOptionUpdate) -> Optional[MenuModifierOption]:
    """Update an existing modifier option"""
    db_option = get_modifier_option(db, option_id)
    if not db_option:
        return None

    update_data = option.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_option, key, value)

    db.commit()
    db.refresh(db_option)
    return db_option


def delete_modifier_option(db: Session, option_id: int) -> bool:
    """Delete a modifier option"""
    db_option = get_modifier_option(db, option_id)
    if not db_option:
        return False
    db.delete(db_option)
    db.commit()
    return True


# ===========================
# ModifierAssignment Service
# ===========================

def get_modifier_assignment(db: Session, assignment_id: int) -> Optional[MenuModifierAssignment]:
    """Get modifier assignment by ID"""
    return db.query(MenuModifierAssignment).filter(MenuModifierAssignment.id == assignment_id).first()


def get_modifier_assignments_by_item(db: Session, item_id: int) -> List[MenuModifierAssignment]:
    """Get all modifier assignments for a menu item"""
    return (
        db.query(MenuModifierAssignment)
        .options(
            selectinload(MenuModifierAssignment.group).selectinload(MenuModifierGroup.options)
        )
        .filter(MenuModifierAssignment.item_id == item_id)
        .order_by(MenuModifierAssignment.position)
        .all()
    )


def get_modifier_assignments_by_category(db: Session, category_id: int) -> List[MenuModifierAssignment]:
    """Get all modifier assignments for a category"""
    return (
        db.query(MenuModifierAssignment)
        .options(
            selectinload(MenuModifierAssignment.group).selectinload(MenuModifierGroup.options)
        )
        .filter(MenuModifierAssignment.category_id == category_id)
        .order_by(MenuModifierAssignment.position)
        .all()
    )


def create_modifier_assignment(db: Session, assignment: ModifierAssignmentCreate) -> MenuModifierAssignment:
    """Create a new modifier assignment"""
    db_assignment = MenuModifierAssignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def update_modifier_assignment(db: Session, assignment_id: int, assignment: ModifierAssignmentUpdate) -> Optional[MenuModifierAssignment]:
    """Update an existing modifier assignment"""
    db_assignment = get_modifier_assignment(db, assignment_id)
    if not db_assignment:
        return None

    update_data = assignment.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_assignment, key, value)

    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def delete_modifier_assignment(db: Session, assignment_id: int) -> bool:
    """Delete a modifier assignment"""
    db_assignment = get_modifier_assignment(db, assignment_id)
    if not db_assignment:
        return False
    db.delete(db_assignment)
    db.commit()
    return True


# ===========================
# Menu Tree Service
# ===========================

def get_menu_tree_for_channel(db: Session, channel: str = "dine_in") -> List[Dict[str, Any]]:
    """
    Get full menu tree with categories, items, variants, and modifiers
    filtered by channel availability.

    Args:
        db: Database session
        channel: Channel name (dine_in, takeaway, delivery)

    Returns:
        List of category trees with nested data
    """
    # Get root categories (no parent)
    root_categories = (
        db.query(MenuCategory)
        .filter(MenuCategory.parent_id.is_(None), MenuCategory.is_active == True)
        .order_by(MenuCategory.position)
        .all()
    )

    result = []
    for category in root_categories:
        result.append(_build_category_tree(db, category, channel))

    return result


def _build_category_tree(db: Session, category: MenuCategory, channel: str) -> Dict[str, Any]:
    """
    Recursively build category tree with items and subcategories.
    Helper function for get_menu_tree_for_channel.
    """
    # Get items for this category
    items_query = (
        db.query(MenuItem)
        .options(
            selectinload(MenuItem.variants),
            selectinload(MenuItem.modifier_assignments).selectinload(MenuModifierAssignment.group).selectinload(MenuModifierGroup.options)
        )
        .filter(MenuItem.category_id == category.id, MenuItem.is_active == True)
    )

    # Filter by channel availability
    items = []
    for item in items_query.all():
        if item.channel_flags and item.channel_flags.get(channel, False):
            # Build modifier groups for this item
            modifier_groups = []
            for assignment in item.modifier_assignments:
                if assignment.group.is_active:
                    modifier_groups.append({
                        "id": assignment.group.id,
                        "name": assignment.group.name,
                        "description": assignment.group.description,
                        "selection_type": assignment.group.selection_type.value,
                        "min_select": assignment.group.min_select,
                        "max_select": assignment.group.max_select,
                        "position": assignment.position,
                        "is_active": assignment.group.is_active,
                        "options": [
                            {
                                "id": opt.id,
                                "name": opt.name,
                                "price_delta_gross": float(opt.price_delta_gross),
                                "is_default": opt.is_default,
                                "is_active": opt.is_active,
                            }
                            for opt in assignment.group.options if opt.is_active
                        ]
                    })

            items.append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "base_price_gross": float(item.base_price_gross),
                "vat_rate_dine_in": float(item.vat_rate_dine_in),
                "vat_rate_takeaway": float(item.vat_rate_takeaway),
                "is_active": item.is_active,
                "channel_flags": item.channel_flags,
                "metadata_json": item.metadata_json,
                "variants": [
                    {
                        "id": var.id,
                        "name": var.name,
                        "price_delta": float(var.price_delta),
                        "is_default": var.is_default,
                        "is_active": var.is_active,
                    }
                    for var in item.variants if var.is_active
                ],
                "modifier_groups": modifier_groups,
            })

    # Get subcategories
    subcategories_query = (
        db.query(MenuCategory)
        .filter(MenuCategory.parent_id == category.id, MenuCategory.is_active == True)
        .order_by(MenuCategory.position)
        .all()
    )

    subcategories = [_build_category_tree(db, subcat, channel) for subcat in subcategories_query]

    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "parent_id": category.parent_id,
        "position": category.position,
        "is_active": category.is_active,
        "items": items,
        "subcategories": subcategories,
    }
