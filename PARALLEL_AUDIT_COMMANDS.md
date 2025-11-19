# 🎯 10 PÁRHUZAMOS AUDIT-PARANCS - POS PROJEKT V1.4

> **HASZNÁLAT**: Másold be mind a 10 parancsot 10 külön Claude Web Code ablakba egyidejű futtatáshoz.
> **MEMÓRIA**: A teljes kód a `main` ágon van (commit: `cb3d2eb`)

---

## 🔍 AUDIT #1: SERVICE_MENU (Kód + Inicializáció)

**CÉL**: Teljes kódaudit a `service_menu` mikroszervízre (modellek, sémák, szolgáltatások, végpontok, inicializáció)

**FELADAT**:
```
[SZEREP] Backend Audit Szakértő vagy, a service_menu mikroszervízt vizsgálod.

[KONTEXTUS]
- Projekt: POS rendszer mikroszervíz architektúrával
- Fókusz: service_menu (termékek, kategóriák, árak kezelése)
- Kód helye: ./backend/service_menu/

[AUDIT FELADATOK]

1. **MODELLEK AUDIT** (./backend/service_menu/models/)
   - Ellenőrizd minden SQLAlchemy modellt
   - Táblák közti kapcsolatok (FK, relationships)
   - Index létrehozás (teljesítmény)
   - Típushibák, nullable mezők konzisztenciája

2. **SÉMÁK AUDIT** (./backend/service_menu/schemas/)
   - Pydantic modellek validációi
   - Request/Response sémák teljes lefedettsége
   - Típuskonverzió hibák (Optional, Union kezelés)

3. **SZOLGÁLTATÁSOK AUDIT** (./backend/service_menu/services/)
   - Üzleti logika hibák
   - DB tranzakciók (commit, rollback kezelés)
   - Error handling (try/except blokkok)
   - N+1 query problémák

4. **VÉGPONTOK AUDIT** (./backend/service_menu/routers/)
   - REST API végpontok (GET, POST, PUT, DELETE)
   - HTTP státuszkódok (200, 201, 400, 404, 500)
   - Request/Response típusozás
   - RBAC integráció (permission check)

5. **INICIALIZÁCIÓ AUDIT**
   - main.py (FastAPI app setup)
   - config.py (környezeti változók, DB URL)
   - dependencies.py (DI pattern használat)
   - Startup/shutdown események

6. **CROSS-SERVICE HÍVÁSOK**
   - HTTP hívások más szolgáltatásokhoz
   - Retry logic, timeout kezelés
   - Error propagáció

[ELVÁRT KIMENET]

Markdown jelentés az alábbi struktúrával:

# SERVICE_MENU AUDIT JELENTÉS

## ✅ HELYES IMPLEMENTÁCIÓK
- [Lista a jól működő funkciókról]

## ⚠️ KRITIKUS HIBÁK
- [Fájl:sor] - Leírás + Javítási javaslat

## 🔶 KÖZEPES PRIORITÁSÚ HIBÁK
- [Fájl:sor] - Leírás + Javítási javaslat

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [Fájl:sor] - Leírás + Javítási javaslat

## 📊 STATISZTIKA
- Vizsgált fájlok száma: X
- Kritikus hibák: X
- Közepes hibák: X
- Alacsony prioritású: X

[FUTTATÁS]
Ellenőrizd a ./backend/service_menu/ teljes könyvtárat.
```

---

## 🔍 AUDIT #2: SERVICE_ORDERS (Kód + Inicializáció)

**CÉL**: Teljes kódaudit a `service_orders` mikroszervízre (rendelések, asztalok, fizetések, ülések)

**FELADAT**:
```
[SZEREP] Backend Audit Szakértő vagy, a service_orders mikroszervízt vizsgálod.

[KONTEXTUS]
- Projekt: POS rendszer mikroszervíz architektúrával
- Fókusz: service_orders (rendelések, asztalok, fizetések, ülések)
- Kód helye: ./backend/service_orders/

[AUDIT FELADATOK]

1. **MODELLEK AUDIT** (./backend/service_orders/models/)
   - Order, OrderItem, Table, Seat, Payment modellek
   - FK kapcsolatok (order -> order_items, table -> seats)
   - Cascade delete/update szabályok
   - Enum típusok (OrderStatus, PaymentStatus, PaymentMethod)
   - Időbélyegek (created_at, updated_at)

2. **SÉMÁK AUDIT** (./backend/service_orders/schemas/)
   - Nested sémák (OrderWithItems, TableWithSeats)
   - Validációk (price >= 0, quantity > 0)
   - Response modellek (exclude sensitive data)

3. **SZOLGÁLTATÁSOK AUDIT** (./backend/service_orders/services/)
   - order_service.py (rendelés lifecycle: create -> update -> close -> pay)
   - table_service.py (asztal állapotkezelés)
   - payment_service.py (tranzakciók, multiple payment methods)
   - seat_service.py (ülőhelyek hozzárendelése)
   - **KRITIKUS**: Stock deduction trigger (HTTP call -> service_inventory)

4. **VÉGPONTOK AUDIT** (./backend/service_orders/routers/)
   - /orders, /tables, /payments, /seats végpontok
   - Filter/Search funkciók (date range, status filter)
   - Pagination implementáció

5. **INICIALIZÁCIÓ AUDIT**
   - main.py (app setup, CORS, middleware)
   - config.py (DB URL, JWT secret)
   - dependencies.py (get_db, get_current_user)

6. **INTER-SERVICE KOMMUNIKÁCIÓ**
   - **KRITIKUS**: Inventory deduction HTTP call
   - Error handling (inventory service down scenario)
   - Rollback stratégia (order created, but stock deduction failed)

[ELVÁRT KIMENET]

# SERVICE_ORDERS AUDIT JELENTÉS

## ✅ HELYES IMPLEMENTÁCIÓK
- [...]

## ⚠️ KRITIKUS HIBÁK
- [Fájl:sor] - Leírás + Javítási javaslat
- **FÓKUSZ**: Stock deduction logic!

## 🔶 KÖZEPES PRIORITÁSÚ HIBÁK
- [...]

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [...]

## 📊 STATISZTIKA
- Vizsgált fájlok: X
- Kritikus: X
- Közepes: X
- Alacsony: X

[FUTTATÁS]
Ellenőrizd a ./backend/service_orders/ teljes könyvtárat.
```

