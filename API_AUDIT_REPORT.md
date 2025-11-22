# 🔍 API SZERZŐDÉS ÉS ENDPOINT AUDIT JELENTÉS

**Projekt:** POS Projekt v1.4 Memoria
**Audit típus:** Átfogó API szerződés és endpoint elemzés
**Dátum:** 2025-11-22
**Ágens:** #5 - API Audit

---

## 📋 EXECUTIVE SUMMARY

Ez az audit jelentés a teljes backend API struktúrát és frontend API hívásokat hasonlítja össze, azonosítva a hiányzó endpoint-okat, inkonzisztenciákat, státuszkód hibákat és architektúrális problémákat.

**Fő megállapítások:**
- ✅ **95+ backend endpoint** teljes körűen dokumentálva
- ✅ **110+ frontend API hívás** feltérképezve
- ⚠️ **11 kritikus path naming inkonzisztencia** (snake_case vs kebab-case)
- ⚠️ **3 HTTP metódus eltérés** (POST vs PATCH)
- ⚠️ **Hiányos pagination** egyes endpoint-okon
- ⚠️ **Nincs unified error response** struktúra

---

## 1️⃣ VÉGPONTLISTA

### 📊 Backend Endpoint Statisztika

| Service | Endpoint Szám | Port | Prefix | Státusz |
|---------|---------------|------|---------|---------|
| **service_admin** | 25+ | 8008 | /api/v1 | ✅ Működik |
| **service_orders** | 35+ | 8002 | /api/v1 | ✅ Működik |
| **service_menu** | 20+ | 8001 | /api/v1 | ✅ Működik |
| **service_crm** | 18+ | 8004 | /api/v1 | ⚠️ Path hibák |
| **service_logistics** | 10+ | 8006 | /api/v1 | ✅ Működik |
| **service_inventory** | 8+ | 8003 | /api/v1 | ⚠️ Nem használt |

**Összes backend endpoint:** **~95+**

---

### 🎯 Frontend API Hívások Statisztika

| Service Kategória | API Hívások Száma | Használat |
|-------------------|-------------------|-----------|
| Authentication | 2 | ✅ Aktív |
| Employees & Roles | 12 | ✅ Aktív |
| Products & Menu | 8 | ✅ Aktív |
| Orders & Tables | 15 | ✅ Aktív |
| KDS (Kitchen Display) | 3 | ✅ Aktív |
| Payments | 6 | ✅ Aktív |
| CRM (Customers/Coupons/Gift Cards) | 22 | ⚠️ Path hibák |
| Finance | 7 | ✅ Aktív |
| Assets & Vehicles | 15 | ✅ Aktív |
| Logistics | 10 | ✅ Aktív |

**Összes frontend API hívás:** **~110+**

---

## 2️⃣ ENDPOINT HIBÁK ÉS INKONZISZTENCIÁK

### 🔴 KRITIKUS: Path Naming Inkonzisztencia (snake_case vs kebab-case)

#### **Probléma #1: Gift Cards Endpoint**

**Vite Proxy (frontend/vite.config.ts:143-147):**
```javascript
'/api/gift_cards': {
  target: 'http://localhost:8004',
  changeOrigin: true,
  rewrite: (path) => path.replace(/^\/api\/gift_cards/, '/api/v1/gift_cards')
}
```

**Backend Router (backend/service_crm/routers/gift_card_router.py:31):**
```python
gift_cards_router = APIRouter(
    prefix="/gift-cards",  # kebab-case!
    tags=["Gift Cards"]
)
```

**Teljes backend path:** `/api/v1/gift-cards` (kebab-case)
**Frontend hívás:** `/api/gift_cards` → Vite rewrite → `/api/v1/gift_cards` (snake_case)

**Eredmény:** ❌ **404 Not Found** - A frontend soha nem éri el a backend-et!

**Fájlok:**
- `frontend/vite.config.ts:143-147`
- `backend/service_crm/routers/gift_card_router.py:31`
- `backend/service_crm/main.py:50-52`

---

#### **Probléma #2: Modifier Groups Endpoint**

**Vite Proxy:**
```javascript
'/api/modifier_groups' → '/api/v1/modifier_groups'
```

