"""
Menu V1 API Routes
Sprint D6: Menu Model V1 Implementation

This module provides FastAPI endpoints for:
- MenuCategory CRUD
- MenuItem CRUD
- MenuItemVariant CRUD
- ModifierGroup CRUD
- ModifierOption CRUD
- ModifierAssignment CRUD
- GET /menu/tree?channel=X - Full menu tree for channel
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.service_menu.database import get_db_connection
from backend.service_menu.services import menu as menu_service
from backend.service_menu.schemas.menu import (
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuCategoryOut,
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemOut,
    MenuItemVariantCreate,
    MenuItemVariantUpdate,
    MenuItemVariantOut,
    ModifierGroupCreate,
    ModifierGroupUpdate,
    ModifierGroupOut,
    ModifierOptionCreate,
    ModifierOptionUpdate,
    ModifierOptionOut,
    ModifierAssignmentCreate,
    ModifierAssignmentUpdate,
    ModifierAssignmentOut,
)


# Create router with prefix /api/v1/menu
router = APIRouter(
    prefix="/menu",
    tags=["menu-v1"]
)


# ===========================
# MenuCategory Endpoints
# ===========================

@router.get(
    "/categories",
    response_model=List[MenuCategoryOut],
    summary="List all menu categories",
    description="Get all menu categories with optional filtering"
)
def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    active_only: bool = Query(False, description="Filter only active categories"),
    db: Session = Depends(get_db_connection)
):
    """List all menu categories with pagination"""
    return menu_service.get_categories(db, skip=skip, limit=limit, active_only=active_only)


@router.get(
    "/categories/{category_id}",
    response_model=MenuCategoryOut,
    summary="Get category by ID",
    description="Retrieve a single menu category by its ID"
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db_connection)
):
    """Get a specific category by ID"""
    category = menu_service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    return category


@router.post(
    "/categories",
    response_model=MenuCategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    description="Create a new menu category"
)
def create_category(
    category: MenuCategoryCreate,
    db: Session = Depends(get_db_connection)
):
    """Create a new menu category"""
    return menu_service.create_category(db, category)


@router.put(
    "/categories/{category_id}",
    response_model=MenuCategoryOut,
    summary="Update a category",
    description="Update an existing menu category"
)
def update_category(
    category_id: int,
    category: MenuCategoryUpdate,
    db: Session = Depends(get_db_connection)
):
    """Update an existing category"""
    updated = menu_service.update_category(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    return updated


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
    description="Delete a menu category"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db_connection)
):
    """Delete a category"""
    success = menu_service.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")


# ===========================
# MenuItem Endpoints
# ===========================

@router.get(
    "/items",
    response_model=List[MenuItemOut],
    summary="List all menu items",
    description="Get all menu items with optional filtering"
)
def list_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    active_only: bool = Query(False, description="Filter only active items"),
    db: Session = Depends(get_db_connection)
):
    """List all menu items with pagination and filtering"""
    return menu_service.get_items(db, skip=skip, limit=limit, category_id=category_id, active_only=active_only)


@router.get(
    "/items/{item_id}",
    response_model=MenuItemOut,
    summary="Get item by ID",
    description="Retrieve a single menu item by its ID"
)
def get_item(
    item_id: int,
    db: Session = Depends(get_db_connection)
):
    """Get a specific item by ID"""
    item = menu_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


@router.post(
    "/items",
    response_model=MenuItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description="Create a new menu item"
)
def create_item(
    item: MenuItemCreate,
    db: Session = Depends(get_db_connection)
):
    """Create a new menu item"""
    return menu_service.create_item(db, item)


@router.put(
    "/items/{item_id}",
    response_model=MenuItemOut,
    summary="Update an item",
    description="Update an existing menu item"
)
def update_item(
    item_id: int,
    item: MenuItemUpdate,
    db: Session = Depends(get_db_connection)
):
    """Update an existing item"""
    updated = menu_service.update_item(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return updated


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    description="Delete a menu item"
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db_connection)
):
    """Delete an item"""
    success = menu_service.delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


# ===========================
# MenuItemVariant Endpoints
# ===========================

@router.get(
    "/items/{item_id}/variants",
    response_model=List[MenuItemVariantOut],
    summary="List variants for an item",
    description="Get all variants for a specific menu item"
)
def list_variants_by_item(
    item_id: int,
    db: Session = Depends(get_db_connection)
):
    """List all variants for a menu item"""
    return menu_service.get_variants_by_item(db, item_id)


@router.post(
    "/variants",
    response_model=MenuItemVariantOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new variant",
    description="Create a new menu item variant"
)
def create_variant(
    variant: MenuItemVariantCreate,
    db: Session = Depends(get_db_connection)
):
    """Create a new variant"""
    return menu_service.create_variant(db, variant)


@router.put(
    "/variants/{variant_id}",
    response_model=MenuItemVariantOut,
    summary="Update a variant",
    description="Update an existing variant"
)
def update_variant(
    variant_id: int,
    variant: MenuItemVariantUpdate,
    db: Session = Depends(get_db_connection)
):
    """Update an existing variant"""
    updated = menu_service.update_variant(db, variant_id, variant)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Variant {variant_id} not found")
    return updated


@router.delete(
    "/variants/{variant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a variant",
    description="Delete a menu item variant"
)
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db_connection)
):
    """Delete a variant"""
    success = menu_service.delete_variant(db, variant_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Variant {variant_id} not found")


# ===========================
# ModifierGroup Endpoints
# ===========================

@router.get(
    "/modifier-groups",
    response_model=List[ModifierGroupOut],
    summary="List all modifier groups",
    description="Get all modifier groups with optional filtering"
)
def list_modifier_groups(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    active_only: bool = Query(False, description="Filter only active groups"),
    db: Session = Depends(get_db_connection)
):
    """List all modifier groups with pagination"""
    return menu_service.get_modifier_groups(db, skip=skip, limit=limit, active_only=active_only)


@router.get(
    "/modifier-groups/{group_id}",
    response_model=ModifierGroupOut,
    summary="Get modifier group by ID",
    description="Retrieve a single modifier group by its ID"
)
def get_modifier_group(
    group_id: int,
    db: Session = Depends(get_db_connection)
):
    """Get a specific modifier group by ID"""
    group = menu_service.get_modifier_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail=f"Modifier group {group_id} not found")
    return group


@router.post(
    "/modifier-groups",
    response_model=ModifierGroupOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new modifier group",
    description="Create a new modifier group"
)
def create_modifier_group(
    group: ModifierGroupCreate,
    db: Session = Depends(get_db_connection)
):
    """Create a new modifier group"""
    return menu_service.create_modifier_group(db, group)


@router.put(
    "/modifier-groups/{group_id}",
    response_model=ModifierGroupOut,
    summary="Update a modifier group",
    description="Update an existing modifier group"
)
def update_modifier_group(
    group_id: int,
    group: ModifierGroupUpdate,
    db: Session = Depends(get_db_connection)
):
    """Update an existing modifier group"""
    updated = menu_service.update_modifier_group(db, group_id, group)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Modifier group {group_id} not found")
    return updated


@router.delete(
    "/modifier-groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a modifier group",
    description="Delete a modifier group"
)
def delete_modifier_group(
    group_id: int,
    db: Session = Depends(get_db_connection)
):
    """Delete a modifier group"""
    success = menu_service.delete_modifier_group(db, group_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Modifier group {group_id} not found")


# ===========================
# ModifierOption Endpoints
# ===========================

@router.get(
    "/modifier-groups/{group_id}/options",
    response_model=List[ModifierOptionOut],
    summary="List options for a modifier group",
    description="Get all options for a specific modifier group"
)
def list_modifier_options_by_group(
    group_id: int,
    db: Session = Depends(get_db_connection)
):
    """List all options for a modifier group"""
    return menu_service.get_modifier_options_by_group(db, group_id)


@router.post(
    "/modifier-options",
    response_model=ModifierOptionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new modifier option",
    description="Create a new modifier option"
)
def create_modifier_option(
    option: ModifierOptionCreate,
    db: Session = Depends(get_db_connection)
):
    """Create a new modifier option"""
    return menu_service.create_modifier_option(db, option)


@router.put(
    "/modifier-options/{option_id}",
    response_model=ModifierOptionOut,
    summary="Update a modifier option",
    description="Update an existing modifier option"
)
def update_modifier_option(
    option_id: int,
    option: ModifierOptionUpdate,
    db: Session = Depends(get_db_connection)
):
    """Update an existing modifier option"""
    updated = menu_service.update_modifier_option(db, option_id, option)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Modifier option {option_id} not found")
    return updated


@router.delete(
    "/modifier-options/{option_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a modifier option",
    description="Delete a modifier option"
)
def delete_modifier_option(
    option_id: int,
    db: Session = Depends(get_db_connection)
):
    """Delete a modifier option"""
    success = menu_service.delete_modifier_option(db, option_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Modifier option {option_id} not found")


# ===========================
# ModifierAssignment Endpoints
# ===========================

@router.get(
    "/items/{item_id}/modifier-assignments",
    response_model=List[ModifierAssignmentOut],
    summary="List modifier assignments for an item",
    description="Get all modifier assignments for a specific menu item"
)
def list_modifier_assignments_by_item(
    item_id: int,
    db: Session = Depends(get_db_connection)
):
    """List all modifier assignments for a menu item"""
    return menu_service.get_modifier_assignments_by_item(db, item_id)


@router.get(
    "/categories/{category_id}/modifier-assignments",
    response_model=List[ModifierAssignmentOut],
    summary="List modifier assignments for a category",
    description="Get all modifier assignments for a specific category"
)
def list_modifier_assignments_by_category(
    category_id: int,
    db: Session = Depends(get_db_connection)
):
    """List all modifier assignments for a category"""
    return menu_service.get_modifier_assignments_by_category(db, category_id)


@router.post(
    "/modifier-assignments",
    response_model=ModifierAssignmentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new modifier assignment",
    description="Create a new modifier assignment"
)
def create_modifier_assignment(
    assignment: ModifierAssignmentCreate,
    db: Session = Depends(get_db_connection)
):
    """Create a new modifier assignment"""
    # Validate: either item_id or category_id must be set, but not both
    if (assignment.item_id and assignment.category_id) or (not assignment.item_id and not assignment.category_id):
        raise HTTPException(
            status_code=400,
            detail="Exactly one of item_id or category_id must be set"
        )
    return menu_service.create_modifier_assignment(db, assignment)


@router.put(
    "/modifier-assignments/{assignment_id}",
    response_model=ModifierAssignmentOut,
    summary="Update a modifier assignment",
    description="Update an existing modifier assignment"
)
def update_modifier_assignment(
    assignment_id: int,
    assignment: ModifierAssignmentUpdate,
    db: Session = Depends(get_db_connection)
):
    """Update an existing modifier assignment"""
    updated = menu_service.update_modifier_assignment(db, assignment_id, assignment)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Modifier assignment {assignment_id} not found")
    return updated


@router.delete(
    "/modifier-assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a modifier assignment",
    description="Delete a modifier assignment"
)
def delete_modifier_assignment(
    assignment_id: int,
    db: Session = Depends(get_db_connection)
):
    """Delete a modifier assignment"""
    success = menu_service.delete_modifier_assignment(db, assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Modifier assignment {assignment_id} not found")


# ===========================
# Menu Tree Endpoint
# ===========================

@router.get(
    "/tree",
    summary="Get full menu tree",
    description="Get complete menu tree with categories, items, variants, and modifiers filtered by channel"
)
def get_menu_tree(
    channel: str = Query("dine_in", description="Channel name (dine_in, takeaway, delivery)"),
    db: Session = Depends(get_db_connection)
):
    """
    Get full menu tree for a specific channel.

    This endpoint returns a hierarchical structure:
    - Categories (with subcategories)
      - Items (filtered by channel availability)
        - Variants
        - Modifier Groups
          - Modifier Options

    Args:
        channel: Channel name (dine_in, takeaway, delivery)

    Returns:
        List of category trees with nested data
    """
    return menu_service.get_menu_tree_for_channel(db, channel)