---

## 🔍 AUDIT #3: SERVICE_INVENTORY (Kód + Inicializáció)

**CÉL**: Teljes kódaudit a `service_inventory` mikroszervízre (készlet, beszállítók, stock mozgások)

**FELADAT**:
```
[SZEREP] Backend Audit Szakértő vagy, a service_inventory mikroszervízt vizsgálod.

[KONTEXTUS]
- Projekt: POS rendszer mikroszervíz architektúrával
- Fókusz: service_inventory (készlet, beszállítók, stock deduction)
- Kód helye: ./backend/service_inventory/

[AUDIT FELADATOK]

1. **MODELLEK AUDIT** (./backend/service_inventory/models/)
   - InventoryItem, Supplier, StockMovement modellek
   - FK kapcsolatok (item -> supplier)
   - Quantity tracking (current_stock, min_stock, max_stock)
   - StockMovement típusok (IN, OUT, ADJUSTMENT)

2. **SÉMÁK AUDIT** (./backend/service_inventory/schemas/)
   - StockDeductionRequest/Response
   - InventoryItem sémák (create, update, read)
   - Validációk (stock >= 0, min_stock < max_stock)

3. **SZOLGÁLTATÁSOK AUDIT** (./backend/service_inventory/services/)
   - **KRITIKUS**: StockDeductionService (inventory deduction logic)
   - InventoryService (CRUD operations)
   - SupplierService
   - **KRITIKUS**: Tranzakció kezelés (atomic stock deduction)
   - **KRITIKUS**: Insufficient stock error handling

4. **VÉGPONTOK AUDIT** (./backend/service_inventory/routers/)
   - **/internal/deduct-stock** (KRITIKUS végpont - service_orders hívja)
   - /inventory, /suppliers végpontok
   - Low stock alerts endpoint

5. **INICIALIZÁCIÓ AUDIT**
   - main.py (app setup)
   - config.py (DB URL)
   - dependencies.py (get_db, get_stock_deduction_service)

6. **INTERNAL API SECURITY**
   - **/internal/** végpontok hozzáférés-szabályozása
   - Service-to-service authentication (van-e?)
   - Request validáció (malicious requests filtering)

[ELVÁRT KIMENET]

# SERVICE_INVENTORY AUDIT JELENTÉS

## ✅ HELYES IMPLEMENTÁCIÓK
- [...]

## ⚠️ KRITIKUS HIBÁK
- [Fájl:sor] - **FÓKUSZ**: /internal/deduct-stock implementáció
- [Fájl:sor] - Tranzakció kezelés hibái
- [Fájl:sor] - Insufficient stock scenario

## 🔶 KÖZEPES PRIORITÁSÚ HIBÁK
- [...]

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [...]

## 📊 STATISZTIKA
- Vizsgált fájlok: X
- Kritikus: X
- Közepes: X
- Alacsony: X

[FUTTATÁS]
Ellenőrizd a ./backend/service_inventory/ teljes könyvtárat.
```

---

## 🔍 AUDIT #4: SERVICE_ADMIN (Kód + Inicializáció + RBAC)

**CÉL**: Teljes kódaudit a `service_admin` mikroszervízre (felhasználók, szerepkörök, jogosultságok, auth)

