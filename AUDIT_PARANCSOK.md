# 🔍 HIBAKERESŐ AUDIT SPRINT - 8 AUDIT-PARANCS

**Verzió:** 1.0
**Cél:** A main ág (commit cb3d2eb) teljes kódbázisának átvizsgálása rejtett hibák, import hibák, elírások, hibás proxy-hívások és inkonzisztenciák felderítésére.

**Kontextus:** A rendszer "nem használható" állapotban van. Feltételezés szerint az "Integrátor" konfliktusfeloldás közben bevitt hibákat, amelyek miatt a rendszer nem működik megfelelően.

---

## 📋 Útmutató a Karmester számára

Minden parancsot **KÜLÖNÁLLÓ Claude Web Code ablakban** futtass. Minden végrehajtó ágens egy-egy modult vizsgál meg teljesen függetlenül.

**Fontos:**
- Minden ágens a `main` ágon dolgozik (commit: `cb3d2eb`)
- Minden ágens csak **LISTÁZZA** a hibákat, **NE JAVÍTSA** őket
- A kimenet mindig strukturált Markdown formátumú legyen
- Minden hibához add meg a **pontos fájlnevet és sorszámot** (pl. `main.py:42`)

---

## AUDIT 1️⃣: service_menu (Modul 0)

### 🎯 Cél
A `service_menu` mikroszolgáltatás teljes kódbázisának átvizsgálása, különös tekintettel a Vertex AI integráció és az `init_db` működésére.

### 📁 Ellenőrizendő fájlok

**Főbb fájlok:**
- `backend/service_menu/main.py`
- `backend/service_menu/Dockerfile`
- `backend/service_menu/config.py`
- `backend/service_menu/database.py`
- `backend/service_menu/requirements.txt`

**Models könyvtár:**
- `backend/service_menu/models/__init__.py`
- `backend/service_menu/models/base.py`
- `backend/service_menu/models/product.py`
- `backend/service_menu/models/category.py`
- `backend/service_menu/models/modifier.py`
- `backend/service_menu/models/modifier_group.py`
- `backend/service_menu/models/image_asset.py`
- `backend/service_menu/models/channel_visibility.py`
- `backend/service_menu/models/associations.py`

**Services könyvtár:**
- `backend/service_menu/services/__init__.py`
- `backend/service_menu/services/product_service.py`
- `backend/service_menu/services/category_service.py`
- `backend/service_menu/services/modifier_service.py`
- `backend/service_menu/services/channel_service.py`
- `backend/service_menu/services/gcs_service.py`
- `backend/service_menu/services/translation_service.py`

**Routers könyvtár:**
- `backend/service_menu/routers/__init__.py`
- `backend/service_menu/routers/products.py`
- `backend/service_menu/routers/categories.py`
- `backend/service_menu/routers/modifier_groups.py`
- `backend/service_menu/routers/channels.py`
- `backend/service_menu/routers/images.py`

### 🔎 Keresendő hibák

1. **Import hibák:**
   - Hiányzó vagy rossz `import` utasítások
   - `from X import Y` helyett `from X import Z` (elírás)
   - Circular import problémák

2. **Vertex AI és init_db problémák:**
   - `init_db()` függvény meghívása helyes-e a `main.py`-ban?
   - Vertex AI credentials inicializálása helyes-e?
   - `translation_service.py` - Vertex AI kliens lazy inicializációja működik-e?

3. **Model definíció hibák:**
   - ForeignKey, relationship hibák
   - SQLAlchemy column típus elírások
   - Missing vagy helytelen `__tablename__`

4. **Router regisztráció hibák:**
   - Minden router be van-e regisztrálva a `main.py`-ban?
   - A prefix-ek helyesek-e? (pl. `/products`, `/categories`)

5. **Config hibák:**
   - Environment változók helyes olvasása
   - Port konfiguráció (8000-nek kellene lennie)

6. **Dockerfile hibák:**
   - EXPOSE port helyes-e (8000)?
   - requirements.txt telepítése OK?

### 📤 Kimenet formátum