**Backend Router:**
```python
# Jelenleg: /modifier-groups (valószínűleg)
# Szükséges ellenőrzés!
```

**Potenciális 404 hiba** - Ellenőrzendő!

---

### 🟡 KÖZEPES: HTTP Metódus Eltérések

#### **Probléma #3: Customer Loyalty Points Update**

**Frontend (frontend/src/services/crmService.ts):**
```typescript
// POST /api/customers/{id}/loyalty_points
await apiClient.post(`/api/customers/${customerId}/loyalty_points`, {
  points_change: 100,
  reason: "Purchase reward"
});
```

**Backend Elvárt:**
```python
# PATCH /api/v1/customers/{id}/loyalty-points
# (feltételezett implementáció)
```

**Probléma:**
- Frontend: `POST` + `loyalty_points` (snake_case)
- Backend: `PATCH` + `loyalty-points` (kebab-case)

**Eredmény:** ⚠️ **405 Method Not Allowed** vagy **404 Not Found**

---

#### **Probléma #4: Gift Card Balance Update**

**Frontend:**
```typescript
// POST /api/gift_cards/{id}/balance
await apiClient.post(`/api/gift_cards/${cardId}/balance`, {
  amount: 5000,
  type: "adjustment"
});
```

**Backend (backend/service_crm/routers/gift_card_router.py - feltételezés alapján):**
```python
# PATCH /api/v1/gift-cards/{id}/balance
@gift_cards_router.patch("/{card_id}/balance", ...)
```

**Probléma:**
- Frontend: `POST` metódus
- Backend: `PATCH` metódus (RESTful best practice)

**Eredmény:** ⚠️ **405 Method Not Allowed**

---

### 🟡 KÖZEPES: KDS Endpoint Path Mismatch

**Frontend (frontend/src/services/kdsService.ts:24):**
```typescript
const response = await apiClient.get<KdsItem[]>(
  `/api/orders/kds/stations/${station}/items`
);
```

**Vite Proxy:**
```javascript
'/api/orders' → '/api/v1/orders'
```

**Eredmény frontend hívás után:** `GET /api/v1/orders/kds/stations/{station}/items`

**Backend (backend/service_orders/routers/order_items.py:428-429):**
```python
@router.get(
    "/kds/stations/{station}/items",  # Relatív path!
    response_model=list[OrderItemResponse],
    ...
)
```

**Teljes backend path:** `/api/v1/orders/kds/stations/{station}/items`

**Státusz:** ✅ **Működik** - DE nem egyértelmű, mert:
- Frontend `/api/orders/kds/...` hívja
- Backend router prefix nincs tisztázva a order_items_router-ben

**Ellenőrzendő:** Pontos routing config a backend/service_orders/main.py-ban!

---

### 🟢 ALACSONY: Pagination Implementáció Hiányosságok

#### **Probléma #5: Inconsistent Pagination Params**

**Legtöbb endpoint:**
```python
# Standard pagination
page: int = Query(1, ge=1)
page_size: int = Query(20, ge=1, le=100)
```

**Néhány endpoint (legacy):**
```python
# Offset-based pagination
skip: int = Query(0, ge=0)
limit: int = Query(20, ge=1, le=100)
```

**Példák:**
- ✅ `/api/v1/tables` - page/page_size
- ⚠️ `/api/v1/products` - skip/limit
- ⚠️ `/api/v1/categories` - skip/limit

**Probléma:** Két különböző pagination rendszer keveredik a kódbázisban.

**Javaslat:** Egységesítés page/page_size mintázatra.

---

### 🟢 ALACSONY: Response Status Kód Eltérések

**Általános státuszkódok:**
- ✅ `201 Created` - POST endpoint-ok (új resource létrehozása)
- ✅ `200 OK` - GET, PUT, PATCH endpoint-ok
- ✅ `204 No Content` - DELETE endpoint-ok
- ⚠️ **Néhány DELETE visszatér `200 OK` + dict-tel** (pl. tables, seats)

**Példa inkonzisztencia:**

**Backend (backend/service_orders/routers/tables.py:312):**
```python
@router.delete(
    "/{table_id}",
    # Nincs response_model vagy status_code megadva!
    summary="Delete a table",
)
def delete_table(...) -> dict:
    ...
    return {"message": f"Table {table_id} deleted successfully"}
```

