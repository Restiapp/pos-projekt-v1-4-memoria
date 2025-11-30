# D5 Sprint Integration Fix Log

**Sprint:** D5 - Wave Selection / Hullam Valaszto
**Branch:** `integration/sprint-d1d5-waiter-final`
**Base Branch:** `integration/sprint-d3d4-waiter-final`
**Merged From:** `origin/claude/d5-waiter-wave-selection-v3`
**Date:** 2025-11-30

---

## Summary

Integrated the D5 Wave Selection feature into the existing D1-D4 waiter module codebase. The integration required resolving 13 merge conflicts while preserving all D1-D4 functionality and adding D5 wave selection capabilities.

### Business Context

**Hullam Valaszto (Wave Selection)** allows waiters to mark order items with priority waves:
- **1. KOR (PIROS/Red)** - Immediate (Round 1) - Items go to kitchen first
- **2. KOR (SARGA/Yellow)** - Next (Round 2) - Items go second
- **3. KOR (JELOLETLEN/Grey)** - Last (Round 3) - Items go last

If the user doesn't mark anything, all items default to Round 1 (Single Wave mode).

---

## Conflict Resolution Summary

### Backend Files (4 conflicts)

| File | Resolution Strategy |
|------|-------------------|
| `backend/core_domain/enums.py` | Added `ServiceRound` enum (D5) while keeping existing enums |
| `backend/service_orders/models/order.py` | Kept HEAD's `CompatibleJSON` import |
| `backend/service_orders/routers/orders.py` | Added `round_number` to `UpdateFlagsRequest`, updated endpoint description |
| `backend/service_orders/services/order_item_service.py` | Combined both: metadata_json handling + round_number column update |

### Frontend Files (9 conflicts)

| File | Resolution Strategy |
|------|-------------------|
| `frontend/package.json` | Kept `@mantine/notifications` from HEAD |
| `frontend/src/App.tsx` | Kept all D1-D4 imports (Reports, Inventory, Bar, Toast, Confirm, DebugAuth) + D5 |
| `frontend/src/api/guestOrderApi.ts` | Added `is_urgent`, `course_tag` flat fields + `updateItemRound` method |
| `frontend/src/features/guest/TableOrderPage.tsx` | Combined D3/D4 logic + D5 wave modal |
| `frontend/src/features/guest/components/AddItemModal.tsx` | Removed course_tag selector (D5 deprecates it) |
| `frontend/src/features/guest/components/MetricsDisplay.tsx` | Used type-only import for `TableMetrics` |
| `frontend/src/features/guest/components/OrderItemRow.tsx` | Used type-only import for `OrderItem` |
| `frontend/src/features/guest/components/RoundList.tsx` | Used type-only import for `OrderItem` |
| `frontend/package-lock.json` | Used incoming version (--theirs) |

---

## Critical Fixes Applied

### 1. JSONB Import Error in order_item.py

**Problem:** `NameError: name 'JSONB' is not defined`

**Cause:** D5 branch used raw `JSONB` type instead of `CompatibleJSON` wrapper.

**Fix:** Changed `metadata_json = Column(JSONB, ...)` to `metadata_json = Column(CompatibleJSON, ...)` and removed duplicate column/property definitions created by the merge.

### 2. TypeScript Type-Only Import Error

**Problem:** `error TS1484: 'OrderItem' is a type and must be imported using a type-only import when 'verbatimModuleSyntax' is enabled`

**Fix:** Changed `import { OrderItem }` to `import type { OrderItem }` in:
- `WaveSelectionModal.tsx`
- `OrderItemRow.tsx`
- `RoundList.tsx`
- `MetricsDisplay.tsx`

---

## New Components Added (D5)

### WaveSelectionModal.tsx
- Modal for selecting waves before sending to kitchen
- Click-to-cycle UI: Red -> Yellow -> Grey -> Red
- Defaults to Round 1 if user doesn't interact (Single Wave mode)

### ServiceRound Enum (backend)
```python
class ServiceRound(int, Enum):
    IMMEDIATE = 1  # Red / PIROS
    NEXT = 2       # Yellow / SARGA
    LAST = 3       # Unmarked / JELOLETLEN
```

---

## API Changes

### PATCH /orders/items/{item_id}/flags

**Request Body (Updated):**
```json
{
  "is_urgent": true,
  "course_tag": "foetal",
  "sync_with_course": "eloetel",
  "round_number": 1  // NEW: 1=Red, 2=Yellow, 3=Unmarked
}
```

### PUT /orders/items/{item_id}

**New Endpoint for Wave Selection:**
```json
{
  "round_number": 2
}
```

---

## Test Plan

### Manual Testing Steps

1. **Open Table Order Page**
   - Navigate to `/guest/table/1`
   - Verify metrics display shows correctly

2. **Add Items**
   - Click "+ Tetel Hozzaadasa"
   - Select product, quantity
   - Verify course tag selector is hidden (D5 deprecation)

3. **Wave Selection Modal**
   - Click "Rendeles Kuldese (Hullamok)"
   - Click items to cycle through waves (Red/Yellow/Grey)
   - Click "Kivalasztottak Kuldese"
   - Verify Round 1 items are sent to KDS

4. **Single Wave Mode**
   - Add items without touching wave selector
   - Send order
   - Verify all items go as Round 1

5. **Backend Health**
   ```bash
   curl http://localhost:8002/health
   # Expected: {"status":"ok","service":"orders","version":"0.1.0"}
   ```

---

## Build Verification

- [x] Docker compose up - all services healthy
- [x] Backend health endpoint responds OK
- [x] Frontend `npm run build` - SUCCESS (chunk size warning is acceptable)
- [x] No TypeScript errors
- [x] No merge conflict markers remaining

---

## Related Documentation

- [GUEST_FLOOR_ORDERS_SPEC_V1.md](../spec/GUEST_FLOOR_ORDERS_SPEC_V1.md) - Full waiter module specification
- [SYSTEM_MASTER_SPEC_V1.md](../spec/SYSTEM_MASTER_SPEC_V1.md) - System-wide specifications
