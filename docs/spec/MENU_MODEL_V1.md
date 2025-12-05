# Menu Model V1 Specification

**Document Version:** 1.0
**Date:** 2025-12-05
**Sprint:** D6 - Menu Structure Implementation
**Branch:** `integration/menu-structure-v1`

---

## 1. Overview

Menu Model V1 is a complete redesign of the menu/product data structure for the Resti POS system. It replaces the legacy `Product`, `Category`, `Modifier`, and `ModifierGroup` models with a more flexible, channel-aware architecture.

### 1.1 Key Features

- **Hierarchical Categories**: Support for subcategories via `parent_id`
- **Channel-Aware Items**: Items can be available on different channels (dine-in, takeaway, delivery) with different VAT rates
- **Item Variants**: Support for product variants (e.g., gluten-free options) with price deltas
- **Flexible Modifiers**: Rich modifier system with groups, options, and assignments
- **Tree API**: Single endpoint (`/api/v1/menu/tree`) returns full hierarchical menu structure

### 1.2 Legacy Models

The following models are marked as **LEGACY** and should not be used for new features:

- `backend/service_menu/models/product.py`
- `backend/service_menu/models/category.py`
- `backend/service_menu/models/modifier.py`
- `backend/service_menu/models/modifier_group.py`

---

## 2. Data Model

### 2.1 MenuCategory

Represents a menu category (e.g., "Hamburgers", "Appetizers").

**Fields:**
- `id` (int, PK)
- `name` (string, required) - Category name
- `description` (text, optional)
- `parent_id` (int, FK to MenuCategory, nullable) - For subcategories
- `position` (int, default 0) - Display order
- `is_active` (bool, default True)
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- `parent`: Self-referencing for hierarchical structure
- `items`: One-to-Many with MenuItem
- `modifier_assignments`: One-to-Many with ModifierAssignment

---

### 2.2 MenuItem

Core menu item with pricing and channel support.

**Fields:**
- `id` (int, PK)
- `category_id` (int, FK to MenuCategory, nullable)
- `name` (string, required)
- `description` (text, optional)
- `base_price_gross` (Decimal, required) - Price including VAT
- `vat_rate_dine_in` (Decimal, default 5.00) - VAT % for dine-in (Hungary)
- `vat_rate_takeaway` (Decimal, default 27.00) - VAT % for takeaway (Hungary)
- `is_active` (bool, default True)
- `channel_flags` (JSON, nullable) - e.g., `{"dine_in": true, "takeaway": true, "delivery": false}`
- `metadata_json` (JSON, nullable) - Images, allergens, translations, etc.
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- `category`: Many-to-One with MenuCategory
- `variants`: One-to-Many with MenuItemVariant
- `modifier_assignments`: One-to-Many with ModifierAssignment

---

### 2.3 MenuItemVariant

Product variants with price deltas (e.g., "Gluten-free Hawaii Burger").

**Fields:**
- `id` (int, PK)
- `item_id` (int, FK to MenuItem, CASCADE)
- `name` (string, required)
- `price_delta` (Decimal, default 0.00) - +/- relative to base price
- `is_default` (bool, default False)
- `is_active` (bool, default True)
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- `item`: Many-to-One with MenuItem

---

### 2.4 ModifierGroup

Groups of modifiers/extras (e.g., "Bun type", "Extra toppings").

**Fields:**
- `id` (int, PK)
- `name` (string, required)
- `description` (text, optional)
- `selection_type` (enum, required) - `REQUIRED_SINGLE`, `OPTIONAL_SINGLE`, `OPTIONAL_MULTIPLE`
- `min_select` (int, default 0) - Minimum selections required
- `max_select` (int, nullable) - Maximum selections (null = unlimited)
- `position` (int, default 0) - Display order
- `is_active` (bool, default True)
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- `options`: One-to-Many with ModifierOption
- `assignments`: One-to-Many with ModifierAssignment

---

### 2.5 ModifierOption

Individual options within a modifier group.

