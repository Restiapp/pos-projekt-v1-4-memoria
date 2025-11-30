# Guest Floor Orders Spec (Phase D1/D2)

**Version:** 1.0
**Status:** DRAFT
**Context:** Definition of backend support for the "Guest Area / Waiter Floor" module, including rounds, flags, and time metrics.

## 1. Schema Extensions

### OrderItem Model (DB)
We are extending the `OrderItem` model to support rounds and detailed flags.

**New Columns:**
1.  `round_number` (Integer, nullable, default=1): Represents the "serving round" or "kör" index.
2.  `metadata_json` (JSONB, nullable): Stores flexible flags and attributes not requiring strict schema enforcement immediately.
    *   `is_urgent` (bool): High priority flag.
    *   `course_tag` (string): "starter", "main", "dessert", etc.
    *   `sync_with_course` (string): Reference to a course tag to sync timing.

*Note: Since Alembic is not currently configured in `service_orders`, these columns must be added carefully. New environments will pick them up via `init_db()`. Existing environments may require a manual SQL `ALTER TABLE` or a rebuild.*

### OrderItemWithFlags (API Schema)
The frontend will receive and send item data in this structure:
```json
{
  "id": 123,
  "product_id": 45,
  "name": "Gulyásleves",
  "quantity": 1,
  "round_number": 1,
  "is_urgent": false,
  "course_tag": "starter",
  "sync_with_course": null
}
```

## 2. New & Updated Endpoints

### 2.1 Open Order for Table
*   **POST** `/api/v1/orders/{table_id}/open`
*   **Behavior:** Returns the existing `OPEN` order for the table or creates a new one.
*   **Response:** `OrderResponse` (including items).

### 2.2 Add Items (With Round)
*   **POST** `/api/v1/orders/{order_id}/items`
*   **Body:**
    ```json
    {
      "round_number": 2,
      "items": [
        { "product_id": 10, "quantity": 1, "is_urgent": true }
      ]
    }
    ```
*   **Behavior:** Adds items to the order, assigning the specified `round_number`.

### 2.3 Send Round to KDS
*   **POST** `/api/v1/orders/{order_id}/rounds/{round_number}/send-to-kds`
*   **Behavior:** Trigger KDS tickets for all items in the specified round.
*   **Note:** Logic delegates to existing KDS flows (mocked or real).

### 2.4 Update Item Flags
*   **PATCH** `/api/v1/orders/items/{item_id}/flags`
*   **Body:** `{ "is_urgent": true, "course_tag": "main" }`
*   **Behavior:** Updates `metadata_json`.

### 2.5 Table Metrics
*   **GET** `/api/v1/orders/{table_id}/metrics`
*   **Response:**
    ```json
    {
      "table_id": 5,
      "active_order_id": 101,
      "order_start_time": "2023-10-27T10:00:00Z",
      "last_round_sent_at": "2023-10-27T10:15:00Z"
    }
    ```

## 3. Migration Note
For existing databases, run:
```sql
ALTER TABLE order_items ADD COLUMN round_number INTEGER DEFAULT 1;
ALTER TABLE order_items ADD COLUMN metadata_json JSONB;
```