```markdown
# AUDIT 1: service_menu - HIBÁK

## 1. Import hibák
- [ ] `fájl:sor` - Leírás (pl. `models/__init__.py:5` - Hiányzik a `Product` import)

## 2. Vertex AI / init_db problémák
- [ ] `fájl:sor` - Leírás

## 3. Model definíció hibák
- [ ] `fájl:sor` - Leírás

## 4. Router regisztráció hibák
- [ ] `fájl:sor` - Leírás

## 5. Config hibák
- [ ] `fájl:sor` - Leírás

## 6. Dockerfile hibák
- [ ] `fájl:sor` - Leírás

## 7. Egyéb hibák
- [ ] `fájl:sor` - Leírás

---

**Összesen:** X db hiba
**Kritikus:** Y db
**Közepes:** Z db
```

---

## AUDIT 2️⃣: service_orders (Modul 1-4)

### 🎯 Cél
A `service_orders` mikroszolgáltatás teljes átvizsgálása, különös tekintettel a triggerekre, Split-Check funkcióra és NTAK ÁFA váltásra.

### 📁 Ellenőrizendő fájlok

**Főbb fájlok:**
- `backend/service_orders/main.py`
- `backend/service_orders/Dockerfile`
- `backend/service_orders/config.py`
- `backend/service_orders/requirements.txt`

**Models könyvtár:**
- `backend/service_orders/models/__init__.py`
- `backend/service_orders/models/database.py`
- `backend/service_orders/models/table.py`
- `backend/service_orders/models/seat.py`
- `backend/service_orders/models/order.py`
- `backend/service_orders/models/order_item.py`
- `backend/service_orders/models/payment.py`

**Services könyvtár:**
- `backend/service_orders/services/__init__.py`
- `backend/service_orders/services/table_service.py`
- `backend/service_orders/services/seat_service.py`
- `backend/service_orders/services/order_service.py` ⚠️ **TRIGGEREK!**
- `backend/service_orders/services/order_item_service.py`
- `backend/service_orders/services/payment_service.py` ⚠️ **SPLIT-CHECK!**

**Routers könyvtár:**
- `backend/service_orders/routers/__init__.py`
- `backend/service_orders/routers/tables.py`
- `backend/service_orders/routers/seats.py`
- `backend/service_orders/routers/orders.py`
- `backend/service_orders/routers/order_items.py`

### 🔎 Keresendő hibák

1. **Import hibák:**
   - Model importok helyessége
   - Service kereszthivatkozások

2. **Trigger és cascade problémák:**
   - `order_service.py` - SQL triggerek helyes definíciója
   - Seat -> Order -> OrderItem cascade működése
   - Seat lezárása -> kapcsolódó rendelések állapotváltozása OK?

3. **Split-Check logika:**
   - `payment_service.py` - Split-Check számítások helyesek?
   - Seat szerinti költségfelosztás működik?
   - NTAK ÁFA váltás (27% <-> különböző kulcsok) helyes?

4. **NTAK ÁFA váltás:**
   - OrderItem model - ÁFA százalék mezők helyesek?
   - Payment számítások tartalmazzák az ÁFA logikát?

5. **Router regisztráció:**
   - Minden router regisztrálva van a `main.py`-ban?
   - Helyes prefix-ek (pl. `/tables`, `/orders`, `/seats`)?

6. **KDS endpoint:**
   - Van-e KDS specifikus endpoint a routerekben?
   - `/kds/pending`, `/kds/ready` stb. léteznek?

7. **Config és Port:**
   - Port 8001-nek kellene lennie
   - Database URL helyes?

### 📤 Kimenet formátum

```markdown
# AUDIT 2: service_orders - HIBÁK

## 1. Import hibák
- [ ] `fájl:sor` - Leírás

## 2. Trigger és cascade problémák
- [ ] `fájl:sor` - Leírás

## 3. Split-Check logika hibák
- [ ] `fájl:sor` - Leírás

## 4. NTAK ÁFA váltás hibák
- [ ] `fájl:sor` - Leírás

## 5. Router regisztráció hibák
- [ ] `fájl:sor` - Leírás

## 6. KDS endpoint hibák
- [ ] `fájl:sor` - Leírás

## 7. Config hibák
- [ ] `fájl:sor` - Leírás

## 8. Egyéb hibák
- [ ] `fájl:sor` - Leírás

---

**Összesen:** X db hiba
**Kritikus:** Y db
**Közepes:** Z db
```