**FELADAT**:
```
[SZEREP] Backend Security + RBAC Audit Szakértő vagy, a service_admin mikroszervízt vizsgálod.

[KONTEXTUS]
- Projekt: POS rendszer mikroszervíz architektúrával
- Fókusz: service_admin (auth, users, roles, permissions, RBAC)
- Kód helye: ./backend/service_admin/

[AUDIT FELADATOK]

1. **AUTH MODELLEK AUDIT** (./backend/service_admin/models/)
   - User, Role, Permission, UserRole, RolePermission modellek
   - Many-to-many kapcsolatok (user <-> roles <-> permissions)
   - Password hashing (bcrypt használat)
   - JWT token refresh mechanism

2. **AUTH SÉMÁK AUDIT** (./backend/service_admin/schemas/)
   - LoginRequest, TokenResponse
   - UserCreate, UserUpdate (password field handling)
   - RoleCreate, PermissionCreate
   - Sensitive data exclusion (password hash)

3. **AUTH SZOLGÁLTATÁSOK AUDIT** (./backend/service_admin/services/)
   - **KRITIKUS**: auth_service.py (login, token generation, refresh)
   - user_service.py (CRUD + password handling)
   - role_service.py, permission_service.py
   - **KRITIKUS**: JWT token expiry (access token 30m, refresh token 7d)

4. **AUTH VÉGPONTOK AUDIT** (./backend/service_admin/routers/)
   - /auth/login, /auth/refresh, /auth/logout
   - /users, /roles, /permissions (RBAC protected)
   - Password reset flow (ha van)

5. **DEPENDENCIES.PY AUDIT**
   - **KRITIKUS**: get_current_user (JWT decode, user validation)
   - **KRITIKUS**: require_permission (permission check logic)
   - **KRITIKUS**: require_role (role check logic)
   - Token expiry validation
   - Disabled user check

6. **RBAC SEED DATA AUDIT** (seed_rbac.py)
   - Default roles (admin, manager, waiter, kitchen_staff)
   - Default permissions (read_menu, create_order, manage_users, etc.)
   - Superuser creation
   - Idempotencia (újrafuttatható-e?)

7. **SECURITY VULNERABILITIES**
   - SQL injection védelem (ORM használat)
   - JWT token signing algorithm (HS256/RS256)
   - Password strength validation
   - Rate limiting (brute force protection)

[ELVÁRT KIMENET]

# SERVICE_ADMIN AUDIT JELENTÉS

## ✅ HELYES IMPLEMENTÁCIÓK
- [...]

## ⚠️ KRITIKUS HIBÁK (SECURITY!)
- [Fájl:sor] - JWT token vulnerabilities
- [Fájl:sor] - RBAC bypass lehetőségek
- [Fájl:sor] - Password handling hibák

## 🔶 KÖZEPES PRIORITÁSÚ HIBÁK
- [...]

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [...]

## 🔐 SECURITY CHECKLIST
- [ ] JWT secret proper handling
- [ ] Password hashing (bcrypt)
- [ ] Permission checks minden védett végponton
- [ ] Disabled user check
- [ ] Token expiry validation

## 📊 STATISZTIKA
- Vizsgált fájlok: X
- Kritikus: X
- Közepes: X
- Alacsony: X

[FUTTATÁS]
Ellenőrizd a ./backend/service_admin/ teljes könyvtárat + dependencies.py + seed_rbac.py
```

---

## 🔍 AUDIT #5: FRONTEND AUTH/PROXY (Vite, Auth Logic, Interceptors)

**CÉL**: Frontend auth rendszer, API proxy, interceptors, token management audit

**FELADAT**:
```
[SZEREP] Frontend Security + Auth Audit Szakértő vagy, a frontend auth rendszert vizsgálod.

[KONTEXTUS]
- Projekt: React + TypeScript + Vite + Zustand frontend
- Fókusz: Auth flow, API interceptors, token management, proxy config
- Kód helye: ./frontend/

[AUDIT FELADATOK]

1. **VITE CONFIG AUDIT** (./frontend/vite.config.ts)
   - **KRITIKUS**: API proxy beállítások
   - Backend szolgáltatások routing (/api/menu -> http://service_menu:8001)
   - CORS konfiguráció
   - Development vs. production config

2. **AUTH SERVICE AUDIT** (./frontend/src/services/authService.ts)
   - Login/logout implementáció
   - Token storage (localStorage vs. sessionStorage)
   - Token refresh logic
   - Auto-logout on token expiry

3. **API CLIENT AUDIT** (./frontend/src/services/api.ts)
   - **KRITIKUS**: Axios interceptors (request/response)
   - **KRITIKUS**: Authorization header injection
   - **KRITIKUS**: Token refresh interceptor (401 -> refresh token -> retry)
   - Error handling (network errors, 500, 403, 404)

4. **AUTH STORE AUDIT** (./frontend/src/stores/authStore.ts)
   - Zustand store setup
   - User state management (currentUser, isAuthenticated)
   - Token storage/retrieval
   - Logout cleanup

5. **PROTECTED ROUTE AUDIT** (./frontend/src/components/auth/ProtectedRoute.tsx)
   - Route guard implementation
   - Redirect to /login if unauthenticated
   - Permission-based rendering (role checks)

6. **AUTH TYPES AUDIT** (./frontend/src/types/auth.ts)
   - User, Role, Permission types
   - LoginRequest, TokenResponse types
   - Type consistency with backend schemas

7. **SECURITY VULNERABILITIES**
   - XSS vulnerabilities (user input sanitization)
   - Token exposure (console.log, localStorage visibility)
   - CSRF protection
   - Sensitive data in URL parameters

[ELVÁRT KIMENET]

# FRONTEND AUTH/PROXY AUDIT JELENTÉS

## ✅ HELYES IMPLEMENTÁCIÓK
- [...]

## ⚠️ KRITIKUS HIBÁK
- [Fájl:sor] - Token management vulnerabilities
- [Fájl:sor] - Interceptor hibák (infinite loop?)
- [Fájl:sor] - Proxy routing errors

## 🔶 KÖZEPES PRIORITÁSÚ HIBÁK
- [...]

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [...]

## 🔐 SECURITY CHECKLIST
- [ ] Token secure storage
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Sensitive data masking
- [ ] Auto-logout on expiry

## 📊 STATISZTIKA
- Vizsgált fájlok: X
- Kritikus: X
- Közepes: X
- Alacsony: X

[FUTTATÁS]
Ellenőrizd a ./frontend/vite.config.ts, ./frontend/src/services/authService.ts, ./frontend/src/services/api.ts, ./frontend/src/stores/authStore.ts, ./frontend/src/components/auth/, ./frontend/src/types/auth.ts fájlokat.
```

