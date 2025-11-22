# RESTI POS - Payment & Closure Flow V1

**Version:** 1.0
**Status:** DRAFT (Sprint 0)
**Context:** Defines how bills are closed, payments recorded, and VAT finalized.

## 1. Entities

### Bill / Check (Számla / Nyugta)
*   Represents the financial obligation of a customer.
*   Usually 1:1 with `Order` in simple cases, but can be 1:N (split bill).
*   **State:** `OPEN` -> `PARTIALLY_PAID` -> `PAID`.

### Payment (Fizetés)
*   A specific transaction settling part or all of a Bill.
*   **Attributes:**
    *   `amount`: Monetary value.
    *   `currency`: HUF (default).
    *   `method`: `PaymentMethod` (CASH, CARD, etc.).
    *   `created_at`: Timestamp.
    *   `created_by`: User ID (staff).

### VAT Category (ÁFA)
*   Defined in `service_menu` per Product.
*   **Logic:**
    *   Dine-in Food: 5%
    *   Dine-in Drink: 27%
    *   Takeaway: 27% (Simplification, rules vary).
    *   **Decision Point:** `service_orders` calculates the final VAT breakdown when the Order is "finalized" (pre-payment).

## 2. Payment Flows

### 2.1 Table Payment (Dine-In)
1.  **Request Bill:** Waiter selects Table. System aggregates unpaid items.
2.  **Print Pre-check:** Optional intermediate receipt.
3.  **Payment:**
    *   **Full:** Waiter selects "Pay All". Selects Method (e.g. Card).
    *   **Split:** Waiter selects specific items OR specific amount.
        *   System creates a "Sub-Bill" or just records partial payment against Order.
4.  **Closure:** When `remaining_amount == 0`, Order status -> `CLOSED` (`LEZART`).
5.  **Fiscalization:** NTAK data submission (async).

### 2.2 Bar Payment (Quick Serve)
1.  Bartender adds items to "Bar Tab" or direct temporary order.
2.  Immediate Payment workflow (add items -> Pay -> Close).
3.  No table selection necessary.

### 2.3 Takeaway / Delivery Payment
1.  **Takeaway:** Customer pays at counter (same as Bar).
2.  **Delivery (Courier Side):**
    *   Courier arrives at address.
    *   Handover: Customer pays Cash or confirms Pre-paid.
    *   Courier marks "Delivered" & "Paid" in Driver App.
    *   System records Payment (Cash on Hand for Courier).

### 2.4 VIP Payment
1.  Items consumed in VIP room.
2.  Bill is often settled by "Invoice" (monthly) or "House Account".
3.  Payment Method: `INVOICE` or `HOUSE_ACCOUNT`.
4.  Requires Manager approval? (Future feature).

## 3. Audit Requirements

### Tracing
*   **Who closed it:** `Payment.created_by` stores the Employee ID.
*   **When:** Timestamp is critical for Shift closing.
*   **Cash Drawer:** Payments of type CASH increase the "expected cash" of the drawer assigned to that User/Terminal.

### Storno / Corrections
*   **Voiding a closed bill:** Requires Manager PIN.
*   **Action:**
    1.  Create Reversal Payment (negative amount).
    2.  Set Order status back to `OPEN` (or `CANCELLED` if full void).
    3.  Log reason for audit.