---

## AUDIT 3️⃣: service_inventory (Modul 5)

### 🎯 Cél
A `service_inventory` mikroszolgáltatás átvizsgálása, különös tekintettel a Recipe model ForeignKey javításaira és az OCR Lazy Init-re.

### 📁 Ellenőrizendő fájlok

**Főbb fájlok:**
- `backend/service_inventory/main.py`
- `backend/service_inventory/Dockerfile`
- `backend/service_inventory/config.py` ⚠️ **PORT 8003!**
- `backend/service_inventory/requirements.txt`

**Models könyvtár:**
- `backend/service_inventory/models/__init__.py`
- `backend/service_inventory/models/database.py`
- `backend/service_inventory/models/inventory_item.py`
- `backend/service_inventory/models/recipe.py` ⚠️ **FOREIGNKEY FIX!**
- `backend/service_inventory/models/supplier_invoice.py`
- `backend/service_inventory/models/daily_inventory_sheet.py`

**Services könyvtár:**
- `backend/service_inventory/services/__init__.py`
- `backend/service_inventory/services/inventory_service.py`
- `backend/service_inventory/services/recipe_service.py`
- `backend/service_inventory/services/ocr_service.py` ⚠️ **LAZY INIT!**
- `backend/service_inventory/services/daily_inventory_service.py`

**Routers könyvtár:**
- `backend/service_inventory/routers/__init__.py`
- `backend/service_inventory/routers/inventory_items.py`
- `backend/service_inventory/routers/recipes.py`
- `backend/service_inventory/routers/invoices.py`
- `backend/service_inventory/routers/daily_inventory.py`

### 🔎 Keresendő hibák

1. **Import hibák:**
   - Model és service importok
   - OCR library importok (Google Vision API)

2. **Recipe model ForeignKey hibák:**
   - `models/recipe.py` - ForeignKey kapcsolatok helyesek?
   - `product_id` kapcsolat helyes?
   - Relationship definíciók OK?

3. **OCR Service Lazy Init:**
   - `services/ocr_service.py` - Google Vision API kliens lazy inicializációja helyes?
   - Credentials kezelése OK?
   - Inicializáció csak első használatkor történik?

4. **Port konfiguráció:**
   - `config.py` - PORT = 8003?
   - `Dockerfile` - EXPOSE 8003?

5. **Router regisztráció:**
   - Minden router regisztrálva a `main.py`-ban?
   - Prefix-ek helyesek?

6. **Database kapcsolat:**
   - Database URL helyes?
   - init_db() meghívása OK?

### 📤 Kimenet formátum

```markdown
# AUDIT 3: service_inventory - HIBÁK

## 1. Import hibák
- [ ] `fájl:sor` - Leírás

## 2. Recipe model ForeignKey hibák
- [ ] `fájl:sor` - Leírás

## 3. OCR Service Lazy Init hibák
- [ ] `fájl:sor` - Leírás

## 4. Port konfiguráció hibák
- [ ] `fájl:sor` - Leírás

## 5. Router regisztráció hibák
- [ ] `fájl:sor` - Leírás

## 6. Database kapcsolat hibák
- [ ] `fájl:sor` - Leírás

## 7. Egyéb hibák
- [ ] `fájl:sor` - Leírás

---

**Összesen:** X db hiba
**Kritikus:** Y db
**Közepes:** Z db
```

---

## AUDIT 4️⃣: service_admin (Modul 6-8)

### 🎯 Cél
A `service_admin` mikroszolgáltatás átvizsgálása, különös tekintettel a Router regisztrációra és JWT kezelésre.

### 📁 Ellenőrizendő fájlok

**Főbb fájlok:**
- `backend/service_admin/main.py` ⚠️ **ROUTER REGISZTRÁCIÓ!**
- `backend/service_admin/Dockerfile`
- `backend/service_admin/config.py` ⚠️ **JWT!**
- `backend/service_admin/dependencies.py`
- `backend/service_admin/seed_rbac.py`
- `backend/service_admin/requirements.txt`

