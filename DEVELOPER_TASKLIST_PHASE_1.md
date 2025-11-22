# DEVELOPER TASKLIST - PHASE 1 (Refined)
**Focus:** Professional Floor Plan Editor & Modern UI Upgrade.
**Reference:** `docs/SPEC_FLOOR_PLAN.md`

## 📦 MODULE 1: Backend Schema (Service Orders)
- [ ] **1.1 Room Model:**
    - Create `Room` model (`name`, `width`, `height`, `type`).
    - Create CRUD Routers (`/rooms`).
- [ ] **1.2 Table Model Upgrade:**
    - Add columns: `room_id` (FK), `shape` (enum), `width`, `height`, `rotation`, `metadata` (JSON).
    - Update Pydantic schemas (`TableCreate`, `TableUpdate`).
    - Update `init_db` or migration scripts if necessary (or just use `reset_db` since we are in dev).

## 📦 MODULE 2: Frontend Infrastructure (Modern Stack)
- [ ] **2.1 Install Dependencies:**
    - Run: `npm install @mantine/core @mantine/hooks @mantine/notifications @tabler/icons-react konva react-konva`
    - Wrap `App.tsx` with `<MantineProvider>`.
- [ ] **2.2 New Layout System:**
    - Create `components/layout/MobileAppShell.tsx`:
        - **Header:** Room Tabs (Scrollable).
        - **Content:** Main Viewport.
        - **Footer:** Bottom Navigation Bar (Tables, Orders, Menu).
    - Replace the old Top Navbar in `App.tsx` with this new Shell for the `/tables` route.

## 📦 MODULE 3: Floor Plan Editor (Admin)
- [ ] **3.1 Graphic Components (`components/floor-plan`):**
    - `TableShape.tsx`: React-Konva component rendering a Rect/Circle + Chairs based on `capacity`.
    - `RoomEditor.tsx`: The main Canvas Stage. Handles Drag & Drop events.
- [ ] **3.2 Admin UI Integration (`pages/admin/FloorPlanEditorPage.tsx`):**
    - Sidebar: "Add Room" button, "Add Table" draggable items.
    - Main Area: The Canvas.
    - Properties Panel: Edit selected table's name/seats.
    - **Action:** Replace `/admin/tables` route with this page.

## 📦 MODULE 4: Customer/Waiter View
- [ ] **4.1 Viewer Component (`pages/TableMapPage.tsx`):**
    - Read-only version of the Canvas.
    - Click events trigger "Open Order".
    - Visual feedback for status (Free/Busy).
- [ ] **4.2 Navigation Update:**
    - Ensure the "Room Switcher" works perfectly to swap Canvases.
