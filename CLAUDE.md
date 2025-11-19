# Claude AI - POS Projekt Gyorsreferencia

Ez a dokumentum a Claude AI ágensek számára készült gyorsreferencia a POS rendszer fejlesztéséhez.

## 📚 Tech Stack Összefoglaló

| Komponens | Technológia | Verzió |
|-----------|-------------|---------|
| **Backend** | Python (FastAPI) | 0.115.x |
| **Adatbázis** | PostgreSQL | 17.x (15-alpine docker) |
| **Frontend** | React (Vite) | 19.x / 6.x |
| **AI Fordítás** | Vertex AI Translation LLM | v2 |
| **AI OCR** | Google Document AI | v2 |
| **Képkezelés** | GCS + Cloud Functions + Pillow | N/A |

## 🚀 Fő Futtatási Parancsok

### Docker Compose (Teljes Stack)
```bash
# Összes szolgáltatás indítása háttérben
docker-compose up -d

# Logok valós időben
docker-compose logs -f

# Összes szolgáltatás leállítása
docker-compose down

# Szolgáltatások státuszának ellenőrzése
docker-compose ps
```

### Backend Mikroszolgáltatások (Fejlesztési Mód)
```bash
# Példa: Orders Service indítása
cd backend/service_orders
pip install -r requirements.txt
uvicorn main:app --reload --port 8002

# Tesztek futtatása
pytest
pytest tests/ -v
pytest tests/test_orders.py::test_create_order

# Tesztek lefedettséggel
pytest --cov=. --cov-report=html
```

### Frontend (React + Vite)
```bash
cd frontend

# Függőségek telepítése
npm install

# Fejlesztői szerver indítása
npm run dev

# Production build
npm run build

# Linter futtatása
npm run lint

# Előnézet production buildből
npm run preview
```

### Adatbázis Műveletek
```bash
# Kapcsolódás PostgreSQL konténerhez
docker exec -it pos-postgres psql -U pos_user -d pos_db

# Adatbázis séma exportálása
docker exec pos-postgres pg_dump -U pos_user -d pos_db --schema-only > schema.sql

# Demo adatok betöltése
python seed_demo_data.py
```

## 🗂️ Backend Szolgáltatások Áttekintése

### `backend/service_menu/` - **Modul 0: Terméktörzs és Menü**
- **Port:** 8001
- **Funkciók:**
  - Termékek és kategóriák kezelése
  - AI-alapú fordítások (Vertex AI Translation LLM)
  - Képfeltöltés és automatikus átméretezés (GCS + Cloud Functions)
  - Komplex módosítók kezelése (JSON struktúra)
  - Allergének és NTAK kategóriák
- **Kulcs Endpointok:**
  - `GET /products` - Termékek listázása
  - `POST /products` - Új termék létrehozása
  - `PUT /products/{id}` - Termék módosítása (automatikus fordítás)
  - `POST /products/{id}/images` - Kép feltöltés (Signed URL generálás)

### `backend/service_orders/` - **Modul 1: Rendeléskezelés**
- **Port:** 8002
- **Funkciók:**
  - Többcsatornás rendelések (pincér, online, önkiszolgáló)
  - Asztalkezelés és rendelések asztalokhoz társítása
  - Rendelés módosítások és sztornózás
  - NTAK ÁFA váltás kezelése
  - Tételenkénti státuszkövetés (pending, preparing, ready, delivered)
- **Kulcs Endpointok:**
  - `POST /orders` - Új rendelés létrehozása
  - `GET /orders/{id}` - Rendelés lekérdezése
  - `PUT /orders/{id}/items/{item_id}` - Tétel módosítása
  - `POST /orders/{id}/cancel` - Rendelés sztornózása

### `backend/service_inventory/` - **Modul 5: Készletkezelés**
- **Port:** 8003
- **Funkciók:**
  - Kettős készletrendszer (automatikus + manuális)
  - AI számlaolvasás (Google Document AI)
  - Készletmozgások nyilvántartása
  - Alapanyag receptúrák (termék dekompozíció)
  - Minimum készletszint riasztások
- **Kulcs Endpointok:**
  - `GET /inventory/items` - Készlettételek listázása
  - `POST /inventory/movements` - Készletmozgás rögzítése
  - `POST /inventory/invoices/ocr` - Számla feltöltés OCR feldolgozással
  - `GET /inventory/alerts` - Alacsony készletszintű tételek

### `backend/service_admin/` - **Modul 6 & 8: Adminisztráció és RBAC**
- **Port:** 8008
- **Funkciók:**
  - Szerepkör-alapú jogosultságkezelés (RBAC)
  - NTAK adatszolgáltatás
  - HACCP nyilvántartás
  - Offline szinkronizáció kezelése
  - Felhasználók és munkakörök kezelése