---

## 🔍 AUDIT #6: FRONTEND FELHASZNÁLÓI MODULOK (Tables, KDS, Payment)

**CÉL**: Felhasználói funkciók audit (asztalkezelés, konyhakezelés, fizetés)

**FELADAT**:
```
[SZEREP] Frontend Funkcionális Audit Szakértő vagy, a felhasználói modulokat vizsgálod.

[KONTEXTUS]
- Projekt: React + TypeScript frontend
- Fókusz: TableMap, KDS, Payment komponensek és szolgáltatások
- Kód helye: ./frontend/src/

[AUDIT FELADATOK]

1. **TABLE MAP AUDIT** (./frontend/src/components/table-map/)
   - TableMap.tsx, TableIcon.tsx
   - Asztal állapot vizualizáció (free, occupied, reserved)
   - Click event handling (asztal kiválasztása)
   - Real-time update (WebSocket vagy polling?)

2. **TABLE SERVICE AUDIT** (./frontend/src/services/tableService.ts)
   - API calls (GET /tables, POST /tables, PUT /tables/:id)
   - Table status update
   - Error handling
   - Type safety (Table type)

3. **KDS (Kitchen Display System) AUDIT** (./frontend/src/components/kds/)
   - KdsLane.tsx, KdsCard.tsx
   - Order lane rendering (NEW, PREPARING, READY)
   - Drag-and-drop (ha van)
   - Status update (order -> PREPARING -> READY)

4. **KDS SERVICE AUDIT** (./frontend/src/services/kdsService.ts)
   - API calls (GET /orders?status=PENDING)
   - Order status update (PUT /orders/:id/status)
   - Real-time updates (WebSocket?)
   - Error handling

5. **PAYMENT MODAL AUDIT** (./frontend/src/components/payment/PaymentModal.tsx)
   - Payment method selection (CASH, CARD, MIXED)
   - Multiple payment handling (split bill)
   - Payment confirmation
   - Error display (insufficient stock, payment failed)

6. **PAYMENT SERVICE AUDIT** (./frontend/src/services/paymentService.ts)
   - API calls (POST /payments)
   - Payment request validation (amount > 0)
   - Success/error handling
   - Receipt generation (ha van)

7. **MENU SERVICE AUDIT** (./frontend/src/services/menuService.ts)
   - API calls (GET /products, GET /categories)
   - Product search/filter
   - Image URL handling
   - Caching strategy (ha van)

[ELVÁRT KIMENET]

# FRONTEND FELHASZNÁLÓI MODULOK AUDIT JELENTÉS

## ✅ HELYES IMPLEMENTÁCIÓK
- [...]

## ⚠️ KRITIKUS HIBÁK
- [Fájl:sor] - Payment flow hibák
- [Fájl:sor] - KDS order status update hibák
- [Fájl:sor] - Table status inconsistency

## 🔶 KÖZEPES PRIORITÁSÚ HIBÁK
- [...]

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [...]

## 📊 STATISZTIKA
- Vizsgált fájlok: X
- Kritikus: X
- Közepes: X
- Alacsony: X

[FUTTATÁS]
Ellenőrizd a ./frontend/src/components/table-map/, ./frontend/src/components/kds/, ./frontend/src/components/payment/, ./frontend/src/services/tableService.ts, ./frontend/src/services/kdsService.ts, ./frontend/src/services/paymentService.ts, ./frontend/src/services/menuService.ts fájlokat.
```

---

## 🔍 AUDIT #7: FRONTEND ADMIN UI (Admin CRUD, RBAC)

**CÉL**: Admin felület audit (CRUD műveletek, szerepkör-alapú megjelenítés)

