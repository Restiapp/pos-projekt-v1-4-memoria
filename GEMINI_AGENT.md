# Gemini Agent - Mikroszolgáltatások Üzemeltetési Útmutató

Ez a dokumentum a Gemini AI ágensek (pl. Vertex AI Studio agents) számára készült gyakorlati útmutató a POS rendszer mikroszolgáltatásainak futtatásához és teszteléséhez.

## 🏗️ Mikroszolgáltatások Felépítése és Működése

### Architektúra Áttekintése

A POS rendszer **mikroszolgáltatás architektúrát** használ, ahol minden modul egy önálló FastAPI alkalmazás:

```
POS System Architecture
=======================

┌──────────────────────────────────────────────────────────┐
│                     Frontend (React)                      │
│                   http://localhost:5173                   │
└────────────────────────┬─────────────────────────────────┘
                         │
                         │ HTTP/REST API
                         │
         ┌───────────────┴────────────────┐
         │                                │
         v                                v
┌─────────────────┐              ┌────────────────┐
│  API Gateway    │              │   Direct API   │
│  (Jövőbeli)     │              │   Calls (Dev)  │
└────────┬────────┘              └────────┬───────┘
         │                                │
         └────────────┬───────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        v             v             v
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│service_menu  │ │service_orders│ │service_admin │
│  Port 8001   │ │  Port 8002   │ │  Port 8008   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │    ┌───────────┴────────┐       │
       │    │                    │       │
       v    v                    v       v
┌──────────────┐         ┌────────────────┐
│service_crm   │         │service_inventory│
│  Port 8004   │         │   Port 8003    │
└──────┬───────┘         └────────┬───────┘
       │                          │
       └────────────┬─────────────┘
                    │
                    v
         ┌────────────────────┐
         │   PostgreSQL DB    │
         │    Port 5432       │
         │  Database: pos_db  │
         └────────────────────┘
```

### Szolgáltatások Közötti Kommunikáció

1. **Szinkron REST API hívások** - Azonnali válasz szükséges esetén
   - Példa: Orders Service → Menu Service (termék ár lekérdezés)
   - Belső Docker hálózaton: `http://service_menu:8001/products/123`

2. **Aszinkron Pub/Sub** - Nem időkritikus, garantált végrehajtás
   - Példa: "Rendelés lezárva" esemény → Készletcsökkentés + NTAK jelentés
   - Technológia: Google Cloud Pub/Sub (production), vagy RabbitMQ (dev)

3. **Közös PostgreSQL Adatbázis** - Állapotmegőrzés
   - Minden szolgáltatás ugyanahhoz az adatbázishoz csatlakozik
   - Táblák logikailag elkülönítve (pl. `orders`, `products`, `inventory_items`)

## 🚀 Rendszer Indítása

### 1. Teljes Stack Indítása (Docker Compose)

Ez a **legegyszerűbb és ajánlott módszer** fejlesztéshez és teszteléshez:

```bash
# A projekt gyökérkönyvtárában
cd /home/user/pos-projekt-v1-4-memoria

# Összes szolgáltatás indítása háttérben
docker-compose up -d

# Várjunk, amíg minden szolgáltatás elindul (~30-60 másodperc)
# Ellenőrizzük a státuszt:
docker-compose ps

# Várható kimenet:
# NAME                COMMAND                  STATUS              PORTS
# pos-postgres        "docker-entrypoint..."   Up (healthy)        0.0.0.0:5432->5432/tcp
# pos-service-menu    "uvicorn main:app..."    Up (healthy)        0.0.0.0:8001->8000/tcp
# pos-service-orders  "uvicorn main:app..."    Up (healthy)        0.0.0.0:8002->8000/tcp
# pos-service-admin   "uvicorn main:app..."    Up (healthy)        0.0.0.0:8008->8000/tcp
# ...

# Logok követése valós időben
docker-compose logs -f

# Vagy csak egy szolgáltatás logja:
docker-compose logs -f service_orders
```

### 2. Egyedi Szolgáltatás Indítása (Fejlesztés)

Ha csak egy szolgáltatáson dolgozol, indítsd azt manuálisan:

```bash
# Példa: Orders Service
cd backend/service_orders

# Virtuális környezet létrehozása (első alkalommal)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# VAGY
venv\Scripts\activate     # Windows

# Függőségek telepítése
pip install -r requirements.txt

# Környezeti változók beállítása
cp .env.example .env
# Szerkeszd az .env fájlt: nano .env

# Szolgáltatás indítása hot-reload módban
uvicorn main:app --reload --port 8002

# A szolgáltatás elérhető: http://localhost:8002
# API dokumentáció: http://localhost:8002/docs
```

