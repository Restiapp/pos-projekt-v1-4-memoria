# Floorplan Domain & API Contract V1 (Rooms + Tables)

**Version:** 1.0
**Status:** DRAFT (Sprint 0)
**Context:** Defines the data model and API contract for the frontend floor plan editor.

## 1. Current State Summary

### Rooms
*   **Missing Model:** There is currently **NO** explicit `Room` model in the backend.
*   **Implicit Definition:** Rooms/Areas are implicitly handled via the `section` string column on the `Table` model (e.g., 'Terasz', 'Belső terem').
*   **Ownership:** N/A (concept doesn't strictly exist yet).

### Tables
*   **Model:** `Table` (in `service_orders`).
*   **Fields:**
    *   `id`: Integer (PK).
    *   `table_number`: String (Unique).
    *   `position_x`: Integer (Optional).
    *   `position_y`: Integer (Optional).
    *   `capacity`: Integer (Optional).
    *   `section`: String (Optional) - Acts as the "Room" identifier.
    *   `parent_table_id`: Integer (Optional) - For table merging.
*   **Ownership:** `service_orders`.

### Missing Pieces for Frontend UX
1.  **Room Entity:** No ID, no order index, no dimensions. The frontend cannot query "all rooms" without scanning all tables.
2.  **Table Metadata:** Missing `width`, `height`, `shape`, `rotation` (implied or needed for editor). `position_x/y` exists but is basic.
3.  **Visual Hints:** No `color_hint` or specific `type` enum for Tables (just generic capacity).

## 2. Target API Contract (V1)

To support the new Floor Plan Editor, the backend must expose the following structure.
*Note: Since DB changes are restricted in Sprint 0, this will be implemented via a transformation layer / read-only endpoint initially.*

### 2.1 Enums (Shared)

Defined in `backend/core_domain/enums.py`.

```python
class RoomType(str, Enum):
    BAR = "BAR"
    INDOOR = "INDOOR"
    TERRACE_SMOKING = "TERRACE_SMOKING"
    TERRACE_NONSMOKING = "TERRACE_NONSMOKING"
    VIP = "VIP"

class TableShape(str, Enum):
    ROUND = "ROUND"
    SQUARE = "SQUARE"
    RECTANGLE = "RECTANGLE"
```

### 2.2 Room API

**Endpoints:**
*   `GET /api/v1/floorplan/rooms` - List all configured rooms.

**Data Object (DTO):**
```json
{
  "id": "section_name_hash_or_id",
  "name": "Belső terem",
  "type": "INDOOR",
  "position_index": 0,
  "width": 800,
  "height": 600,
  "is_active": true
}
```

*Temporary Mapping Strategy:*
*   Since `Room` table is missing, the backend will dynamically generate this list based on distinct `section` values found in the `Table` table, or from a hardcoded configuration in code until the DB migration in Sprint 1.

### 2.3 Table API

**Endpoints:**
*   `GET /api/v1/floorplan/rooms/{room_id}/tables` - List tables for a specific room.
*   `GET /api/v1/floorplan/full-map` - Aggregated view (Room + Tables).

**Data Object (DTO):**
```json
{
  "id": 101,
  "room_id": "section_hash",
  "name": "Asztal 1",
  "number": "1",
  "capacity": 4,
  "shape": "RECTANGLE",
  "x": 100,
  "y": 200,
  "width": 80,
  "height": 80,
  "color_hint": null,
  "is_active": true,
  "is_smoking": false
}
```

*Mapping Strategy (Sprint 0):*
*   `room_id` -> derived from `section`.
*   `shape` -> Default to `RECTANGLE` (or derived from name if possible).
*   `width/height` -> Default to fixed size (e.g., 80x80) or calculated from capacity.
*   `x/y` -> Map from `position_x`, `position_y`.

## 3. Implementation Plan (Sprint 0)

1.  **Core Domain:** Add `RoomType` and `TableShape` enums.
2.  **Service Orders:**
    *   Create `FloorplanService` to handle the aggregation.
    *   Create a new router `floorplan_router.py`.
    *   Implement `GET /api/v1/floorplan/full-map`.
3.  **Frontend Contract:** The endpoint will return the "Target" structure, filling missing DB columns with safe defaults.

## 4. Future Migration (Sprint 1+)

*   Create real `rooms` table in Postgres.
*   Add `width`, `height`, `shape`, `rotation`, `room_id` columns to `tables`.
*   Migrate `section` string data to `room_id` foreign keys.