**FELADAT**:
```
[SZEREP] Frontend Admin UI Audit Szakértő vagy, az admin komponenseket vizsgálod.

[KONTEXTUS]
- Projekt: React + TypeScript frontend
- Fókusz: Admin CRUD komponensek (Products, Employees, Roles, Tables, etc.)
- Kód helye: ./frontend/src/components/admin/

[AUDIT FELADATOK]

1. **PRODUCT ADMIN AUDIT**
   - ProductList.tsx, ProductEditor.tsx
   - CRUD műveletek (Create, Read, Update, Delete)
   - Form validáció (name required, price >= 0)
   - Image upload (ha van)
   - Category selection

2. **EMPLOYEE ADMIN AUDIT**
   - EmployeeList.tsx, EmployeeEditor.tsx
   - User CRUD műveletek
   - Password handling (create vs. update)
   - Role assignment (multi-select)
   - Active/inactive toggle

3. **ROLE ADMIN AUDIT**
   - RoleList.tsx, RoleEditor.tsx
   - Role CRUD műveletek
   - Permission assignment (checkbox list)
   - Default roles protection (admin, manager ne legyen törölhető)

4. **TABLE ADMIN AUDIT**
   - TableList.tsx, TableEditor.tsx
   - Table CRUD műveletek
   - Capacity validation (capacity > 0)
   - Position/layout editing

5. **COUPON ADMIN AUDIT**
   - CouponList.tsx, CouponEditor.tsx
   - Coupon CRUD műveletek
   - Discount type (PERCENTAGE, FIXED)
   - Validity date validation (start < end)

6. **CRM ADMIN AUDIT** (Customer, Vehicle, Asset, Logistics)
   - CustomerList.tsx, CustomerEditor.tsx
   - VehicleList.tsx, VehicleEditor.tsx
   - AssetList.tsx, AssetEditor.tsx, AssetGroupList.tsx, AssetGroupEditor.tsx
   - AssetServiceList.tsx, VehicleMaintenanceList.tsx, VehicleRefuelingList.tsx
   - CRUD konzisztencia

7. **ADMIN SERVICES AUDIT**
   - ./frontend/src/services/employeeService.ts
   - ./frontend/src/services/roleService.ts
   - ./frontend/src/services/financeService.ts
   - ./frontend/src/services/assetService.ts
   - ./frontend/src/services/logisticsService.ts
   - ./frontend/src/services/vehicleService.ts
   - ./frontend/src/services/crmService.ts
   - API calls consistency (GET, POST, PUT, DELETE)
   - Error handling
   - Type safety

8. **RBAC UI INTEGRATION**
   - Permission-based button visibility (canDelete, canEdit)
   - Role-based menu items
   - Unauthorized access handling

[ELVÁRT KIMENET]

# FRONTEND ADMIN UI AUDIT JELENTÉS

## ✅ HELYES IMPLEMENTÁCIÓK
- [...]

## ⚠️ KRITIKUS HIBÁK
- [Fájl:sor] - CRUD operation failures
- [Fájl:sor] - RBAC bypass vulnerabilities
- [Fájl:sor] - Form validation missing

## 🔶 KÖZEPES PRIORITÁSÚ HIBÁK
- [...]

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [...]

## 📊 STATISZTIKA
- Vizsgált komponensek: X
- Vizsgált szolgáltatások: X
- Kritikus: X
- Közepes: X
- Alacsony: X

[FUTTATÁS]
Ellenőrizd a ./frontend/src/components/admin/ könyvtárat és a ./frontend/src/services/ admin-related szolgáltatásokat (employeeService.ts, roleService.ts, financeService.ts, assetService.ts, logisticsService.ts, vehicleService.ts, crmService.ts).
```

---

## 🔍 AUDIT #8: FINAL SECURITY AUDIT (RBAC, JWT, Permissions)

**CÉL**: Végső biztonsági audit a teljes RBAC, JWT, permission rendszerre

**FELADAT**:
```
[SZEREP] Senior Security Audit Szakértő vagy, a teljes auth/authz rendszert vizsgálod.

[KONTEXTUS]
- Projekt: POS rendszer mikroszervíz architektúrával
- Fókusz: **TELJES** security audit (backend + frontend)
- Kritikus: RBAC bypass, JWT vulnerabilities, permission escalation

[AUDIT FELADATOK]

1. **JWT TOKEN SECURITY AUDIT**
   - **Backend**: service_admin dependencies.py (get_current_user)
   - JWT decode logic (algorithm validation)
   - Token expiry check (exp claim)
   - Token signature validation
   - Disabled user check
   - **Frontend**: api.ts interceptors (Authorization header)
   - Token refresh flow (401 -> refresh -> retry)
   - Token storage security (XSS protection)

2. **RBAC IMPLEMENTATION AUDIT**
   - **Backend**: service_admin dependencies.py (require_permission, require_role)
   - Permission check logic (user -> roles -> permissions)
   - Role hierarchy (ha van)
   - Multiple roles support
   - **Frontend**: ProtectedRoute.tsx, admin komponensek
   - Permission-based rendering
   - Role-based menu visibility

3. **PERMISSION INTEGRITY AUDIT**
   - **Backend**: seed_rbac.py
   - Default permissions lista (completeness)
   - Permission-to-resource mapping (read_menu, create_order, manage_users)
   - Idempotencia (újrafuttatás safe?)
   - **Cross-check**: Minden védett végpont rendelkezik permission checkkel?

4. **ENDPOINT PROTECTION AUDIT**
   - **service_menu**: Védett végpontok (require_permission dependency)
   - **service_orders**: Védett végpontok
   - **service_inventory**: /internal/ védelem (service-to-service auth?)
   - **service_admin**: /auth végpontok (public) vs. /users, /roles (protected)

5. **PASSWORD SECURITY AUDIT**
   - **Backend**: service_admin auth_service.py
   - Bcrypt usage (password hashing)
   - Password strength validation (min length, complexity)
   - Password reset flow security (ha van)

6. **SESSION MANAGEMENT AUDIT**
   - Token expiry (access token 30m, refresh token 7d)
   - Logout implementation (token invalidation?)
   - Concurrent session handling
   - Remember me functionality (ha van)

7. **AUTHORIZATION BYPASS TESTING**
   - **Szimuláld**: User A megpróbál User B erőforrásához hozzáférni
   - **Szimuláld**: Waiter role megpróbál admin műveletet végrehajtani
   - **Szimuláld**: Expired token használat
   - **Szimuláld**: Malformed token

[ELVÁRT KIMENET]

# FINAL SECURITY AUDIT JELENTÉS

## ✅ BIZTONSÁGOS IMPLEMENTÁCIÓK
- [...]

## 🚨 KRITIKUS BIZTONSÁGI RÉSEK (HOTFIX!)
- [Fájl:sor] - JWT vulnerability (pl. weak algorithm)
- [Fájl:sor] - RBAC bypass lehetőség
- [Fájl:sor] - Permission escalation
- [Fájl:sor] - Unprotected endpoint

## ⚠️ KÖZEPES BIZTONSÁGI KOCKÁZATOK
- [...]

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [...]

## 🔐 SECURITY PENETRATION TEST RESULTS
| Test Scenario | Result | Details |
|---------------|--------|---------|
| JWT expired token | ✅/❌ | ... |
| RBAC bypass (waiter -> admin) | ✅/❌ | ... |
| Permission escalation | ✅/❌ | ... |
| Unauthorized resource access | ✅/❌ | ... |

## 📊 STATISZTIKA
- Vizsgált fájlok: X
- Kritikus: X
- Közepes: X
- Alacsony: X

[FUTTATÁS]
Ellenőrizd: ./backend/service_admin/dependencies.py, ./backend/service_admin/services/auth_service.py, ./backend/service_admin/seed_rbac.py, ./frontend/src/services/api.ts, ./frontend/src/services/authService.ts, ./frontend/src/components/auth/ProtectedRoute.tsx, valamint minden backend service védett végpontját.
```

