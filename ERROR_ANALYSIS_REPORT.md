# HIBAELEMZÉSI JELENTÉS - Parancsnoki Híd részére

**Dátum**: 2025-11-19
**Elemző**: Claude Technikus
**Állapot**: KRITIKUS - Több API végpont meghibásodott

---

## 1. KRITIKUS BLOKKEREK

**Állapot**: ✅ Nincs teljes leállás
- Backend szerver fut és válaszol
- Frontend alkalmazás betöltődött
- Nincs crash loop vagy container restart

---

## 2. API HÍVÁSI HIBÁK

### 2.1 HTTP 422 - Unprocessable Entity (Validációs Hiba)

**Érintett végpont**: `GET /api/orders/tables`

| Frontend Komponens | Backend Végpont | HTTP Kód | Fájl Hivatkozás |
|-------------------|-----------------|----------|-----------------|
| `TableMap` | `GET /api/orders/tables?page=1&page_size=100` | 422 | `src/services/tableService.ts:29` |
| `TableList` | `GET /api/orders/tables?page=1&page_size=100` | 422 | `src/services/tableService.ts:29` |

**Diagnózis**: A backend validációs hibát dob. Valószínű okok:
- Pydantic modell validációs hiba
- Hibás query paraméterek (`page`, `page_size` típushibák)
- Backend oldali enum vagy típus eltérés

**Javasolt vizsgálat**:
- Backend: `app/api/v1/endpoints/tables.py` vagy hasonló
- Backend: `app/models/table.py` Pydantic modellek
- Backend log részletek a 422 hibához

---

### 2.2 HTTP 500 - Internal Server Error

**Érintett végpontok**: `GET /api/products`, `GET /api/categories`

| Frontend Komponens | Backend Végpont | HTTP Kód | Fájl Hivatkozás |
|-------------------|-----------------|----------|-----------------|
| `ProductList` | `GET /api/products?page=1&page_size=20&is_active=true` | 500 | `src/services/menuService.ts:44` |
| `ProductList` | `GET /api/categories?page=1&page_size=100` | 500 | `src/services/menuService.ts:115` |

**Diagnózis**: Belső szerver hiba. Valószínű okok:
- Adatbázis kapcsolati hiba
- Session/DB binding probléma ("Session is not bound" típusú hiba)
- Null pointer/AttributeError a backend kódban
- Nem létező rekordokra való hivatkozás

**Javasolt vizsgálat**:
- Backend: `app/api/v1/endpoints/products.py`
- Backend: `app/api/v1/endpoints/categories.py`
- Backend: SQLAlchemy session kezelés
- Backend konzol log elemzése a stack trace-hez

---

### 2.3 HTTP 405 - Method Not Allowed

**Érintett végpont**: `POST /api/orders/tables`

| Frontend Komponens | Backend Végpont | HTTP Kód | Fájl Hivatkozás |
|-------------------|-----------------|----------|-----------------|
| `TableEditor` | `POST /api/orders/tables` | 405 | `src/services/tableService.ts:67` |

**Diagnózis**: A backend nem támogatja a POST metódust ezen az URL-en. Lehetséges okok:
- Rossz API útvonal a frontenden
- Backend router nem definiálja a POST endpointot
- URL eltérés: lehet, hogy `/api/tables` helyett `/api/orders/tables`-t használ

**Javasolt vizsgálat**:
- Frontend: `src/services/tableService.ts:67` - ellenőrizd az URL-t
- Backend: Router konfiguráció (`/api/orders/tables` vs `/api/tables`)
- Backend: `app/api/v1/api.py` routing setup

---

## 3. AUTH/JOGOSULTSÁG HIBÁK

**Állapot**: ✅ Nincs jogosultsági hiba
- Nincs 401 Unauthorized
- Nincs 403 Forbidden
- Nincs token lejárati hiba
- Nincs RBAC permission error a logokban

---

## 4. MINTA AZONOSÍTÁS - Rendszer Szintű Problémák

### 🔴 KRITIKUS MINTA #1: 422 Validációs Hiba Loop

**Ismétlődő hiba**: `GET /api/orders/tables` → 422 (többször ismétlődik)

**Jellemzők**:
- Minden oldalfrissítéskor 2-4x ismétlődik (React StrictMode double render)
- Konzisztens query paraméterek: `page=1&page_size=100`
- Minden komponens ugyanazt a hibát kapja

**Valószínű root cause**:
- Backend Pydantic validációs séma változott, de frontend nem frissült
- Típushibás query paraméter (pl. string helyett int)

---

### 🔴 KRITIKUS MINTA #2: 500 Backend Crash

**Ismétlődő hiba**:
- `GET /api/products` → 500
- `GET /api/categories` → 500

**Jellemzők**:
- Minden product/category fetch sikertelen
- Szinkron megjelenés (ugyanakkor történik)
- Valószínűleg közös backend dependency hiba

**Valószínű root cause**:
- Database session binding hiba
- SQLAlchemy session lifecycle probléma
- Middleware hiba a backend oldalon

---

### 🟡 KÖZEPES MINTA #3: 405 Method Mismatch

**Ismétlődő hiba**: `POST /api/orders/tables` → 405

**Jellemzők**:
- Csak új asztal létrehozásakor jelentkezik
- Konzisztens hiba minden POST kísérletnél

**Valószínű root cause**:
- API route mismatch frontend és backend között
- Backend nem implementálta a POST endpointot erre az URL-re

---

## 5. JAVÍTÁSI PRIORITÁS

### ⚡ AZONNAL (P0 - Blokkoló)

1. **Backend 500 hibák (Products & Categories)**
   - Fájl: Backend products/categories endpoint
   - Oka: Database/session hiba
   - Hatás: Teljes menü kezelés működésképtelen

2. **Backend 422 hiba (Tables GET)**
   - Fájl: Backend tables endpoint + Pydantic model
   - Oka: Validációs séma eltérés
   - Hatás: Asztalkezelés lista/térkép nézet nem működik

### 🔧 MAGAS (P1)

3. **Backend 405 hiba (Tables POST)**
   - Fájl: `tableService.ts:67` + Backend router
   - Oka: URL vagy method mismatch
   - Hatás: Új asztal létrehozás lehetetlen

---

## 6. AZONNALI KÖVETKEZŐ LÉPÉSEK (Parancsnok számára)

```bash
# 1. Backend konzol log lekérése
docker logs <backend-container> --tail 200

# 2. Backend HTTP 500 részletek keresése
grep "500" <backend-log-file>
grep "Traceback" <backend-log-file>

# 3. Database kapcsolat ellenőrzése
# Ellenőrizd, hogy a DB elérhető-e és a session kezelés helyes-e

# 4. API végpontok listázása
# Ellenőrizd a backend router konfigurációt
```

**Javasolt javítási sorrend**:
1. Backend 500 hibák (products/categories) - KRITIKUS
2. Backend 422 hiba (tables GET) - KRITIKUS
3. Backend 405 hiba (tables POST) - MAGAS

---

**Jelentés vége**