**Models könyvtár:**
- `backend/service_admin/models/__init__.py`
- `backend/service_admin/models/database.py`
- `backend/service_admin/models/employee.py`
- `backend/service_admin/models/role.py`
- `backend/service_admin/models/permission.py`
- `backend/service_admin/models/audit_log.py`

**Services könyvtár:**
- `backend/service_admin/services/__init__.py`
- `backend/service_admin/services/auth_service.py`
- `backend/service_admin/services/employee_service.py`
- `backend/service_admin/services/role_service.py`
- `backend/service_admin/services/permission_service.py`
- `backend/service_admin/services/ntak_service.py`
- `backend/service_admin/services/audit_log_service.py`

**Routers könyvtár:**
- `backend/service_admin/routers/__init__.py`
- `backend/service_admin/routers/auth.py`
- `backend/service_admin/routers/employees.py`
- `backend/service_admin/routers/roles.py`
- `backend/service_admin/routers/permissions.py`
- `backend/service_admin/routers/internal.py`

### 🔎 Keresendő hibák

1. **Import hibák:**
   - Model, service, router importok
   - JWT library importok (python-jose, passlib)

2. **Router regisztráció hibák:**
   - `main.py` - Minden router (auth, employees, roles, permissions, internal) regisztrálva van?
   - Prefix-ek helyesek? (pl. `/auth`, `/employees`, `/roles`)

3. **JWT konfiguráció:**
   - `config.py` - JWT_SECRET_KEY beállítva?
   - JWT_ALGORITHM helyes (HS256)?
   - ACCESS_TOKEN_EXPIRE_MINUTES beállítva?

4. **Auth Service hibák:**
   - `services/auth_service.py` - Password hashing helyes (bcrypt)?
   - Token generálás működik?
   - Token validáció működik?

5. **Dependencies hibák:**
   - `dependencies.py` - get_current_user dependency helyes?
   - Token extraction működik?
   - Permission check logika OK?

6. **RBAC seed hibák:**
   - `seed_rbac.py` - Inicializáló adatok helyesek?
   - Role és Permission kapcsolatok OK?

7. **Port konfiguráció:**
   - PORT = 8002?
   - EXPOSE 8002 a Dockerfile-ban?

### 📤 Kimenet formátum

```markdown
# AUDIT 4: service_admin - HIBÁK

## 1. Import hibák
- [ ] `fájl:sor` - Leírás

## 2. Router regisztráció hibák
- [ ] `fájl:sor` - Leírás

## 3. JWT konfiguráció hibák
- [ ] `fájl:sor` - Leírás

## 4. Auth Service hibák
- [ ] `fájl:sor` - Leírás

## 5. Dependencies hibák
- [ ] `fájl:sor` - Leírás

## 6. RBAC seed hibák
- [ ] `fájl:sor` - Leírás

## 7. Port konfiguráció hibák
- [ ] `fájl:sor` - Leírás

## 8. Egyéb hibák
- [ ] `fájl:sor` - Leírás

---

**Összesen:** X db hiba
**Kritikus:** Y db
**Közepes:** Z db
```

---

## AUDIT 5️⃣: Frontend Alapok (Auth/Proxy)

### 🎯 Cél
A frontend alap konfigurációjának átvizsgálása: Vite proxy, Axios interceptor és Zustand auth store.

### 📁 Ellenőrizendő fájlok

**Konfigurációs fájlok:**
- `frontend/vite.config.ts` ⚠️ **MIND A 4 PORT PROXYJA!**
- `frontend/package.json`
- `frontend/tsconfig.json`

**Core Services:**
- `frontend/src/services/api.ts` ⚠️ **AXIOS INTERCEPTOR!**

**Stores:**
- `frontend/src/stores/authStore.ts` ⚠️ **ZUSTAND!**

### 🔎 Keresendő hibák

1. **Vite Proxy konfiguráció:**
   - `vite.config.ts` - Mind a 4 mikroszolgáltatás proxyja beállítva?
     - `/api/menu` -> `http://localhost:8000`
     - `/api/orders` -> `http://localhost:8001`
     - `/api/admin` -> `http://localhost:8002`
     - `/api/inventory` -> `http://localhost:8003`
   - `rewrite` szabályok helyesek?
   - `changeOrigin: true` be van állítva?