---

## 🔍 AUDIT #9: INTER-SERVICE TRIGGERS (Orders → Inventory/Admin)

**CÉL**: Szolgáltatások közötti HTTP hívások audit (trigger chain, error propagation)

**FELADAT**:
```
[SZEREP] Distributed Systems Audit Szakértő vagy, az inter-service kommunikációt vizsgálod.

[KONTEXTUS]
- Projekt: POS rendszer mikroszervíz architektúrával
- Fókusz: HTTP trigger chain (service_orders -> service_inventory, service_orders -> service_admin)
- Kritikus: Tranzakciós integritás, error handling, rollback stratégia

[AUDIT FELADATOK]

1. **ORDERS → INVENTORY TRIGGER AUDIT**
   - **Source**: service_orders/services/order_service.py vagy payment_service.py
   - **Target**: service_inventory/routers/internal.py (/internal/deduct-stock)
   - **Flow**: Order creation/payment -> Stock deduction HTTP POST
   - **Ellenőrizd**:
     - HTTP client konfigurálás (timeout, retry)
     - Request payload (product_id, quantity)
     - Response handling (success vs. insufficient stock)
     - **KRITIKUS**: Error scenario (inventory service down, network timeout)
     - **KRITIKUS**: Rollback logic (ha inventory hívás fail, order rollback?)

2. **INVENTORY DEDUCTION ENDPOINT AUDIT**
   - **Backend**: service_inventory/routers/internal.py
   - **/internal/deduct-stock** végpont
   - **Ellenőrizd**:
     - Request validation (product_id valid, quantity > 0)
     - Stock sufficiency check (current_stock >= quantity)
     - Atomic update (DB transaction)
     - Error response (400 Insufficient Stock, 404 Product Not Found, 500 Internal Error)
     - **KRITIKUS**: Idempotencia (ugyanaz a request kétszer meghívva ne okozzon dupla deduction-t)

3. **ORDERS → ADMIN TRIGGERS AUDIT** (ha van)
   - **Példa**: Order creation trigger -> Admin log/audit trail
   - HTTP hívások azonosítása
   - Error handling

4. **SERVICE DISCOVERY AUDIT**
   - **Backend**: service_orders/config.py (INVENTORY_SERVICE_URL)
   - Environment variables (SERVICE_INVENTORY_URL)
   - Hardcoded URLs vs. dynamic discovery
   - Docker compose networking (service names vs. localhost)

5. **TIMEOUT & RETRY LOGIC AUDIT**
   - HTTP client timeout beállítások (5s, 10s?)
   - Retry stratégia (exponential backoff, max retries)
   - Circuit breaker pattern (ha van)

6. **ERROR PROPAGATION AUDIT**
   - **Szimuláld**: Inventory service DOWN
   - **Szimuláld**: Network timeout
   - **Szimuláld**: Insufficient stock response
   - **Ellenőrizd**: Frontend felé küldött error message (user-friendly?)

7. **TRANSACTION CONSISTENCY AUDIT**
   - **Scenario 1**: Order created, inventory deduction SUCCESS -> ✅
   - **Scenario 2**: Order created, inventory deduction FAIL -> ❌ Order rollback?
   - **Scenario 3**: Inventory deduction SUCCESS, but order commit FAIL -> ❌ Orphan stock deduction?
   - **KRITIKUS**: Distributed transaction handling (2PC, Saga pattern, vagy manual rollback?)

[ELVÁRT KIMENET]

# INTER-SERVICE TRIGGERS AUDIT JELENTÉS

## ✅ HELYES IMPLEMENTÁCIÓK
- [...]

## ⚠️ KRITIKUS HIBÁK (TRANSACTION INTEGRITY!)
- [Fájl:sor] - Missing rollback logic
- [Fájl:sor] - No timeout/retry handling
- [Fájl:sor] - Error propagation missing
- [Fájl:sor] - Idempotencia hiánya

## 🔶 KÖZEPES PRIORITÁSÚ HIBÁK
- [...]

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [...]

## 🔄 TRANSACTION FLOW DIAGRAM
```
[Order Created] --HTTP POST--> [Inventory Deduction]
     |                                  |
     |                              SUCCESS ✅
     |                                  |