### 3. Frontend Indítása

```bash
cd frontend

# Függőségek telepítése (első alkalommal)
npm install

# Fejlesztői szerver indítása
npm run dev

# Várható kimenet:
# VITE v6.x.x  ready in XXX ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: use --host to expose
```

## 🧪 API Tesztek Futtatása

### Pytest Alapú Tesztek

Minden mikroszolgáltatásnak van saját `tests/` mappája unit és integrációs tesztekkel.

#### 1. Teljes Teszt Suite Futtatása

```bash
# A projekt gyökérkönyvtárában
cd backend/service_orders

# Aktiváld a virtuális környezetet (ha még nem aktív)
source venv/bin/activate

# Összes teszt futtatása
pytest

# Részletes kimenettel
pytest -v

# Csak egy specifikus teszt fájl
pytest tests/test_orders.py

# Csak egy specifikus teszt függvény
pytest tests/test_orders.py::test_create_order

# Tesztek lefedettséggel (coverage)
pytest --cov=. --cov-report=html
# A jelentés itt lesz: htmlcov/index.html
```

#### 2. Teszt Kategóriák

```bash
# Csak unit tesztek (gyors, nincs külső függőség)
pytest tests/unit/

# Csak integrációs tesztek (lassabb, adatbázis szükséges)
pytest tests/integration/

# Csak API endpoint tesztek
pytest tests/api/

# Teszt futtatása kimenet nyomtatással (debugging)
pytest -s tests/test_orders.py::test_create_order_with_items
```

#### 3. Docker Környezetben Tesztelés

Ha a szolgáltatások Docker-ben futnak, futtasd a teszteket a konténerben:

```bash
# Belépés a konténerbe
docker exec -it pos-service-orders /bin/bash

# A konténeren belül:
pytest tests/ -v

# Vagy közvetlenül kívülről:
docker exec pos-service-orders pytest tests/ -v
```

### Példa Teszt Esetek

#### Service Orders - Rendelés Létrehozás Teszt

```python
# tests/api/test_orders.py
def test_create_order_success():
    """Test successful order creation with valid data"""
    response = client.post(
        "/orders",
        json={
            "table_id": 5,
            "guest_count": 4,
            "order_items": [
                {
                    "product_id": 101,
                    "quantity": 2,
                    "course": "main",
                    "notes": "No onions"
                }
            ]
        },
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["table_id"] == 5
    assert data["guest_count"] == 4
    assert len(data["order_items"]) == 1
```

#### Service Menu - Termék Lekérdezés Teszt

```python
# tests/api/test_products.py
def test_get_product_by_id():
    """Test retrieving a product by ID"""
    response = client.get("/products/101")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 101
    assert "name" in data
    assert "price" in data
```

### cURL Alapú API Tesztek (Manuális)

Ha gyorsan tesztelni szeretnél egy endpointot:

```bash
# Health check
curl http://localhost:8002/health

# Bejelentkezés (token megszerzése)
curl -X POST http://localhost:8008/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Termékek listázása
curl http://localhost:8001/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Új rendelés létrehozása
curl -X POST http://localhost:8002/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "table_id": 5,
    "guest_count": 2,
    "order_items": [
      {
        "product_id": 101,
        "quantity": 1,
        "course": "starter",
        "notes": "Extra spicy"
      }
    ]
  }'
```

## 🔍 Hibaelhárítás

### 1. Szolgáltatás Nem Indul

```bash
# Ellenőrizd a logokat
docker-compose logs service_orders

# Gyakori problémák:
# - Adatbázis nem elérhető → Várd meg, hogy a postgres konténer "healthy" legyen
# - Port már használatban → docker-compose down && docker-compose up -d
# - Környezeti változók hiányoznak → Ellenőrizd a .env fájlt
```

### 2. Adatbázis Kapcsolati Hiba

```bash
# Ellenőrizd, hogy a PostgreSQL fut-e
docker exec pos-postgres pg_isready -U pos_user -d pos_db

# Kimenet legyen: "pos_db:5432 - accepting connections"

# Ha nem fut, indítsd újra:
docker-compose restart postgres

# Csatlakozz manuálisan az adatbázishoz:
docker exec -it pos-postgres psql -U pos_user -d pos_db
# SQL konzolon: \dt (táblák listázása)
```

### 3. Szolgáltatások Nem Kommunikálnak