- **Kulcs Endpointok:**
  - `POST /auth/login` - Bejelentkezés (JWT token)
  - `GET /users` - Felhasználók listázása
  - `POST /ntak/submit` - NTAK adatcsomag küldése
  - `GET /ntak/status` - NTAK státusz lekérdezése

### `backend/service_crm/` - **Modul 7: CRM és Integrációk**
- **Port:** 8004 (vagy dinamikus)
- **Funkciók:**
  - Törzsvevők kezelése
  - Hitelkeret nyilvántartás
  - Kedvezmények és törzsvásárlói programok
  - Külső integrációk (SZÉP kártya, stb.)
- **Kulcs Endpointok:**
  - `GET /customers` - Törzsvevők listázása
  - `POST /customers` - Új törzsvevő létrehozása
  - `GET /customers/{id}/credit` - Hitelkeret lekérdezése

### `backend/service_logistics/` - **Modul 3 & 4: KDS és Számlázás**
- **Port:** Változó (vagy több alszolgáltatás)
- **Funkciók:**
  - Konyhai Kijelző rendszer (KDS)
  - Számlázás és fizetések
  - SZÉP kártya integráció
  - NAV Online Számla

## 🏗️ Mikroszolgáltatás Architektúra

```
┌─────────────────┐
│   Frontend      │
│  (React/Vite)   │
└────────┬────────┘
         │
         v
┌────────────────────┐
│   API Gateway      │ (Opcionális - fejlesztés alatt)
└────────┬───────────┘
         │
    ┌────┴────────────────────────┐
    │                             │
    v                             v
┌───────────────┐         ┌──────────────┐
│ service_menu  │◄────────┤ service_admin│
│   (Port 8001) │         │  (Port 8008) │
└───────────────┘         └──────────────┘
         │                        │
         │                        │
         v                        v
┌───────────────┐         ┌──────────────┐
│service_orders │◄────────┤  service_crm │
│   (Port 8002) │         │  (Port 8004) │
└───────────────┘         └──────────────┘
         │
         v
┌───────────────┐
│ PostgreSQL    │
│  (Port 5432)  │
└───────────────┘
```

## 📝 Fejlesztési Megjegyzések

### Környezeti Változók
- Minden szolgáltatásnak van `.env.example` fájlja
- Docker Compose automatikusan kezeli a környezeti változókat
- Lokális fejlesztéshez másold át: `cp .env.example .env`

### API Dokumentáció
- Minden FastAPI szolgáltatás automatikusan generál OpenAPI docs-ot
- Elérhető: `http://localhost:{PORT}/docs` (pl. http://localhost:8002/docs)
- Alternatív: `http://localhost:{PORT}/redoc`

### Adatbázis Migrációk
- Jelenleg manuális SQL scriptek (a DATABASE_SCHEMA.md alapján)
- Jövőbeni terv: Alembic migráció rendszer bevezetése

### Tesztelés
- Unit tesztek: `pytest tests/`
- Integrációs tesztek: `pytest tests/integration/`
- API tesztek: `pytest tests/api/`

### RBAC (Jogosultságkezelés)
- Központi implementáció: `backend/service_admin/`
- Minden szolgáltatás importálja: `from service_admin.dependencies import require_permission`
- Használat endpointokban:
  ```python
  @router.post("/orders", dependencies=[Depends(require_permission("orders.create"))])
  ```

## 🔍 Hasznos Parancsok Hibakereséshez

```bash
# Docker logok csak egy szolgáltatásból
docker-compose logs -f service_orders

# Futó konténerek listázása
docker ps

# Konténer shell elérése
docker exec -it pos-service-orders /bin/bash

# Adatbázis kapcsolat tesztelése
docker exec pos-postgres pg_isready -U pos_user -d pos_db

# Hálózati kapcsolat tesztelése szolgáltatások között
docker exec pos-service-orders curl http://service_admin:8008/health
```

## 📚 Kapcsolódó Dokumentumok

- **ARCHITECTURE.md** - Részletes architektúra leírás
- **DATABASE_SCHEMA.md** - Teljes adatbázis séma
- **API_SPECS.md** - API specifikációk
- **TECH_STACK.md** - Technológiai döntések indoklása
- **SPRINT_PLAN.md** - 48 órás fejlesztési sprint terv

---

**Verzió:** 1.4
**Utolsó frissítés:** 2025-11-19
**Készítette:** Claude Code Web Agent