[Commit Order] <-----------------------+
     |
   FAIL ❌ -> [Rollback Order?]
```

## 📊 STATISZTIKA
- Vizsgált inter-service hívások: X
- Kritikus: X
- Közepes: X
- Alacsony: X

[FUTTATÁS]
Ellenőrizd: ./backend/service_orders/services/ (order_service.py, payment_service.py), ./backend/service_inventory/routers/internal.py, ./backend/service_orders/config.py, ./backend/service_inventory/services/ (stock_deduction_service.py vagy hasonló).
```

---

## 🔍 AUDIT #10: DATABASE SCHEMA CONSISTENCY (Cross-Service FK, Schema vs. Model)

**CÉL**: Adatbázis séma konzisztencia audit (cross-service FK, séma dokumentáció vs. SQLAlchemy modellek)

**FELADAT**:
```
[SZEREP] Database Architect Audit Szakértő vagy, az adatbázis séma konzisztenciát vizsgálod.

[KONTEXTUS]
- Projekt: POS rendszer mikroszervíz architektúrával
- Fókusz: Cross-service foreign keys, schema vs. model consistency
- Referencia: DATABASE_SCHEMA.md dokumentáció

[AUDIT FELADATOK]

1. **SCHEMA DOKUMENTÁCIÓ AUDIT**
   - **Fájl**: ./DATABASE_SCHEMA.md
   - **Ellenőrizd**:
     - Minden tábla dokumentálva van?
     - Oszlopok (név, típus, nullable, default)
     - Foreign keys (referencia táblák)
     - Indexes (performance optimalizáció)
     - Unique constraints

2. **SQLALCHEMY MODELLEK vs. SCHEMA AUDIT**
   - **service_menu**: models/ vs. DATABASE_SCHEMA.md
     - products tábla (id, name, description, price, category_id, image_url, is_available, created_at, updated_at)
     - categories tábla (id, name, description, parent_id)
   - **service_orders**: models/ vs. DATABASE_SCHEMA.md
     - orders tábla (id, table_id, employee_id, status, total_amount, created_at, updated_at, closed_at)
     - order_items tábla (id, order_id, product_id, quantity, unit_price, subtotal, notes)
     - tables tábla (id, number, capacity, status, position_x, position_y)
     - seats tábla (id, table_id, seat_number, employee_id)
     - payments tábla (id, order_id, amount, payment_method, payment_status, transaction_id, created_at)
   - **service_inventory**: models/ vs. DATABASE_SCHEMA.md
     - inventory_items tábla (id, product_id, current_stock, min_stock, max_stock, unit, supplier_id, last_restocked)
     - suppliers tábla (id, name, contact_person, email, phone, address)
     - stock_movements tábla (id, inventory_item_id, movement_type, quantity, notes, created_at)
   - **service_admin**: models/ vs. DATABASE_SCHEMA.md
     - users tábla (id, username, email, password_hash, full_name, is_active, created_at, updated_at)
     - roles tábla (id, name, description)
     - permissions tábla (id, name, resource, action, description)
     - user_roles tábla (user_id, role_id)
     - role_permissions tábla (role_id, permission_id)
   - **Ellenőrizd**: Típusok, nullable fields, default értékek, FK references

3. **CROSS-SERVICE FOREIGN KEYS AUDIT**
   - **KRITIKUS**: order_items.product_id -> products.id (service_orders -> service_menu)
     - **Probléma**: Külön DB-k esetén FK constraint NEM LEHET!
     - **Ellenőrizd**: Van-e FK deklarálva a modellben? (relationship() OK, ForeignKey() ROSSZ)
     - **Ellenőrizd**: Manual validation a service rétegben (product_id existence check via HTTP)
   - **KRITIKUS**: orders.employee_id -> users.id (service_orders -> service_admin)
     - Hasonló ellenőrzés
   - **KRITIKUS**: inventory_items.product_id -> products.id (service_inventory -> service_menu)
     - Hasonló ellenőrzés

4. **MIGRATION FILES AUDIT** (ha vannak)
   - **Könyvtárak**: ./backend/service_*/migrations/
   - Alembic migration fájlok
   - **Ellenőrizd**:
     - Minden model változás rendelkezik migration-nel?
     - Migration order (dependency)
     - Rollback scriptek (downgrade)

5. **INDEX OPTIMIZATION AUDIT**
   - **Ellenőrizd**: Gyakran queried oszlopok rendelkeznek indexszel?
     - products.category_id (JOIN categories)
     - order_items.order_id (JOIN orders)
     - order_items.product_id (JOIN products - ha same DB)
     - orders.table_id, orders.employee_id
     - inventory_items.product_id, inventory_items.supplier_id
     - user_roles.user_id, user_roles.role_id
   - **SQLAlchemy**: `Index()` deklarációk a modellekben

6. **DATA INTEGRITY AUDIT**
   - **CASCADE delete** szabályok (pl. order delete -> order_items cascade delete)
   - **RESTRICT delete** védelem (pl. role delete restricted if user_roles exists)
   - **ON UPDATE CASCADE** (FK update propagation)
   - **Nullable constraints** (pl. order.table_id NOT NULL)

7. **DATABASE SEEDING AUDIT**
   - **Fájl**: ./seed_demo_data.py
   - **Ellenőrizd**:
     - Seed data consistency (FK references valid)
     - Idempotencia (újrafuttatható?)
     - Default data (superuser, default roles)

[ELVÁRT KIMENET]

# DATABASE SCHEMA CONSISTENCY AUDIT JELENTÉS

## ✅ KONZISZTENS IMPLEMENTÁCIÓK
- [...]

## ⚠️ KRITIKUS INKONZISZTENCIÁK
- [Modell fájl:sor] - Schema vs. Model mismatch (TYPE, NULLABLE, DEFAULT)
- [Modell fájl:sor] - Cross-service FK constraint (REMOVE ForeignKey!)
- [Migration fájl] - Missing migration for model change

## 🔶 KÖZEPES PRIORITÁSÚ HIBÁK
- [Modell fájl:sor] - Missing index on frequently queried column
- [Modell fájl:sor] - Incorrect cascade behavior

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK
- [Dokumentáció] - DATABASE_SCHEMA.md outdated

## 📊 SCHEMA CONSISTENCY MATRIX
| Service | Model Files | Schema Documented | Migrations Exist | Consistency |
|---------|-------------|-------------------|------------------|-------------|
| service_menu | X | ✅/❌ | ✅/❌ | ✅/❌ |
| service_orders | X | ✅/❌ | ✅/❌ | ✅/❌ |
| service_inventory | X | ✅/❌ | ✅/❌ | ✅/❌ |
| service_admin | X | ✅/❌ | ✅/❌ | ✅/❌ |

## 🔗 CROSS-SERVICE FK AUDIT
| FK Reference | Current Implementation | Should Be |
|--------------|------------------------|-----------|
| order_items.product_id -> products.id | ForeignKey() ❌ / relationship() ✅ | Manual validation via HTTP |
| orders.employee_id -> users.id | ... | ... |
| inventory_items.product_id -> products.id | ... | ... |

## 📊 STATISZTIKA
- Vizsgált modellek: X
- Kritikus: X
- Közepes: X
- Alacsony: X

[FUTTATÁS]
Ellenőrizd: ./DATABASE_SCHEMA.md, ./backend/service_menu/models/, ./backend/service_orders/models/, ./backend/service_inventory/models/, ./backend/service_admin/models/, ./backend/service_*/migrations/ (ha vannak), ./seed_demo_data.py
```