```bash
# Ellenőrizd a Docker hálózatot
docker network inspect pos-projekt-v1-4-memoria_pos-network

# Teszteld a kapcsolatot konténerek között
docker exec pos-service-orders curl http://service_menu:8001/health
# Válasz legyen: {"status": "healthy"}

# Ha nem működik:
docker-compose down
docker-compose up -d
```

### 4. Frontend Nem Éri El a Backend-et

```bash
# Ellenőrizd a CORS beállításokat
# backend/service_orders/main.py:
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],  # Frontend URL
#     ...
# )

# Ellenőrizd, hogy a backend fut-e:
curl http://localhost:8002/health
```

## 📊 API Dokumentáció Elérése

Minden FastAPI szolgáltatás automatikusan generál interaktív API dokumentációt:

```
Service Menu:      http://localhost:8001/docs
Service Orders:    http://localhost:8002/docs
Service Inventory: http://localhost:8003/docs
Service Admin:     http://localhost:8008/docs
Service CRM:       http://localhost:8004/docs
```

Az OpenAPI (Swagger) UI-on keresztül:
- Megtekintheted az összes endpointot
- Tesztelheted az API hívásokat közvetlenül a böngészőből
- Látod a request/response sémákat

## 🔐 Authentikáció és Jogosultságok

### JWT Token Megszerzése

```bash
# 1. Bejelentkezés
curl -X POST http://localhost:8008/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Válasz:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }

# 2. Token használata más endpointoknál
curl http://localhost:8002/orders \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### RBAC Ellenőrzés

A jogosultságok a `service_admin` szolgáltatásban vannak kezelve. Minden védett endpoint ellenőrzi a felhasználó szerepkörét:

```python
# Példa: csak "waiter" vagy "admin" szerepkör hozhat létre rendelést
@router.post("/orders", dependencies=[Depends(require_permission("orders.create"))])
```

## 📝 Környezeti Változók Konfigurálása

### Docker Compose Környezet

A `docker-compose.yml` fájl automatikusan kezeli a legtöbb környezeti változót. Ha módosítani szeretnéd őket:

```bash
# 1. Készíts egy .env fájlt a projekt gyökérkönyvtárában
cp .env.example .env

# 2. Szerkeszd az értékeket
nano .env

# Példa .env tartalom:
POSTGRES_PASSWORD=my_secure_password
JWT_SECRET_KEY=my_super_secret_jwt_key
GCP_PROJECT_ID=my-gcp-project-id
NTAK_API_KEY=my_ntak_api_key

# 3. Újraindítás az új értékekkel
docker-compose down
docker-compose up -d
```

### Lokális Fejlesztési Környezet

Minden szolgáltatás mappájában van egy `.env.example`:

```bash
cd backend/service_orders
cp .env.example .env
nano .env

# Szükséges minimális beállítások:
# DATABASE_URL=postgresql://pos_user:password@localhost:5432/pos_db
# JWT_SECRET_KEY=change-this-in-production
# ADMIN_SERVICE_URL=http://localhost:8008
```

## 🎯 Gyors Referencia Parancsok

```bash
# === DOCKER COMPOSE ===
docker-compose up -d              # Indítás
docker-compose down               # Leállítás
docker-compose ps                 # Státusz
docker-compose logs -f            # Logok
docker-compose restart service_orders  # Újraindítás

# === TESZTELÉS ===
pytest                            # Összes teszt
pytest -v                         # Részletes kimenet
pytest tests/api/                 # Csak API tesztek
pytest --cov=. --cov-report=html  # Lefedettséggel

# === ADATBÁZIS ===
docker exec -it pos-postgres psql -U pos_user -d pos_db  # SQL konzol
docker exec pos-postgres pg_dump -U pos_user pos_db > backup.sql  # Backup

# === DEBUGGING ===
docker exec -it pos-service-orders /bin/bash  # Konténer shell
docker-compose logs -f service_orders         # Logok követése
curl http://localhost:8002/health             # Health check
```

## 📚 További Információk

- **API_SPECS.md** - Részletes API endpoint leírások
- **DATABASE_SCHEMA.md** - Adatbázis táblák és kapcsolatok
- **ARCHITECTURE.md** - Mikroszolgáltatás architektúra részletei
- **CLAUDE.md** - Claude AI ágensek gyorsreferenciája

---

**Verzió:** 1.0
**Utolsó frissítés:** 2025-11-19
**Készítette:** Claude Code Web Agent
**Célközönség:** Gemini AI Agents (Vertex AI Studio)
