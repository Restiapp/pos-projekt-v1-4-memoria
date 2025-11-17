# Docker Deployment Hibajavítások Dokumentációja

## Verzió: 2025-11-17
## Integrátor: Claude (Az Integrátor)

---

## 1. ÖSSZEFOGLALÓ

Ez a dokumentum tartalmazza az összes változtatást ami a Docker deployment során történt, hogy a projekt dokumentálható és követhető maradjon.

---

## 2. DEPENDENCY VERSION UPDATES

### 2.1. Inventory Service - Pydantic verzió frissítés

**Fájl:** `backend/service_inventory/requirements.txt`

**Probléma:**
- A service_inventory régi Pydantic 2.5.0 verziót használt
- Ez nem támogatta a `decimal_places` constraint-et
- Hiba: `ValueError: Unknown constraint decimal_places`

**Változtatás:**
```diff
- pydantic==2.5.0
- pydantic-settings==2.1.0
+ pydantic==2.9.0
+ pydantic-settings==2.5.0
```

**Indoklás:** Egységesítés a többi service-szel (menu, orders, admin mind 2.9.0-t használ)

**Sorszám:** 12-13

---

### 2.2. Admin Service - Email Validator hiányzó dependency

**Fájl:** `backend/service_admin/requirements.txt`

**Probléma:**
- Az employee.py schema használ EmailStr típust
- A Pydantic 2.9.0 email validációhoz külön `email-validator` package kell
- Hiba: `ImportError: email-validator is not installed, run 'pip install pydantic[email]'`

**Változtatás:**
```diff
  # FastAPI Core
  fastapi==0.115.0
  uvicorn[standard]==0.32.0
  pydantic==2.9.0
  pydantic-settings==2.5.0
+ email-validator==2.1.0
```

**Indoklás:** Az EmailStr típus használatához szükséges dependency

**Sorszám:** 6

---

## 3. KÓDVÁLTOZTATÁSOK (CODE REFACTORING)

### 3.1. Inventory Service - OCR Service Lazy Initialization

**Fájl:** `backend/service_inventory/services/ocr_service.py`

**Probléma:**
- A 389. sorban a `ocr_service = OcrService()` module szinten azonnal fut
- Ez a Document AI client inicializálást triggereli module import-kor
- Hiányzó fájl: `/app/credentials/gcp-key.json`
- Hiba: `google.auth.exceptions.DefaultCredentialsError: File /app/credentials/gcp-key.json was not found`
- **Következmény:** Az egész service nem indul el, még akkor sem ha az OCR funkciót nem használják

**Választott megoldás:** Lazy Initialization Pattern

**Változtatás (389-390. sor):**
```diff
- # Create singleton instance
- ocr_service = OcrService()
+ # Lazy singleton instance - only initialized when first accessed
+ _ocr_service_instance: Optional[OcrService] = None
+
+
+ def get_ocr_service() -> OcrService:
+     """
+     Get or create the singleton OcrService instance.
+
+     This lazy initialization allows the service to start even if GCP
+     credentials are not available. The error will only occur when
+     actually trying to use OCR functionality.
+
+     Returns:
+         OcrService: The singleton OCR service instance
+
+     Raises:
+         Exception: If GCP credentials are invalid or missing when first accessed
+     """
+     global _ocr_service_instance
+     if _ocr_service_instance is None:
+         _ocr_service_instance = OcrService()
+     return _ocr_service_instance
+
+
+ # For backwards compatibility, provide ocr_service that initializes on access
+ class _OcrServiceProxy:
+     """Proxy object that lazily initializes the OCR service."""
+
+     def __getattr__(self, name):
+         return getattr(get_ocr_service(), name)
+
+
+ ocr_service = _OcrServiceProxy()
```

**Indoklás:**
- Az OCR service mostantól csak akkor inicializálódik amikor ténylegesen használják
- A service elindul GCP credentials nélkül is
- Backwards compatible: a `ocr_service` továbbra is használható ugyanúgy
- Az OCR endpoints csak akkor hibáznak amikor ténylegesen meghívják őket
- Ez lehetővé teszi a service működését development környezetben, GCP setup nélkül

**Érintett sorok:** 388-420

**Import szükséges:** Az `Optional` type már importálva volt a fájl elején (10. sor)

**Backwards Compatibility:** ✅ TELJES
- Minden korábbi `ocr_service.method()` hívás továbbra is működik
- A proxy object transparensen delegálja a hívásokat a lazy-initialized instance-nak

---

### 3.2. Admin Service - Helytelen Import Path

**Fájl:** `backend/service_admin/routers/permissions.py`

