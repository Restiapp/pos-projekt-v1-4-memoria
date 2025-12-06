# Rounds Feature - Frontend Implementation

## Overview

The Rounds feature enables restaurant staff to organize order items into multiple "rounds" (Hungarian: "kör"), allowing staged delivery of courses. This is essential for fine dining experiences where appetizers, main courses, and desserts are served at different times.

## Branch

**Branch name:** `claude/integrate-order-service-01DmEygUFy62rnAvewyyNWbx`

## Components

### 1. TableOrderPanel

**Location:** `frontend/src/components/orders/TableOrderPanel.tsx`

Main component for displaying and managing rounds within an order.

**Features:**
- Displays all rounds grouped by `round_number`
- Shows items within each round with quantity and price
- "Új kör" button to create new rounds
- "Tétel hozzáadása ehhez a körhöz" button per round
- "Kör küldése konyhának" button per round
- Round status badges (NYITOTT, KONYHÁNAK KÜLDVE, KÉSZ)

**Usage:**
```tsx
import { TableOrderPanel } from '@/components/orders';

<TableOrderPanel
  orderId={123}
  onOrderUpdated={() => console.log('Order updated')}
/>
```

**Props:**
- `orderId: number` - The order ID to display
- `onOrderUpdated?: () => void` - Optional callback when order is updated

### 2. AddItemModal

**Location:** `frontend/src/components/orders/AddItemModal.tsx`

Modal for selecting products and adding them to a specific round.

**Features:**
- Product selection dropdown (searchable)
- Quantity input
- Multiple products can be added before submission
- Real-time price calculation
- Validation and error handling

**Usage:**
```tsx
import { AddItemModal } from '@/components/orders';

<AddItemModal
  isOpen={true}
  onClose={() => setModalOpen(false)}
  orderId={123}
  roundNumber={2}
  onItemsAdded={() => refreshOrder()}
/>
```

**Props:**
- `isOpen: boolean` - Controls modal visibility
- `onClose: () => void` - Called when modal is closed
- `orderId: number` - The order ID to add items to
- `roundNumber: number` - The round number to add items to
- `onItemsAdded: () => void` - Called when items are successfully added

### 3. GuestFloorPage (Demo)

**Location:** `frontend/src/pages/GuestFloorPage.tsx`

Demo page showing how to integrate the TableOrderPanel.

**URL:** `/guest-floor?order_id=123`

## Type Definitions

**Location:** `frontend/src/types/order.ts`

### OrderItem
```typescript
interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product_name?: string;
  quantity: number;
  unit_price: number;
  round_number?: number; // NEW: for grouping items into rounds
  kds_status: KDSStatus;
  // ... other fields
}
```

### Round
```typescript
interface Round {
  round_number: number;
  items: OrderItem[];
  status?: 'OPEN' | 'SENT_TO_KDS' | 'READY';
}
```

### OrderWithItems
```typescript
interface OrderWithItems extends Order {
  items: OrderItem[];
}
```

## Service Methods

**Location:** `frontend/src/services/orderService.ts`

### getOrderWithItems
```typescript
const orderWithItems = await getOrderWithItems(orderId);
```
Fetches an order with all its items. Includes fallback logic if the backend endpoint doesn't exist yet.

### addItemsToRound
```typescript
const items = [
  { product_id: 1, quantity: 2, unit_price: 1500 },
  { product_id: 2, quantity: 1, unit_price: 2000 }
];
await addItemsToRound(orderId, roundNumber, items);
```
Adds items to a specific round. Falls back to adding items one-by-one with `round_number` if the dedicated endpoint doesn't exist.

### sendRoundToKds
```typescript
const result = await sendRoundToKds(orderId, roundNumber);
// result: { success: boolean, message: string }
```
Sends a round to the kitchen (KDS). Currently returns a mock success response since the backend endpoint may not exist yet.

## Rounds Behavior

### Default Round Assignment
- If an item has no `round_number`, it defaults to round 1
- Rounds are automatically sorted by `round_number` ascending

### Creating New Rounds
1. Click "Új kör" button
2. System calculates next round number (max + 1)
3. AddItemModal opens to add items to the new round

### Adding Items to Existing Rounds
1. Click "Tétel hozzáadása ehhez a körhöz" for a specific round
2. Select products and quantities in the modal
3. Items are added with the correct `round_number`

### Sending Rounds to Kitchen
1. Click "Kör küldése konyhának" for a specific round
2. Backend endpoint is called (or mock response is returned)
3. Toast notification shows success/error
4. Round status updates (when backend support is added)

## Backend Integration Status

### ✅ Implemented (Frontend)
- Type definitions with `round_number`
- UI components for rounds management
- Service methods with fallback logic
- Toast notifications

### ⚠️ TODO (Backend)
The following backend endpoints are expected but may not exist yet:

1. **GET /api/orders/{id}/items**
   - Should return order with all items including `round_number`

2. **POST /api/orders/{id}/rounds/{round_number}/items**
   - Should add items to a specific round
   - Request body: `{ items: [...] }`

3. **POST /api/orders/{id}/rounds/{round_number}/send-to-kds**
   - Should send a round to the kitchen
   - Should update item statuses

### Fallback Behavior
Until backend endpoints are implemented:
- `getOrderWithItems` falls back to separate calls
- `addItemsToRound` adds items one-by-one with `round_number` field
- `sendRoundToKds` returns mock success response

## Testing

### Build Status
✅ **Build passes:** `npm run build` completes successfully

### Manual Testing
1. Create an order (or use existing order ID)
2. Navigate to `/guest-floor?order_id=123`
3. Test creating new rounds
4. Test adding items to rounds
5. Test sending rounds to kitchen
6. Verify toast notifications appear correctly

## Files Changed/Created

### Created
- `frontend/src/components/orders/TableOrderPanel.tsx`
- `frontend/src/components/orders/TableOrderPanel.css`
- `frontend/src/components/orders/AddItemModal.tsx`
- `frontend/src/components/orders/AddItemModal.css`
- `frontend/src/components/orders/index.ts`
- `frontend/src/pages/GuestFloorPage.tsx`
- `frontend/src/pages/GuestFloorPage.css`
- `frontend/ROUNDS_FEATURE.md` (this file)

### Modified
- `frontend/src/types/order.ts` - Added OrderItem, Round, OrderWithItems types
- `frontend/src/services/orderService.ts` - Added rounds management methods

## Next Steps

### For Backend Team (Jules)
1. Add `round_number` field to OrderItem model
2. Implement `/api/orders/{id}/items` endpoint
3. Implement `/api/orders/{id}/rounds/{round_number}/items` endpoint
4. Implement `/api/orders/{id}/rounds/{round_number}/send-to-kds` endpoint
5. Add round status tracking logic

### For Frontend Integration
1. Update routing to include GuestFloorPage
2. Modify TableMap to navigate to GuestFloorPage when table has active order
3. Add round status indicators based on backend data
4. Enhance AddItemModal with modifiers support
5. Add seat assignment to items

## Hungarian Terminology

- **Kör** = Round (course)
- **Tétel** = Item
- **Konyha** = Kitchen
- **Nyitott** = Open
- **Konyhának küldve** = Sent to kitchen
- **Kész** = Ready

## Notes

⚠️ **Important:** Do not delete existing rooms and tables. If test data is needed, create new rooms with "DEV –" prefix (e.g., "DEV – Teszt terem 1").

---

**Implementation Date:** 2025-11-23
**Developer:** Web Claude (Frontend)
**Sprint:** FE-3 (Rounds & Item Adding UI)