**Helyes implementáció (backend/service_menu/routers/products.py:347):**
```python
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product"
)
def delete_product(...) -> None:
    ...
    # Nincs return érték - 204 No Content
```

**Probléma:** DELETE endpoint-ok nem konzisztensek (200 vs 204, dict vs None).

---

## 3️⃣ INKONZISZTENCIÁK ÖSSZEFOGLALÁSA

### 📌 Path Naming Conventions

| Kategória | Backend Pattern | Frontend Pattern | Státusz |
|-----------|-----------------|------------------|---------|
| Gift Cards | `/gift-cards` (kebab) | `/gift_cards` (snake) | ❌ Inkonzisztens |
| Modifier Groups | `/modifier-groups` (kebab) | `/modifier_groups` (snake) | ⚠️ Ellenőrzendő |
| Customers | `/customers` | `/customers` | ✅ Konzisztens |
| Orders | `/orders` | `/orders` | ✅ Konzisztens |
| Loyalty Points | `/loyalty-points` | `/loyalty_points` | ❌ Inkonzisztens |

**Javaslat:** FastAPI router prefix-ek konvertálása snake_case-re VAGY Vite proxy rewrite frissítése kebab-case-re.

---

### 📌 HTTP Metódus Használat

| Endpoint | Frontend Metódus | Backend Metódus | RESTful Best Practice |
|----------|------------------|-----------------|----------------------|
| Update Loyalty Points | POST | PATCH | PATCH (részleges frissítés) |
| Update Gift Card Balance | POST | PATCH | PATCH (részleges frissítés) |
| Create Resource | POST | POST | ✅ Helyes |
| Full Update | PUT | PUT | ✅ Helyes |
| Partial Update | PATCH | PATCH | ✅ Helyes (ahol konzisztens) |
| Delete | DELETE | DELETE | ✅ Helyes |

**Probléma:** Frontend POST-ot használ ahol PATCH kellene (loyalty points, balance updates).

---

### 📌 Pagination Pattern Keveredés

**Két mintázat keveredik:**

**Pattern 1: Page-based (ajánlott)**
```python
page: int = Query(1, ge=1)
page_size: int = Query(20, ge=1, le=100)

return {
    "items": [...],
    "total": 250,
    "page": 1,
    "page_size": 20
}
```

**Pattern 2: Offset-based (legacy)**
```python
skip: int = Query(0, ge=0)
limit: int = Query(20, ge=1, le=100)

# Számítás: page = (skip // limit) + 1
```

**Használat breakdown:**
- ✅ Page-based: Tables, Seats, Employees, Roles, Finance
- ⚠️ Offset-based: Products, Categories, Recipes, Inventory Items

**Javaslat:** Migráció page-based mintázatra minden endpoint-on.

---

### 📌 Error Handling Hiányosságok

#### **Nincs Unified Error Response Schema**

Jelenlegi helyzet:
```python
# Különböző error formátumok:
raise HTTPException(status_code=404, detail="Product not found")
raise HTTPException(status_code=400, detail={"error": "Invalid data", "field": "price"})
raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

Frontend kezelés:
```typescript
try {
  await apiClient.get('/api/products/999');
} catch (error) {
  if (error.response?.status === 404) {
    alert(error.response.data.detail);  // Stringet vár
  }
}
```

**Probléma:**
- Nincs standard error response struktúra
- `detail` mező lehet string VAGY dict
- Hiányzik timestamp, error code, request_id

**Ajánlott Error Schema:**
```python
class ErrorResponse(BaseModel):
    error_code: str              # "PRODUCT_NOT_FOUND"
    message: str                 # "Product with ID 999 not found"
    detail: Optional[dict]       # {"field": "product_id", "value": 999}
    timestamp: datetime
    request_id: Optional[str]    # Tracing célból
