# SPECIFICATION: Floor Plan & Visual Editor (v1.0)

## 🎯 Overview
This document defines the architecture for the "Professional Floor Plan Editor" and the modernized "Customer/Waiter View". The goal is to move away from list-based views to a graphical, spatial interface (Canvas-based) with a modern "App-like" navigation structure.

## 🛠 Tech Stack Recommendations
To ensure a "Pro" look and feel (avoiding the "C64 look"), the following libraries are mandated:

1.  **UI Framework:** `Mantine UI (v7)`
    *   Used for: App Shell, Modals, Inputs, Buttons, Notifications.
    *   Benefit: Consistent, modern design system out-of-the-box.
2.  **Graphics Engine:** `React-Konva` (Canvas)
    *   Used for: The Floor Plan Editor (Admin) and Viewer (Customer).
    *   Benefit: High performance, supports rotation, custom shapes (chairs), zooming, and layer management.
3.  **Icons:** `Lucide React` or `Tabler Icons`

---

## 📱 UX/UI Layout Redesign

### 1. Customer / Waiter View (`/tables`)
*   **Top Bar (Room Switcher):**
    *   A scrollable horizontal bar containing tabs for each **Room** (e.g., "Garden", "Main Hall", "VIP").
    *   Clicking a tab switches the active Canvas view.
*   **Center (The Canvas):**
    *   Displays the interactive floor plan using `React-Konva`.
    *   Users tap tables to initiate orders.
    *   Tables show status colors (Green: Free, Red: Busy).
*   **Bottom Bar (Global Navigation):**
    *   Replaces the old top header.
    *   Contains icons: `Tables`, `KDS` (if staff), `Orders`, `Menu` (if admin).
    *   Fixed at the bottom of the screen (Mobile-app style).

### 2. Admin Dashboard (`/admin`)
*   **Routing Change:**
    *   `/admin/tables`: Renders the **Graphical Editor**, not a list.
*   **Editor Features:**
    *   **Canvas Area:** Drop zone for tables.
    *   **Toolbar (Side/Bottom):** Draggable "Furniture" (Round Table, Rect Table, Wall, Decoration).
    *   **Properties Panel:** When a table is selected, edit:
        *   Label (Number)
        *   Seats (Capacity)
        *   Rotation (Slider)
        *   Dimensions (Width/Height)

---

## 💾 Database Schema Changes

### 1. New Model: `Room`
*   `id`: Integer (PK)
*   `name`: String (e.g., "Garden")
*   `type`: Enum ('indoor', 'outdoor', 'bar')
*   `width`: Integer (Canvas coordinate space width)
*   `height`: Integer (Canvas coordinate space height)
*   `background_image_url`: String (Optional, for custom floor textures)

### 2. Update Model: `Table`
*   `room_id`: Integer (FK -> Room.id) **[CRITICAL]**
*   `shape`: String ('rect', 'round')
*   `position_x`: Integer
*   `position_y`: Integer
*   `width`: Integer
*   `height`: Integer
*   `rotation`: Float (Degrees, 0-360)
*   `metadata`: JSON (Stores "chair positions", colors, etc.)

---

## 💻 Implementation Steps (For VS Codex)

### Step 1: Backend Foundation (`service_orders`)
1.  Create `Room` SQLAlchemy model.
2.  Update `Table` model with new geometry fields (`shape`, `rotation`, `width`, `height`, `room_id`).
3.  Create API endpoints:
    *   `GET /rooms`
    *   `POST /rooms`
    *   `POST /rooms/{id}/tables` (Bulk update for saving layout).

### Step 2: Frontend Core (`frontend`)
1.  **Install Dependencies:**
    ```bash
    npm install @mantine/core @mantine/hooks @mantine/notifications @tabler/icons-react konva react-konva use-image
    # Also install PostCSS/Tailwind if needed by Mantine (Mantine works with raw CSS modules too)
    ```
2.  **Setup App Shell:**
    *   Create `Layout/AppLayout.tsx` using Mantine's `AppShell`.
    *   Implement the "Bottom Navigation" logic.

### Step 3: Floor Plan Engine (`components/floor-plan`)
1.  **`FloorCanvas` Component:**
    *   Wrapper around `<Stage>` and `<Layer>` from `react-konva`.
2.  **`DraggableTable` Component:**
    *   Renders a `<Group>` containing `<Rect>`/`<Circle>` (Table) and smaller shapes (Chairs).
    *   Handles `onDragEnd` to update coordinates.
3.  **`RoomTabs` Component:**
    *   Mantine `<Tabs>` component to switch between Rooms.

### Step 4: Integration
1.  Update `/admin/tables` to use the new `FloorPlanEditor`.
2.  Update `/tables` (Public) to use `FloorPlanViewer` (Read-only version).