2. **Axios Interceptor hibák:**
   - `api.ts` - Request interceptor hozzáadja a JWT tokent?
   - Authorization header formátuma: `Bearer ${token}`?
   - Response interceptor kezeli a 401 hibát?
   - 401 hiba esetén átirányítás `/login`-ra?

3. **Zustand Auth Store hibák:**
   - `authStore.ts` - State struktura helyes?
   - `user`, `token`, `isAuthenticated` mezők vannak?
   - `login`, `logout`, `setUser` akciók definiálva?
   - LocalStorage persist működik?

4. **TypeScript típusok:**
   - User interface definiálva?
   - API response típusok helyesek?

5. **Package.json dependencies:**
   - axios telepítve?
   - zustand telepítve?
   - react-router-dom telepítve?

### 📤 Kimenet formátum

```markdown
# AUDIT 5: Frontend Alapok - HIBÁK

## 1. Vite Proxy konfiguráció hibák
- [ ] `fájl:sor` - Leírás

## 2. Axios Interceptor hibák
- [ ] `fájl:sor` - Leírás

## 3. Zustand Auth Store hibák
- [ ] `fájl:sor` - Leírás

## 4. TypeScript típus hibák
- [ ] `fájl:sor` - Leírás

## 5. Package.json dependency hibák
- [ ] `fájl:sor` - Leírás

## 6. Egyéb hibák
- [ ] `fájl:sor` - Leírás

---

**Összesen:** X db hiba
**Kritikus:** Y db
**Közepes:** Z db
```

---

## AUDIT 6️⃣: Frontend Auth Logika

### 🎯 Cél
A frontend bejelentkezési és routing logikájának átvizsgálása.

### 📁 Ellenőrizendő fájlok

**Services:**
- `frontend/src/services/authService.ts` ⚠️ **HELYES HÍVÁS: /api/auth/login?**

**Pages:**
- `frontend/src/pages/LoginPage.tsx` ⚠️ **HELYES ÁTIRÁNYÍTÁS: /tables?**

**App:**
- `frontend/src/App.tsx` ⚠️ **ROUTING SORREND!**

**Types:**
- `frontend/src/types/` (User, Auth stb.)

### 🔎 Keresendő hibák

1. **AuthService API hívások:**
   - `authService.ts` - Login endpoint helyes: `POST /api/admin/auth/login`?
   - Logout endpoint: `POST /api/admin/auth/logout`?
   - Get current user: `GET /api/admin/auth/me`?
   - Token küldése a header-ben?

2. **LoginPage hibák:**
   - `LoginPage.tsx` - Sikeres login után átirányítás `/tables`-ra?
   - Form validáció működik?
   - Error handling helyes?
   - authStore.login() meghívása OK?

3. **App.tsx routing hibák:**
   - Protected route wrapper van?
   - Route sorrend helyes (specifikus előbb, mint általános)?
   - `/login` route nem védett?
   - Többi route védett (requireAuth)?
   - Default redirect `/tables`-ra vagy `/login`-ra?

4. **Auth state management:**
   - useAuthStore hook használata helyes?
   - Token persistence localStorage-ban?
   - Auto-logout 401 esetén?

5. **TypeScript típusok:**
   - LoginRequest, LoginResponse típusok definiálva?
   - User interface konzisztens?

### 📤 Kimenet formátum

```markdown
# AUDIT 6: Frontend Auth Logika - HIBÁK

## 1. AuthService API hívás hibák
- [ ] `fájl:sor` - Leírás

## 2. LoginPage hibák
- [ ] `fájl:sor` - Leírás

## 3. App.tsx routing hibák
- [ ] `fájl:sor` - Leírás

## 4. Auth state management hibák
- [ ] `fájl:sor` - Leírás

## 5. TypeScript típus hibák
- [ ] `fájl:sor` - Leírás

## 6. Egyéb hibák
- [ ] `fájl:sor` - Leírás

---

**Összesen:** X db hiba
**Kritikus:** Y db
**Közepes:** Z db
```

---

## AUDIT 7️⃣: Frontend Funkcionális Modulok (Tables/KDS)