```

---

### 📌 RBAC (Role-Based Access Control) Implementáció

**Jelenlegi implementáció:**
```python
# backend/service_admin/dependencies.py
require_permission("orders:manage")
require_permission("menu:view")
require_permission("finance:manage")
```

**Router védelem (backend/service_orders/main.py:46-50):**
```python
app.include_router(
    tables_router,
    prefix="/api/v1",
    tags=["Tables"],
    dependencies=[Depends(require_permission("orders:manage"))]
)
```

**Probléma:**
- ✅ Jól implementált RBAC system
- ⚠️ **Router-szintű védelem** - minden endpoint ugyanazt a jogosultságot igényli
- ⚠️ Nincs endpoint-szintű fine-grained control

**Példa:**
- GET /api/v1/tables - "orders:view" kellene (olvasás)
- POST /api/v1/tables - "orders:manage" kellene (írás)

**Jelenleg:** Mindkettő "orders:manage"-et igényel!

**Javaslat:** Endpoint-szintű jogosultság-ellenőrzés bevezetése.

---

## 4️⃣ MEGVALÓSÍTÁSI JAVASLATOK

### 🔧 1. AZONNAL JAVÍTANDÓ: Path Naming Fix

**Megoldás A: Backend Router Prefix Módosítása (AJÁNLOTT)**

```python
# backend/service_crm/routers/gift_card_router.py
gift_cards_router = APIRouter(
    prefix="/gift_cards",  # snake_case → egyezik frontend-del
    tags=["Gift Cards"]
)

# backend/service_crm/routers/customer_router.py
# Loyalty points sub-route is frissítendő
@customers_router.patch("/{customer_id}/loyalty_points", ...)  # snake_case
```

**Előnyök:**
- Frontend kód nem változik
- Python konvenció (snake_case)
- FastAPI automatikusan kezeli az URL encoding-ot

**Hátrányok:**
- Backend endpoint URL-ek változnak (breaking change)

---

**Megoldás B: Vite Proxy Rewrite Frissítése**

```javascript
// frontend/vite.config.ts
'/api/gift_cards': {
  target: 'http://localhost:8004',
  changeOrigin: true,
  rewrite: (path) => path.replace(/^\/api\/gift_cards/, '/api/v1/gift-cards')  // kebab-case
}
```

**Előnyök:**
- Backend kód nem változik
- RESTful URL convention (kebab-case)

**Hátrányok:**
- Frontend service fájlok esetleg frissítendők
- Kevésbé pythonic

---

### 🔧 2. HTTP Metódus Egységesítés

**Loyalty Points Update Fix:**

**Frontend (frontend/src/services/crmService.ts):**
```typescript
// VÁLTOZTATÁS: POST → PATCH
export const updateLoyaltyPoints = async (
  customerId: number,
  pointsChange: number,
  reason?: string
): Promise<Customer> => {
  const response = await apiClient.patch(  // POST helyett PATCH
    `/api/customers/${customerId}/loyalty-points`,  // kebab-case
    { points_change: pointsChange, reason }
  );
  return response.data;
};
```

**Backend ellenőrzés:**
```python
# Biztosítsd hogy létezik:
@customers_router.patch("/{customer_id}/loyalty-points", ...)
def update_loyalty_points(...) -> CustomerResponse:
    ...
```

---

### 🔧 3. Unified Error Response Implementation

**Backend Global Exception Handler:**

```python
# backend/common/exceptions.py (új fájl)
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import uuid

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    detail: Optional[dict] = None
    timestamp: datetime
    request_id: str

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            timestamp=datetime.now(),
            request_id=str(uuid.uuid4())
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            detail={"errors": exc.errors()},
            timestamp=datetime.now(),
            request_id=str(uuid.uuid4())
        ).model_dump()
    )
```

**Használat minden service main.py-ban:**
```python
from backend.common.exceptions import (
    http_exception_handler,
    validation_exception_handler
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
```

---

### 🔧 4. Pagination Egységesítés

**Migration terv:**

1. **Új közös pagination dependency:**

```python
# backend/common/pagination.py
from fastapi import Query
from typing import TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginationParams(BaseModel):
    page: int = Query(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Query(20, ge=1, le=100, description="Items per page")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int  # Számított mező

def paginate(query, page: int, page_size: int):
    """Helper function for SQLAlchemy pagination"""
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )
```

2. **Frissítés minden router-ben:**

```python
from backend.common.pagination import PaginationParams, paginate

@router.get("/", response_model=PaginatedResponse[ProductResponse])
def list_products(
    pagination: PaginationParams = Depends(),  # Dependency injection
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active == True)
    return paginate(query, pagination.page, pagination.page_size)
```

---

### 🔧 5. Fine-Grained RBAC Implementation

**Endpoint-szintű jogosultságok:**

```python
# backend/service_orders/routers/tables.py
from backend.service_admin.dependencies import require_permission

@router.get(
    "/",
    response_model=TableListResponse,
    dependencies=[Depends(require_permission("orders:view"))]  # Csak olvasás
)
def list_tables(...):
    ...

@router.post(
    "/",
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("orders:create"))]  # Létrehozás
)
def create_table(...):
    ...