**Probléma:**
- A 12. sorban helytelen import path: `from backend.service_admin.database import get_db`
- A `database.py` fájl valójában a `models/` mappában van: `backend/service_admin/models/database.py`
- Hiba: `ModuleNotFoundError: No module named 'backend.service_admin.database'`
- **Következmény:** Az egész admin service nem indul el

**Választott megoldás:** Import path javítás

**Változtatás (12. sor):**
```diff
- from backend.service_admin.database import get_db
+ from backend.service_admin.models.database import get_db
```

**Indoklás:**
- A `database.py` modul helyes elérési útja: `backend/service_admin/models/database.py`
- Ez az architektúrával konzisztens (models mappa tartalmazza a database setup-ot)
- Azonos pattern mint az inventory service-ben

**Érintett sor:** 12

**Sorszám:** 12

---

### 3.3. Inventory Service - Hiányzó Pydantic Import

**Fájl:** `backend/service_inventory/routers/inventory_items.py`

**Probléma:**
- A 215. sorban használva van a `BaseModel` osztály egy Pydantic schema definiálásához
- A fájl tetején nincs importálva a `BaseModel` és `Field` a pydantic-ból
- Hiba: `NameError: name 'BaseModel' is not defined`
- **Következmény:** Az inventory service nem tud elindulni

**Választott megoldás:** Hiányzó import hozzáadása

**Változtatás (13. sor - új sor beszúrása):**
```diff
  from typing import Optional
  from decimal import Decimal
  from fastapi import APIRouter, Depends, HTTPException, Query, status
  from sqlalchemy.orm import Session
+ from pydantic import BaseModel, Field

  from backend.service_inventory.models.database import get_db
```

**Indoklás:**
- A `BaseModel` és `Field` a Pydantic alapvető komponensei, szükségesek schema definiáláshoz
- A fájlban a 215. sorban `StockUpdateRequest(BaseModel)` használatban van
- Standard pattern minden FastAPI/Pydantic service-ben

**Érintett sor:** 13 (új import sor)

**Sorszám:** 13

---

## 4. DOCKER-COMPOSE KONFIGURÁCIÓ VÁLTOZÁSOK

### Korábbi session-ökben végzett változások:

Az előző context ablakban (summary alapján) történt változtatások:

1. **JWT dependencies javítás** (részletek nem ismertek - korábbi session)
2. **Environment variable naming issues** (részletek nem ismertek - korábbi session)

**FONTOS:** Ezek a változások NEM DOKUMENTÁLTAK részletesen. Ha létezik korábbi change log vagy commit history, azt be kellene illeszteni ide.

---

## 5. JELENLEGI SERVICE STÁTUSZ (FRISSÍTVE: 2025-11-17 07:45)

### Docker Compose Services:

| Service | Port | Status | Notes |
|---------|------|--------|-------|
| postgres | 5432 | ✅ HEALTHY | PostgreSQL 15, sikeresen elindult |
| service_menu | 8001 | ✅ HEALTHY | Module 0 - Menu Service működik |
| service_orders | 8002 | ✅ HEALTHY | Module 1 - Orders Service működik |
| service_admin | 8008 | ✅ HEALTHY | Module 6 & 8 - Admin/RBAC Service működik |
| service_inventory | 8003 | ✅ HEALTHY | Module 5 - Inventory Service működik (lazy initialization-nel) |

### Database Status:
- ✅ RBAC seeding sikeresen lefutott
- ✅ 14 permission létrehozva
- ✅ 3 role létrehozva (Admin, Pultos, Szakács)
- ✅ 1 employee létrehozva (admin user)

### Authentication Test:
- ✅ Admin login működik (username: admin, password: 1234)
- ✅ JWT token generálás sikeres
- ✅ Token tartalmazza a szerepköröket és jogosultságokat

---

## 6. DEPLOYMENT SIKERES ✅

1. **Service rebuild szükséges:**
   ```bash
   docker-compose down
   docker-compose up -d --build service_admin service_inventory
   ```

2. **Inventory Service GCP credentials megoldás** (választani kell az opciók közül)

3. **Health check verification** minden service-re

4. **Database seeding** RBAC adatokkal

5. **API tesztelés** minden service health endpoint-ján

---

## 7. FONTOS JEGYZETEK

### 7.1. Dependency Management
- Minden service saját `requirements.txt` fájllal rendelkezik
- **Kritikus:** Pydantic verziónak egységesnek KELL lennie az összes service-ben
- Jelenlegi standard: `pydantic==2.9.0`, `pydantic-settings==2.5.0`

### 7.2. Google Cloud Dependencies
- Menu Service: GCS (images), Vertex AI Translation használ
- Inventory Service: GCS (invoices), Document AI (OCR) használ
- **Development környezetben:** GCP credentials opcionálissá kellene tenni