---

## 🚀 FUTTATÁSI ÚTMUTATÓ (Karmester számára)

### Párhuzamos Futtatás (10 Claude Web Code ablak)

1. **Nyiss meg 10 Claude Web Code ablakot** (web böngészőben)
2. **Másold be az alábbi parancsokat** (1 parancs per ablak):
   - Ablak 1: **AUDIT #1** (service_menu)
   - Ablak 2: **AUDIT #2** (service_orders)
   - Ablak 3: **AUDIT #3** (service_inventory)
   - Ablak 4: **AUDIT #4** (service_admin)
   - Ablak 5: **AUDIT #5** (Frontend Auth/Proxy)
   - Ablak 6: **AUDIT #6** (Frontend User Modules)
   - Ablak 7: **AUDIT #7** (Frontend Admin UI)
   - Ablak 8: **AUDIT #8** (Final Security Audit)
   - Ablak 9: **AUDIT #9** (Inter-Service Triggers)
   - Ablak 10: **AUDIT #10** (Database Schema Consistency)

3. **Futtasd az összes auditot egyidejűleg** (10 ágensen párhuzamosan)
4. **Várj, amíg mind a 10 audit befejeződik** (~5-10 perc)
5. **Összegyűjtöd az auditok kimeneteit** (10 Markdown jelentés)
6. **Aggregálás**: Egyesítsd a jelentéseket egy **MASTER_AUDIT_REPORT.md** fájlba

---

## 📋 ÖSSZESÍTŐ SABLON (Master Report)

A 10 audit után készíts egy master jelentést:

```markdown
# 🎯 MASTER AUDIT REPORT - POS PROJEKT V1.4

## 📊 ÖSSZESÍTETT STATISZTIKA
- Vizsgált fájlok összesen: XXX
- Kritikus hibák: XX
- Közepes hibák: XX
- Alacsony prioritású: XX

## 🚨 TOP 10 KRITIKUS HIBA (HOTFIX!)
1. [Audit #X] [Fájl:sor] - Leírás
2. ...

## ⚠️ TOP 20 KÖZEPES PRIORITÁSÚ HIBA
1. [Audit #X] [Fájl:sor] - Leírás
2. ...

## 🔵 ALACSONY PRIORITÁSÚ JAVÍTÁSOK (Backlog)
- [Lista...]

## ✅ HELYES IMPLEMENTÁCIÓK (Best Practices)
- [Lista...]

## 📈 KÖVETKEZŐ LÉPÉSEK
1. HOTFIX ág létrehozása
2. TOP 10 kritikus hiba javítása
3. Security patch release (v1.4.1)
4. Közepes prioritású hibák backlog-ba
```

---

## ✅ ELVÁRT EREDMÉNY

- **10 részletes audit jelentés** (Markdown formátumban)
- **1 aggregált master jelentés** (összes audit eredményével)
- **Kritikus hibák prioritizálva** (HOTFIX jelölés)
- **Közepes és alacsony prioritású backlog** (jövőbeli sprintek)

---

**STÁTUSZ**: ✅ Audit parancsok készen állnak a párhuzamos futtatásra!
