# RESTI POS - Architecture Target V1

**Version:** 1.0
**Status:** DRAFT (Sprint 0)
**Author:** Jules (System Architect)

## 1. System Overview

RESTI POS is a microservices-based Point of Sale system designed for high-throughput restaurant environments (Dine-in, Takeaway, Delivery). It aims to replace a "48-hour hackathon" prototype with a robust, scalable architecture.

The system relies on a **clean separation of concerns** between services, communicating primarily via synchronous REST APIs (internal network) and ostensibly asynchronous events (Google Pub/Sub) for non-blocking operations in the future.

**Key Goals:**
*   **Reliability:** Strict ownership of data (Single Source of Truth).
*   **Scalability:** Services can be scaled independently (e.g., Orders vs. Logistics).
*   **Auditability:** Every financial action and stock movement is traceable.

## 2. Service Map (Current vs Target)

| Service | Current Responsibilities (Audit) | Target Responsibilities (Sprint 2+) |
| :--- | :--- | :--- |
| **service_menu** | Stores products, categories. | **Canonical Product Master**. Owns Recipes, Allergens, AI Translations. |
| **service_orders** | Handles Tables, Orders, KDS Logic, Payments. | **Order Lifecycle**. Owns Tables, Carts, KDS State. **Delegates** stock logic to Inventory. |
| **service_inventory** | Basic stock levels. | **Warehouse Management**. Stock movements, Waste logs, Purchase Orders, Recipe deductions. |
| **service_crm** | Minimal customer data. | **Customer 360**. Loyalty points, Gift cards, CRM campaigns. |
| **service_logistics** | Basic zone checks. | **Delivery Operations**. Courier tracking, Zone polygons, Dispatcher algorithms. |
| **service_admin** | RBAC, Users, Basic Reporting. | **Enterprise Core**. Staff management, Shifts, **Financial Ledger**, Payroll. |
| **api_gateway** | Pass-through. | Auth termination, Rate limiting, Request logging. |

## 3. Responsibility Boundaries

### `service_orders`
*   **OWNS:** `Order`, `OrderItem`, `Table`, `Seat`, `Bill` (Check), `KdsTicket`.
*   **MUST NOT OWN:** Product definitions (names, prices), Stock levels, Customer profiles (only references IDs), Courier location.
*   **INTERFACES:**
    *   GET `menu/products/{id}` (to validate items).
    *   POST `inventory/allocate` (future: reserve stock).
    *   GET `crm/customers/{id}` (identify guest).

### `service_menu`
*   **OWNS:** `Product`, `Category`, `ModifierGroup`, `Recipe`.
*   **MUST NOT OWN:** Sales history, Stock counts.
*   **INTERFACES:** Serves data to all services.

### `service_inventory`
*   **OWNS:** `Ingredient`, `StockLevel`, `StockMovement`, `WasteLog`.
*   **MUST NOT OWN:** Product sales prices (menu).

### `service_admin`
*   **OWNS:** `User` (Employee), `Role`, `Permission`, `CashDrawer`, `FinancialTransaction`.
*   **MUST NOT OWN:** Live Order state.

## 4. Domain Model Ownership

| Concept | Owner Service | Notes |
| :--- | :--- | :--- |
| **Order / OrderItem** | `service_orders` | The transaction core. |
| **Table / Zone** | `service_orders` | Physical layout state. |
| **Ticket (KDS)** | `service_orders` | Derived from OrderItems, managed via KDS endpoints. |
| **VIP Flow** | `service_orders` | Special status flag on Order/Table. |
| **Delivery Zone** | `service_logistics` | Polygon data for fee calc. |
| **Courier** | `service_logistics` | Staff specializing in delivery. |
| **Recipe** | `service_menu` | Definition of ingredients per product. |
| **Stock Movement** | `service_inventory` | Result of Order, Waste, or Delivery. |
| **Customer** | `service_crm` | Personal data, loyalty balance. |
| **Payment (Record)** | `service_orders` | The act of paying a specific order. |
| **Financial Ledger** | `service_admin` | Aggregated cash drawer / revenue tracking. |

## 5. KDS Target Architecture

The Kitchen Display System (KDS) is not a separate service but a logical module within `service_orders` (for data) and Frontend (for display).

### State Machine (Per Ticket/Item)
1.  **QUEUED**: Sent to kitchen, not yet started.
2.  **IN_PROGRESS**: Cook has acknowledged/started.
3.  **READY**: Food is plated/packed.
4.  **DELIVERED**: Waiter/Courier has taken the item.
5.  **CANCELLED**: Voided.

### Lane Coordination
*   **Kitchen Lane:** Shows all food items.
*   **Pizza Lane:** Filtered view for pizza station.
*   **Bar Lane:** Drinks only.
*   **Expeditor (Menu) Lane:** Aggregates all items per order to coordinate serving.

### Urgency & Cross-Lane
*   **Urgency:** Flag on `KdsTicket` (`priority: NORMAL | URGENT | VIP`).
*   **Timers:** Calculated from `created_at` vs. `now()`. Warning thresholds configured in `service_admin` (future).

## 6. VAT & Payment Logic Placement

*   **VAT Decision:** `service_orders` snapshots the VAT rate at the time of order creation/closure (based on `service_menu` data). Stored in `Order.final_vat_rate` and `OrderItem.vat_rate`.
*   **Invoice (Számlázz.hu):** `service_orders` triggers the request to `service_admin` (or calls integration directly) to generate the invoice document.
*   **Bill Closure:**
    *   **Waiter:** Closes Table orders via POS.
    *   **Bar:** Closes direct Bar orders.
    *   **Courier:** "Closes" Delivery orders upon handover (Cash/Card) -> updates Order status.
    *   **Dispatcher:** Can force-close orders.
*   **Payment Records:**
    *   `Payment` entity in `service_orders` records the method (CASH, CARD) and amount.
    *   This emits an event (future) or API call to `service_admin` to update the `CashDrawer` balance.

## 7. Future Migration Plan

**Sprint 1-2 Goals:**
1.  **Consolidate Enums:** Move all status strings to `backend/core_domain/enums.py`.
2.  **Remove Circular Deps:** Refactor `service_orders` to not import from `service_admin` code directly. Move shared Pydantic schemas to `backend/core_domain` if needed (or keep strictly separate and duplicate for decoupling).
3.  **Standardize IDs:** Ensure all Foreign Keys across services are clearly typed or named (e.g., `customer_id` in orders implies `service_crm` ownership).