### 🎯 Cél
A frontend Tables és KDS szolgáltatásainak átvizsgálása, különös tekintettel az API hívásokra.

### 📁 Ellenőrizendő fájlok

**Services:**
- `frontend/src/services/tableService.ts` ⚠️ **HELYES HÍVÁS: /api/orders/tables?**
- `frontend/src/services/kdsService.ts` ⚠️ **HELYES HÍVÁS: /api/orders/kds/...?**
- `frontend/src/services/menuService.ts`
- `frontend/src/services/paymentService.ts`

**Pages:**
- `frontend/src/pages/TableMapPage.tsx`
- `frontend/src/pages/KdsPage.tsx`
- `frontend/src/pages/PaymentPage.tsx`

**Components:**
- `frontend/src/components/table-map/`
- `frontend/src/components/kds/`
- `frontend/src/components/payment/`

### 🔎 Keresendő hibák

1. **TableService API hívások:**
   - `tableService.ts` - GET `/api/orders/tables` helyes?
   - POST `/api/orders/tables` helyes?
   - PUT `/api/orders/tables/:id` helyes?
   - GET `/api/orders/tables/:id/seats` helyes?

2. **KdsService API hívások:**
   - `kdsService.ts` - GET `/api/orders/kds/pending` helyes?
   - GET `/api/orders/kds/ready` helyes?
   - PUT `/api/orders/kds/:id/status` helyes?
   - WebSocket kapcsolat van-e (opcionális)?

3. **MenuService API hívások:**
   - `menuService.ts` - GET `/api/menu/products` helyes?
   - GET `/api/menu/categories` helyes?
   - POST `/api/menu/products` helyes?

4. **PaymentService API hívások:**
   - `paymentService.ts` - POST `/api/orders/payments` helyes?
   - Split-check támogatás van?
   - Seat szerinti fizetés működik?

5. **Component-Service integráció:**
   - TableMapPage használja a tableService-t?
   - KdsPage használja a kdsService-t?
   - Error handling minden service hívásban?

6. **TypeScript típusok:**
   - Table, Seat, Order, OrderItem típusok konzisztensek?
   - API response típusok helyesek?

### 📤 Kimenet formátum

```markdown
# AUDIT 7: Frontend Funkcionális Modulok - HIBÁK

## 1. TableService API hívás hibák
- [ ] `fájl:sor` - Leírás

## 2. KdsService API hívás hibák
- [ ] `fájl:sor` - Leírás

## 3. MenuService API hívás hibák
- [ ] `fájl:sor` - Leírás

## 4. PaymentService API hívás hibák
- [ ] `fájl:sor` - Leírás

## 5. Component-Service integráció hibák
- [ ] `fájl:sor` - Leírás

## 6. TypeScript típus hibák
- [ ] `fájl:sor` - Leírás

## 7. Egyéb hibák
- [ ] `fájl:sor` - Leírás

---

**Összesen:** X db hiba
**Kritikus:** Y db
**Közepes:** Z db
```

---

## AUDIT 8️⃣: Frontend Admin UI

### 🎯 Cél
A frontend Admin Dashboard átvizsgálása, különös tekintettel a sidebar linkekre és az admin API hívásokra.

### 📁 Ellenőrizendő fájlok

**Pages:**
- `frontend/src/pages/AdminPage.tsx` ⚠️ **SIDEBAR LINKEK!**

**Admin Components:**
- `frontend/src/components/admin/TableList.tsx`
- `frontend/src/components/admin/TableEditor.tsx`
- `frontend/src/components/admin/ProductList.tsx`
- `frontend/src/components/admin/ProductEditor.tsx`
- `frontend/src/components/admin/EmployeeList.tsx`
- `frontend/src/components/admin/EmployeeEditor.tsx`
- `frontend/src/components/admin/RoleList.tsx`
- `frontend/src/components/admin/RoleEditor.tsx`

**Services:**
- `frontend/src/services/employeeService.ts` ⚠️ **HELYES HÍVÁS: /api/admin/employees?**
- `frontend/src/services/roleService.ts` ⚠️ **HELYES HÍVÁS: /api/admin/roles?**