**Fields:**
- `id` (int, PK)
- `group_id` (int, FK to ModifierGroup, CASCADE)
- `name` (string, required)
- `price_delta_gross` (Decimal, default 0.00) - +/- price
- `is_default` (bool, default False)
- `is_active` (bool, default True)
- `metadata_json` (JSON, nullable) - Allergens, translations, etc.
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- `group`: Many-to-One with ModifierGroup

---

### 2.6 ModifierAssignment

Links modifier groups to items or categories.

**Fields:**
- `id` (int, PK)
- `group_id` (int, FK to ModifierGroup, CASCADE)
- `item_id` (int, FK to MenuItem, CASCADE, nullable)
- `category_id` (int, FK to MenuCategory, CASCADE, nullable)
- `applies_to_variants` (bool, default True)
- `is_required_override` (bool, nullable) - Override group's selection_type
- `position` (int, default 0) - Display order
- `created_at`, `updated_at` (timestamps)

**Relationships:**
- `group`: Many-to-One with ModifierGroup
- `item`: Many-to-One with MenuItem (if item-level)
- `category`: Many-to-One with MenuCategory (if category-level)

**Constraints:**
- Exactly one of `item_id` or `category_id` must be set (enforced by CHECK constraint)

---

## 3. API Endpoints

All endpoints are under `/api/v1/menu` and require `menu:view` permission.

### 3.1 MenuCategory Endpoints

- `GET /categories` - List all categories
  - Query params: `skip`, `limit`, `active_only`
- `GET /categories/{id}` - Get category by ID
- `POST /categories` - Create new category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

### 3.2 MenuItem Endpoints

- `GET /items` - List all items
  - Query params: `skip`, `limit`, `category_id`, `active_only`
- `GET /items/{id}` - Get item by ID
- `POST /items` - Create new item
- `PUT /items/{id}` - Update item
- `DELETE /items/{id}` - Delete item

### 3.3 MenuItemVariant Endpoints

- `GET /items/{item_id}/variants` - List variants for item
- `POST /variants` - Create new variant
- `PUT /variants/{id}` - Update variant
- `DELETE /variants/{id}` - Delete variant

### 3.4 ModifierGroup Endpoints

- `GET /modifier-groups` - List all groups
  - Query params: `skip`, `limit`, `active_only`
- `GET /modifier-groups/{id}` - Get group by ID
- `POST /modifier-groups` - Create new group
- `PUT /modifier-groups/{id}` - Update group
- `DELETE /modifier-groups/{id}` - Delete group

### 3.5 ModifierOption Endpoints

- `GET /modifier-groups/{group_id}/options` - List options for group
- `POST /modifier-options` - Create new option
- `PUT /modifier-options/{id}` - Update option
- `DELETE /modifier-options/{id}` - Delete option

### 3.6 ModifierAssignment Endpoints

- `GET /items/{item_id}/modifier-assignments` - List assignments for item
- `GET /categories/{category_id}/modifier-assignments` - List assignments for category
- `POST /modifier-assignments` - Create new assignment
- `PUT /modifier-assignments/{id}` - Update assignment
- `DELETE /modifier-assignments/{id}` - Delete assignment

### 3.7 Menu Tree Endpoint (PRIMARY)

**`GET /api/v1/menu/tree?channel={channel}`**

Returns complete hierarchical menu structure for a specific channel.

**Query Parameters:**
- `channel` (string, default "dine_in") - One of: `dine_in`, `takeaway`, `delivery`