### 7.3. Docker Compose Version Warning
- Docker Compose figyelmeztetés: `version: '3.8'` obsolete
- Ez NEM kritikus hiba, de jövőben eltávolítható a docker-compose.yml-ből

---

## 8. VÁLTOZTATÁSOK AUDITÁLÁSA

### Session 1 (Előző context ablak):
- JWT dependencies javítás ❓ (részletek nem dokumentáltak)
- Environment variables javítás ❓ (részletek nem dokumentáltak)

### Session 2 (Jelenlegi):
- `backend/service_inventory/requirements.txt`: Pydantic 2.5.0 → 2.9.0 ✅
- `backend/service_admin/requirements.txt`: email-validator==2.1.0 hozzáadva ✅
- `backend/service_inventory/services/ocr_service.py`: Lazy initialization pattern implementálva (388-420. sor) ✅
- `backend/service_admin/routers/permissions.py`: Import path javítás (12. sor) - `backend.service_admin.database` → `backend.service_admin.models.database` ✅
- `backend/service_inventory/routers/inventory_items.py`: BaseModel import hozzáadva Pydantic-ból (13. sor) ✅
- `backend/service_admin/seed_rbac.py`: `is_admin` mező eltávolítása az Employee model instantiációból (369. sor) ✅

---

## 9. VISSZAÁLLÍTÁS (ROLLBACK INSTRUKCIÓK)

Ha bármelyik változtatást vissza kell állítani:

### Inventory Pydantic verzió visszaállítása:
```bash
# backend/service_inventory/requirements.txt
# Változtasd vissza a 12-13. sorokat:
pydantic==2.5.0
pydantic-settings==2.1.0
```

**FIGYELEM:** Ez visszahozza az eredeti `decimal_places` hibát!

### Admin Email Validator eltávolítása:
```bash
# backend/service_admin/requirements.txt
# Távolítsd el a 6. sort:
# email-validator==2.1.0
```

**FIGYELEM:** Ez visszahozza az EmailStr import hibát!

### OCR Service Lazy Initialization visszaállítása:
```python
# backend/service_inventory/services/ocr_service.py
# Változtasd vissza a 388-420. sorokat az eredeti egyszerű singleton-ra:

# Create singleton instance
ocr_service = OcrService()
```

**FIGYELEM:** Ez visszahozza a GCP credentials hiányzó hiba miatt a service startup failuret! A service nem fog elindulni development környezetben GCP credentials nélkül.

---

## 10. TESZTELÉSI CHECKLIST

- [x] PostgreSQL elérhető és healthy
- [x] Menu Service (8001) válaszol `/health` endpointra
- [x] Orders Service (8002) válaszol `/health` endpointra
- [x] Admin Service (8008) elindul email-validator-rel
- [x] Admin Service (8008) válaszol `/health` endpointra
- [x] Inventory Service (8003) elindul (lazy initialization megoldással)
- [x] Inventory Service (8003) válaszol `/health` endpointra
- [x] Database seeding lefut hibátlanul
- [x] Admin login működik default credentials-szel (admin/1234)

---

## 11. DEPLOYMENT ÖSSZEFOGLALÓ

### Összes Javítás (Session 2):

1. **backend/service_inventory/requirements.txt** - Pydantic verzió upgrade (2.5.0 → 2.9.0)
2. **backend/service_admin/requirements.txt** - email-validator dependency hozzáadva
3. **backend/service_inventory/services/ocr_service.py** - Lazy initialization pattern implementálva
4. **backend/service_admin/routers/permissions.py** - Import path javítva
5. **backend/service_inventory/routers/inventory_items.py** - BaseModel import hozzáadva
6. **backend/service_admin/seed_rbac.py** - is_admin mező eltávolítva Employee instantiációból (2 helyen)

### Eredmény:
✅ **TELJES DEPLOYMENT SIKERES**

Minden service működik, az adatbázis fel van töltve, az autentikáció tesztelt és működőképes.

### Production Teendők:
1. ⚠️ Változtasd meg az admin PIN kódot/jelszót (jelenleg: 1234)
2. ⚠️ Konfiguráld a GCP credentials-t production környezetben
3. ⚠️ Állítsd be a helyes JWT_SECRET_KEY-t
4. ⚠️ Konfiguráld a NTAK API kulcsokat

---

## DOKUMENTUM VÉGE

**Utolsó frissítés:** 2025-11-17 07:46 CET
**Státusz:** ✅ SIKERES - deployment teljes és működőképes
**Következő lépés:** Production környezet konfigurálása és biztonsági beállítások