### 🔎 Keresendő hibák

1. **AdminPage Sidebar hibák:**
   - `AdminPage.tsx` - Sidebar navigation linkek helyesek?
   - Tab switching működik (Tables, Products, Employees, Roles)?
   - Active tab highlighting OK?
   - Permission-based menu filtering van?

2. **EmployeeService API hívások:**
   - `employeeService.ts` - GET `/api/admin/employees` helyes?
   - POST `/api/admin/employees` helyes?
   - PUT `/api/admin/employees/:id` helyes?
   - DELETE `/api/admin/employees/:id` helyes?

3. **RoleService API hívások:**
   - `roleService.ts` - GET `/api/admin/roles` helyes?
   - POST `/api/admin/roles` helyes?
   - PUT `/api/admin/roles/:id` helyes?
   - DELETE `/api/admin/roles/:id` helyes?
   - GET `/api/admin/permissions` helyes?

4. **Admin Component hibák:**
   - EmployeeList, EmployeeEditor - employeeService használata helyes?
   - RoleList, RoleEditor - roleService használata helyes?
   - TableList, TableEditor - tableService használata helyes (/api/orders/tables)?
   - ProductList, ProductEditor - menuService használata helyes (/api/menu/products)?

5. **Form validáció:**
   - Employee form validáció működik?
   - Role form validáció működik?
   - Error handling minden form-ban?

6. **TypeScript típusok:**
   - Employee, Role, Permission típusok konzisztensek?
   - CreateEmployeeRequest, UpdateRoleRequest típusok helyesek?

### 📤 Kimenet formátum

```markdown
# AUDIT 8: Frontend Admin UI - HIBÁK

## 1. AdminPage Sidebar hibák
- [ ] `fájl:sor` - Leírás

## 2. EmployeeService API hívás hibák
- [ ] `fájl:sor` - Leírás

## 3. RoleService API hívás hibák
- [ ] `fájl:sor` - Leírás

## 4. Admin Component hibák
- [ ] `fájl:sor` - Leírás

## 5. Form validáció hibák
- [ ] `fájl:sor` - Leírás

## 6. TypeScript típus hibák
- [ ] `fájl:sor` - Leírás

## 7. Egyéb hibák
- [ ] `fájl:sor` - Leírás

---

**Összesen:** X db hiba
**Kritikus:** Y db
**Közepes:** Z db
```

---

## 📊 Összesítő sablon (Karmester használja)

Az összes audit lefutása után a Karmester készíti el:

```markdown
# HIBAKERESŐ AUDIT SPRINT - ÖSSZESÍTŐ

**Audit időpont:** YYYY-MM-DD
**Auditált commit:** cb3d2eb
**Végrehajtó ágensek száma:** 8

## Hibák Modul szerint

| Modul | Kritikus | Közepes | Összesen |
|-------|----------|---------|----------|
| service_menu | X | Y | Z |
| service_orders | X | Y | Z |
| service_inventory | X | Y | Z |
| service_admin | X | Y | Z |
| Frontend Alapok | X | Y | Z |
| Frontend Auth | X | Y | Z |
| Frontend Funkcionális | X | Y | Z |
| Frontend Admin | X | Y | Z |
| **ÖSSZESEN** | **XX** | **YY** | **ZZ** |

## Következő lépések

1. Priorizálás (Kritikus hibák először)
2. Javító Sprint indítása
3. Regressziós tesztek írása
```

---

## ✅ Végrehajtási jegyzet

**Minden végrehajtó ágensnek:**
1. Olvasd be a fenti audit parancsot
2. Vizsgáld meg a megadott fájlokat
3. Listázd a talált hibákat a megadott formátumban
4. **NE JAVÍTSD** a hibákat, csak dokumentáld őket
5. Add vissza a strukturált Markdown kimenet

**Karmester feladatai:**
1. Indítsd el mind a 8 auditor ágenst párhuzamosan (8 külön ablakban)
2. Gyűjtsd össze az eredményeket
3. Készítsd el az összesítőt
4. Priorizáld a hibákat
5. Indítsd el a Javító Sprintet

---

**Dokumentum vége. Minden parancs készen áll a másolásra és végrehajtásra.**