**Response Structure:**
```json
[
  {
    "id": 1,
    "name": "Hamburgers",
    "description": "...",
    "parent_id": null,
    "position": 0,
    "is_active": true,
    "items": [
      {
        "id": 10,
        "name": "Hawaii Burger",
        "description": "...",
        "base_price_gross": 3990.0,
        "vat_rate_dine_in": 5.0,
        "vat_rate_takeaway": 27.0,
        "is_active": true,
        "channel_flags": {"dine_in": true, "takeaway": true, "delivery": false},
        "metadata_json": {...},
        "variants": [
          {
            "id": 100,
            "name": "Gluten-free Hawaii Burger",
            "price_delta": 500.0,
            "is_default": false,
            "is_active": true
          }
        ],
        "modifier_groups": [
          {
            "id": 1,
            "name": "Bun Type",
            "description": "...",
            "selection_type": "REQUIRED_SINGLE",
            "min_select": 1,
            "max_select": 1,
            "position": 0,
            "is_active": true,
            "options": [
              {
                "id": 10,
                "name": "Normal Bun",
                "price_delta_gross": 0.0,
                "is_default": true,
                "is_active": true
              },
              {
                "id": 11,
                "name": "Sesame Bun",
                "price_delta_gross": 0.0,
                "is_default": false,
                "is_active": true
              }
            ]
          }
        ]
      }
    ],
    "subcategories": []
  }
]
```

---

## 4. Database Migration

**File:** `backend/service_menu/alembic/versions/manual_001_create_menu_v1_tables.py`

Creates:
- 6 new tables
- 1 enum type (`SelectionType`)
- Indexes on FK columns and `is_active` flags
- CHECK constraint on `modifier_assignments` for exclusive item/category assignment

**Running Migration:**
```bash
cd backend/service_menu
alembic upgrade head
```

---

## 5. Seed Data Import

**File:** `backend/service_menu/scripts/import_menu_seed_data.py`

Imports menu data from `C:\Codex\resti-menu\data\menu.json` into new tables.

**Running Import:**
```bash
cd backend/service_menu
python -m scripts.import_menu_seed_data
```

**Import Strategy:**
- Best-effort mapping from legacy JSON structure
- Creates 3 sample modifier groups (Bun Type, Extra Toppings, Side Dish)
- Stores original data in `metadata_json` for reference
- Fine-tuning can be done later via admin interface

---

## 6. Frontend Integration

### 6.1 Types

**File:** `frontend/src/types/menuV1.ts`

Defines TypeScript interfaces for all entities and tree structures.

### 6.2 Service

**File:** `frontend/src/services/menuV1Service.ts`

Provides API client methods for all CRUD operations and tree retrieval.

### 6.3 Debug View

**Route:** `/admin/menu-debug`
**Component:** `frontend/src/pages/MenuDebugPage.tsx`

Simple text-based view for testing Menu V1 API. Shows:
- Category tree
- Items with variants
- Modifier groups with options
- Channel filtering

---

## 7. Future Enhancements

### 7.1 Phase 2 (D7+)
- Full admin UI for CRUD operations
- Drag-and-drop reordering
- Bulk import/export
- Image upload integration
- Advanced allergen management

### 7.2 Phase 3
- Integration with order flow
- Real-time modifier price calculations
- Multi-language menu support
- Menu scheduling (time-based availability)

---

## 8. Testing Checklist

- [ ] Migration runs successfully: `alembic upgrade head`
- [ ] Seed data imports without errors
- [ ] GET `/api/v1/menu/tree?channel=dine_in` returns data
- [ ] Frontend `/admin/menu-debug` page displays menu tree
- [ ] All CRUD endpoints return correct HTTP status codes
- [ ] Foreign key constraints prevent orphaned records
- [ ] Check constraint prevents invalid modifier assignments

---

## 9. Breaking Changes

### 9.1 From Legacy Models

- Old `Product` model is NOT compatible with `MenuItem`
- Old `Category` model lacks `position` and `parent_id`
- Old `Modifier`/`ModifierGroup` do not support channel filtering
- No migration path from legacy to new schema (intentional clean slate)

### 9.2 API Changes

- Legacy endpoints (`/api/v1/products`, `/api/v1/categories`) remain functional
- New endpoints are under `/api/v1/menu` namespace
- Frontend should use `menuV1Service` instead of `menuService` for new features

---

**Document Status:** ✅ Complete
**Author:** Claude (VS Claude Integration Agent)
**Review Required:** Product Owner, Backend Lead