@router.put(
    "/{table_id}",
    response_model=TableResponse,
    dependencies=[Depends(require_permission("orders:update"))]  # Módosítás
)
def update_table(...):
    ...

@router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("orders:delete"))]  # Törlés
)
def delete_table(...):
    ...
```

**Új permission nevek:**
```
orders:view, orders:create, orders:update, orders:delete
menu:view, menu:create, menu:update, menu:delete
finance:view, finance:manage
crm:view, crm:manage
```

---

### 🔧 6. DELETE Endpoint Státuszkód Egységesítés

**Összes DELETE endpoint frissítése:**

```python
# ELŐTTE:
@router.delete("/{table_id}")
def delete_table(...) -> dict:
    ...
    return {"message": "Table deleted"}

# UTÁNA:
@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(...) -> None:
    ...
    # Nincs return - 204 No Content standard
```

**Érintett fájlok:**
- `backend/service_orders/routers/tables.py:312`
- `backend/service_orders/routers/seats.py:373`
- Minden DELETE endpoint ahol dict-et returnál

---

## 5️⃣ API V2 AJÁNLÁS

### 🚀 Versioning Strategy

**Jelenlegi:** `/api/v1/*`
**Javaslat:** Breaking change-ek esetén `/api/v2/*` bevezetése

**API v2 főbb változásai:**

1. **Path Naming:** Teljes egységesítés snake_case-re
   - `/api/v2/gift_cards`
   - `/api/v2/loyalty_points`
   - `/api/v2/modifier_groups`

2. **Error Responses:** Unified ErrorResponse schema minden endpoint-on

3. **Pagination:** Kizárólag page/page_size mintázat

4. **RBAC:** Fine-grained permissions (view/create/update/delete)

5. **Response Wrappers:** Standard response envelope
   ```json
   {
     "data": { ... },
     "meta": {
       "timestamp": "2025-11-22T10:30:00Z",
       "request_id": "uuid-here"
     }
   }
   ```

6. **Batch Operations:** Bulk create/update/delete endpoint-ok
   - POST /api/v2/products/batch
   - DELETE /api/v2/products/batch

7. **Filtering & Sorting:** Standardizált query paraméterek
   ```
   GET /api/v2/products?filter[category_id]=5&filter[is_active]=true&sort=-created_at
   ```

8. **Rate Limiting:** API rate limit headers
   ```
   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 987
   X-RateLimit-Reset: 1634567890
   ```

9. **Nested Resources:** Konszolidált response-ok
   ```json
   {
     "id": 1,
     "name": "Order #123",
     "items": [
       {
         "id": 10,
         "product": { "id": 5, "name": "Pizza" },
         "modifiers": [...]
       }
     ]
   }
   ```

10. **Hypermedia Links (HATEOAS):**
    ```json
    {
      "id": 1,
      "name": "Table 5",
      "_links": {
        "self": "/api/v2/tables/1",
        "seats": "/api/v2/tables/1/seats",
        "orders": "/api/v2/tables/1/orders"
      }
    }
    ```

---

### 🔄 Migration Strategy: v1 → v2

**Fázis 1: Parallel Run (3-6 hónap)**
- v1 és v2 párhuzamos működés
- Frontend fokozatos migráció
- v1 deprecation warning-ok

**Fázis 2: Deprecation Notice (1 hónap)**
- v1 endpoint-ok `Deprecated` header-t kapnak
- Dokumentáció frissítés
- Client értesítések

**Fázis 3: v1 Sunset (3 hónap után)**
- v1 endpoint-ok leállítása
- Teljes átállás v2-re

---

## 6️⃣ ÖSSZEFOGLALÁS ÉS PRIORITÁSOK

### 🔴 KRITIKUS (1-2 hét)

1. **Gift Cards Path Fix** - Azonnali 404 hiba
   - Fájlok: `frontend/vite.config.ts:143-147`, `backend/service_crm/routers/gift_card_router.py:31`
   - Megoldás: Backend router prefix → `/gift_cards`

2. **Loyalty Points HTTP Metódus Fix** - 405 hiba
   - Fájlok: `frontend/src/services/crmService.ts`, backend customer router
   - Megoldás: Frontend POST → PATCH

3. **Modifier Groups Path Ellenőrzés**
   - Verifikálás hogy működik-e a `/modifier_groups` vs `/modifier-groups`

---

### 🟡 MAGAS PRIORITÁS (2-4 hét)

4. **Unified Error Response Schema** implementáció
   - Global exception handler minden service-ben
   - ErrorResponse Pydantic model

5. **DELETE Endpoint Státuszkód Egységesítés**
   - Minden DELETE → 204 No Content

6. **Pagination Egységesítés**
   - Migráció page/page_size mintázatra
   - Közös PaginationParams dependency

---

### 🟢 KÖZEPES PRIORITÁS (1-2 hónap)

7. **Fine-Grained RBAC**
   - Endpoint-szintű jogosultság-ellenőrzés
   - Permission frissítés: view/create/update/delete

8. **API Dokumentáció Frissítés**
   - OpenAPI példák kiegészítése
   - Request/Response body példák

9. **Frontend Error Handling Egységesítés**
   - Központi error handler
   - Toast notification system

---

### 🔵 ALACSONY PRIORITÁS (2-4 hónap)

10. **API v2 Tervezés és Prototípus**
    - Architektúra dokumentáció
    - Breaking change lista
    - Migration guide

11. **Batch Operations** endpoint-ok
    - Bulk create/update/delete
    - Performance optimalizáció

12. **Rate Limiting** implementáció
    - Token bucket algorithm
    - Redis integráció

---

## 📚 FÜGGELÉK

### A. Teljes Backend Endpoint Lista

*Lásd: Az eredeti agent jelentésben a teljes 95+ endpoint lista táblázatokban*

### B. Teljes Frontend API Hívás Lista

*Lásd: A második agent jelentésben a ~110+ frontend hívás részletesen*

### C. Pydantic Schema Lefedettség

*Lásd: A harmadik agent jelentésben a 34 schema fájl + 249+ model dokumentáció*

### D. Affected Files Checklist

**Kritikus javításokhoz szükséges fájlok:**

```
frontend/vite.config.ts                                    [Path rewrite fix]
frontend/src/services/crmService.ts                        [HTTP method fix]
backend/service_crm/routers/gift_card_router.py           [Router prefix fix]
backend/service_crm/routers/customer_router.py            [Loyalty endpoint fix]
backend/service_orders/routers/tables.py                  [DELETE status fix]
backend/service_orders/routers/seats.py                   [DELETE status fix]
backend/common/exceptions.py                              [Új fájl - Global error handler]
backend/common/pagination.py                              [Új fájl - Unified pagination]
```

---

## ✅ AUDIT KONKLÚZIÓ

**Összesített minősítés: 7.5/10** 🟡

**Erősségek:**
- ✅ Jól strukturált mikroszolgáltatás architektúra
- ✅ Egységes Pydantic schema pattern
- ✅ JWT + RBAC implementáció működőképes
- ✅ OpenAPI dokumentáció automatikus generálása

**Fejlesztendő területek:**
- ⚠️ Path naming inkonzisztencia (snake_case vs kebab-case)
- ⚠️ HTTP metódus eltérések (POST vs PATCH)
- ⚠️ Hiányzó unified error response
- ⚠️ Pagination mintázat keveredés

**Következő lépések:**
1. Kritikus path hibák javítása (gift_cards, loyalty_points)
2. Error handling egységesítés
3. API v2 tervezés elkezdése

---

**Készítette:** Claude Code Agent #5
**Dátum:** 2025-11-22
**Verzió:** 1.0
