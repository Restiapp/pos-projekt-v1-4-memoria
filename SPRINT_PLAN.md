> **ARCHIVED / ELAVULT DOKUMENTUM**
> Ez a dokumentum torteneti celokat szolgal.
> A fejleszteshez **NE** ezt hasznald specifikaciokent.
> Aktualis fo specifikacio: `docs/spec/SYSTEM_MASTER_SPEC_V1.md`
> Aktualis roadmap: `docs/roadmap/MASTER_ROADMAP.md`

# V3.0 Master Plan - Resti Bistro POS Rendszer (ARCHIVED)

**Verzió:** 3.0
**Állapot:** ARCHIVED (regi terv)
**Utolsó Frissítés:** 2025-01-18
**Követési Branch:** main

---

## 📋 Stratégiai Döntések és Architektúra Bővítés

### Miért térünk el a V1.4 Sprint Tervtől?

A V1.4 egy "48 órás hiperagresszív sprint terv" volt, amely jó alapot adott, de **nem képes támogatni a valós üzleti igényeket**. A V3.0 Master Plan a következő kritikus problémákat oldja meg:

1. **Hiányzó Üzleti Folyamatok:**
   - Nincs törzsadatkezelés (munkatársak, asztalok, receptek)
   - Nincs inventár és raktárkezelés
   - Nincs CRM és vendégkezelés
   - Nincs pénzügyi modul és analitika

2. **Szétszórt Modulok:**
   - Az eredeti tervezés szerint 8 modul volt 1 monolit szolgáltatásban
   - Ez skálázási és karbantartási gondokat okozott volna

3. **Valós Integrációk:**
   - Számlázz.hu API integráció (online számlázás)
   - NTAK küldés (kötelező vendéglátóipari adatszolgáltatás)
   - Valós Google Cloud infrastruktúra (GCS, Vertex AI)

---

## 🏗️ Architektúra: Microservices-alapú rendszer

### Microservice-ek (7 fő szervíz)

| Szervíz | Port | Cél | Felelősség |
|---------|------|-----|------------|
| `service_menu` | 8001 | Terméktörzs és Menü | Termékek, kategóriák, módosítók, receptek, képek (GCS) |
| `service_orders` | 8002 | Rendeléskezelés | Rendelések, asztalok, tételek, fizetések, NTAK |
| `service_inventory` | 8003 | Raktárkezelés | Alapanyagok, beszerzések, leltár, selejtezés, AI számlakezelés |
| `service_admin` | 8004 | Adminisztráció | Munkatársak, RBAC, jogosultságok, pénzügy, Számlázz.hu |
| `service_crm` | 8005 | CRM és Vendégkezelés | Vendégek, címek, pontok, kupónok, ajándékkártyák |
| `service_logistics` | 8006 | Kiszállítás | Kiszállítási zónák, futárok, járművek, tracking |
| `frontend` | 3000 | React (Vite) | Felhasználói felület: POS, KDS, Admin, Dashboard |

**Közös PostgreSQL adatbázis:** `pos_db` (minden service külön sémát használ)

---

## 🎯 V3.0 Fázisok és Állapot

### ✅ **Fázis 0: Alapok Bővítése (Core Model & Schema Expansion)** - KÉSZ

**Cél:** Az alapvető adatmodellek kiterjesztése a valós üzleti igények szerint.

#### Orders Service Bővítés (service_orders)
- **Table:** `section`, `parent_table_id` (asztal összevonás)
- **Order:** `guest_count`, `course_sequence`, `loyalty_points_earned`
- **OrderItem:** `course`, `special_instructions_internal`, `waste_logged`

#### Admin Service Bővítés (service_admin)
- **Employee:** `hire_date`, `employment_type`, `hourly_rate`, `overtime_hours`
- **Új modellek:**
  - `FinancialTransaction` (cash_drawer_id, transaction_type, amount)
  - `CashDrawer` (cash_on_hand, expected_cash)
  - `Asset` (oven, hűtő, POS terminál nyilvántartás)
  - `Vehicle` (cégautók, futárjárművek)

#### Inventory Service Bővítés (service_inventory)
- **WasteLog:** Selejtezési napló (tétel alapú nyomon követés)

#### Új Service: CRM (service_crm)
- **Customer:** Vendégek (név, email, telefon, loyalty pontok)
- **Address:** Kiszállítási címek (customer_id FK)
- **Coupon:** Kuponok (discount_type, usage_limit)
- **GiftCard:** Ajándékkártyák (balance, expiry_date)

#### Új Service: Logistics (service_logistics)
- **DeliveryZone:** Kiszállítási zónák (polygon térképen, delivery_fee)
- **Courier:** Futárok (name, phone, vehicle_id)

**Állapot:** ✅ 8 ág merged, +2080 sor kód, 32 fájl módosítva

---

### ✅ **Fázis 1: Vendégtér és Pult Funkciók (Guest & POS)** - KÉSZ

**Cél:** Működő backend API végpontok a rendeléskezeléshez, pénzügyekhez és CRM-hez.

#### Orders Service Logika Bővítés
- **Table Management API:**
  - `POST /api/v1/tables/{table_id}/merge/{target_table_id}` - Asztal összevonás
  - `POST /api/v1/tables/{table_id}/split` - Asztal szétválasztás
  - `PATCH /api/v1/tables/{table_id}/move` - Asztal áthelyezés
- **TableService:** Python service layer az asztalkezeléshez

#### Admin Service Logika Bővítés
- **Finance Module:**
  - `POST /api/v1/finance/transactions` - Pénzügyi tranzakció rögzítése
  - `GET /api/v1/finance/cash-drawer/{drawer_id}` - Pénztárfiók állapot
  - `POST /api/v1/finance/cash-drawer/{drawer_id}/open` - Nyitóösszeggel
  - `POST /api/v1/finance/cash-drawer/{drawer_id}/close` - Záróösszeg
- **Számlázz.hu Integration:**
  - `POST /api/v1/integrations/szamlazzhu/invoice` - Számla küldés
  - `GET /api/v1/integrations/szamlazzhu/invoice/{invoice_number}` - Számla lekérdezés
  - XML generálás (Agent ID: `12345678`, API Key: env-based)

#### CRM Service Felépítése
- **Customer API:**
  - `POST /api/v1/crm/customers` - Vendég létrehozása
  - `GET /api/v1/crm/customers/{customer_id}` - Vendég adatlap
  - `PATCH /api/v1/crm/customers/{customer_id}/loyalty-points` - Pontok hozzáadása
- **Coupon API:**
  - `POST /api/v1/crm/coupons` - Kupon létrehozása
  - `GET /api/v1/crm/coupons/{code}` - Kupon ellenőrzés
  - `POST /api/v1/crm/coupons/{code}/redeem` - Kupon beváltás

**Állapot:** ✅ 3 ág merged, +4347 sor kód, 27 fájl módosítva

---

### 🔄 **Fázis 2: Kiszállítási Ökoszisztéma (Logistics)** - FOLYAMATBAN

**Cél:** Teljes körű kiszállítási rendszer futárokkal, zónákkal és valós idejű trackingel.

#### Logistics Service API
- **DeliveryZone Management:**
  - `POST /api/v1/logistics/zones` - Új zóna (polygon koordináták)
  - `GET /api/v1/logistics/zones/calculate-fee` - Cím alapján díj kalkuláció
- **Courier Management:**
  - `POST /api/v1/logistics/couriers` - Futár hozzáadása
  - `GET /api/v1/logistics/couriers/available` - Elérhető futárok
  - `PATCH /api/v1/logistics/couriers/{courier_id}/status` - Státusz frissítés
- **Delivery Tracking:**
  - `POST /api/v1/logistics/deliveries` - Kiszállítás indítása
  - `PATCH /api/v1/logistics/deliveries/{delivery_id}/status` - Státusz frissítés (PICKED_UP, ON_WAY, DELIVERED)
  - WebSocket channel: `/ws/delivery/{delivery_id}` - Valós idejű tracking

#### Frontend Integration
- **Térképes Zóna Editor:** Polygon rajzolás Google Maps API-val
- **Futár Dashboard:** Napi feladatok, útvonaloptimalizálás
- **Live Tracking:** Vendég oldali követés (SMS link + WebSocket)

**Állapot:** 📋 Tervezett, modellek kész (Fázis 0), API implementálás alatt

---

### 📋 **Fázis 3: Háttér Műveletek (Back-Office)** - TERVEZETT

**Cél:** Teljes körű raktárkezelés, receptkezelés és beszállítói integráció.

#### Inventory Service Bővítés
- **Recipe Engine:**
  - `POST /api/v1/inventory/recipes` - Recept létrehozása (product_id, ingredients[])
  - Automatikus készletcsökkentés rendelés lezárásakor
- **Supplier Management:**
  - `POST /api/v1/inventory/suppliers` - Beszállító hozzáadása
  - `POST /api/v1/inventory/purchase-orders` - Megrendelés
- **AI Invoice Processing:**
  - Google Document AI (Form Parser API)
  - OCR → JSON → automatikus tranzakció rögzítés

#### Admin Service Analitika
- **Dashboard Metrics:**
  - Napi/heti/havi bevétel (Finance API aggregált query-k)
  - Top termékek (service_orders JOIN)
  - Munkatársi teljesítmény (órabér + túlóra kalkuláció)
- **Asset Management:**
  - Karbantartási naptár (`Asset.last_maintenance_date`)
  - Élettartam követés (beszerzési dátum + warranty_period)

**Állapot:** 🎯 Jövőbeli (Q1 2025 után)

---

### 🎯 **Fázis 4: Finomhangolás és CRM Bővítés** - JÖVŐBELI

**Cél:** Profi CRM funkciók, ajándékkártyák, hűségprogram és marketing automatizáció.

#### CRM Service Advanced Features
- **Gift Card System:**
  - `POST /api/v1/crm/gift-cards` - Kártya aktiválás
  - `POST /api/v1/crm/gift-cards/{card_id}/top-up` - Feltöltés
  - `POST /api/v1/crm/gift-cards/{card_id}/deduct` - Felhasználás
- **Loyalty Program:**
  - `GET /api/v1/crm/customers/{id}/rewards` - Elérhető jutalmak
  - `POST /api/v1/crm/customers/{id}/redeem-reward` - Jutalom beváltás
- **Marketing Automation:**
  - Email kampányok (Mailchimp API)
  - SMS értesítések (Twilio API)

#### Frontend Advanced UI
- **Customer 360 View:** Teljes ügyfélprofil (rendelések, pontok, címek)
- **Campaign Manager:** Kupon és kampány létrehozó UI
- **Analytics Dashboard:** Retention rate, CLTV, churn analysis

**Állapot:** 📋 Backlog (Post-MVP)

---

## 🛠️ Technológiai Stack

### Backend
- **Nyelv:** Python 3.11+
- **Framework:** FastAPI 0.110+
- **ORM:** SQLAlchemy 2.0
- **Adatbázis:** PostgreSQL 16 (Cloud SQL vagy self-hosted)
- **Auth:** JWT (PyJWT)
- **Validáció:** Pydantic v2

### Frontend
- **Framework:** React 18 (Vite)
- **Routing:** React Router v6
- **State Management:** Zustand + React Query
- **UI:** Tailwind CSS + shadcn/ui
- **Térképek:** Google Maps JavaScript API

### Infrastruktúra
- **Containerization:** Docker Compose (development), Kubernetes (production option)
- **Felhő:** Google Cloud Platform
  - Cloud Storage (GCS): Képek tárolása
  - Cloud Functions: Képfeldolgozás (Pillow)
  - Vertex AI: Fordítás (Translation API)
  - Document AI: Számla OCR
- **CI/CD:** GitHub Actions (terv)

### Integrációk
- **Számlázás:** Számlázz.hu XML Agent API
- **NTAK:** Magyar NAV adatküldés (WebService XML)
- **Email:** SendGrid vagy Mailchimp (terv)
- **SMS:** Twilio (terv)

---

## 📊 Jelenlegi Állapot és Statisztikák

### ✅ Elkészült (V1.4 + V3.0 Fázis 0 + Fázis 1)

| Komponens | Állapot | Fájlok | Kódsorok | Megjegyzés |
|-----------|---------|--------|----------|------------|
| **V1.4 Alaprendszer** | ✅ KÉSZ | ~50 | ~8000 | POS, KDS, Auth, alapvető rendeléskezelés |
| **V3.0 Fázis 0** | ✅ KÉSZ | 32 | +2080 | Schema bővítések (8 ág merged) |
| **V3.0 Fázis 1** | ✅ KÉSZ | 27 | +4347 | API végpontok (3 ág merged) |
| **Docker Setup** | ✅ KÉSZ | 8 | ~400 | 7 service + PostgreSQL konténerek |
| **Demo Seeding** | ✅ KÉSZ | 1 | ~200 | 9 asztal, 5 kategória, 19 termék |

**Összesen:** ~110 fájl, ~14,800+ sor működő kód

---

### 🔄 Folyamatban (V3.0 Fázis 2)

- [ ] Logistics API végpontok (DeliveryZone, Courier, Delivery)
- [ ] Frontend térképes zóna editor
- [ ] WebSocket tracking implementáció
- [ ] Futár mobilalkalmazás (opcionális)

---

### 📋 Jövőbeli Mérföldkövek

| Mérföldkő | Cél Dátum | Leírás |
|-----------|-----------|--------|
| **Fázis 2 Lezárása** | 2025-01-25 | Logistics teljes működés |
| **Fázis 3 Start** | 2025-02-01 | Inventory + Recipes implementáció |
| **V3.0 Release** | 2025-03-01 | Teljes rendszer production-ready |
| **Fázis 4 Start** | 2025-04-01 | Advanced CRM és marketing |

---

## 🚀 Hogyan Indítsd el a Rendszert?

### Gyors Start (Docker Compose)

```bash
# 1. Klónozás
git clone <repository-url>
cd pos-projekt-v1-4-memoria

# 2. Környezeti változók
cp backend/service_admin/.env.example backend/service_admin/.env
# Töltsd ki a DB és JWT titkok!

# 3. Indítás
docker compose up -d --build

# 4. Demo adatok
docker exec pos-service-orders python seed_demo_data.py

# 5. Frontend
# http://localhost:3000
# Bejelentkezés: username=jkovacs, PIN=1234
```

### Service Port Mapping

| URL | Service | Funkció |
|-----|---------|---------|
| http://localhost:3000 | Frontend | POS UI |
| http://localhost:8001/docs | service_menu | Terméktörzs Swagger |
| http://localhost:8002/docs | service_orders | Rendelések Swagger |
| http://localhost:8003/docs | service_inventory | Raktár Swagger |
| http://localhost:8004/docs | service_admin | Admin Swagger |
| http://localhost:8005/docs | service_crm | CRM Swagger |
| http://localhost:8006/docs | service_logistics | Logistics Swagger |

---

## 🧑‍💻 Fejlesztési Workflow

### Git Branching Strategy

- `main` - Production-ready kód
- `develop` - Integration branch (opcionális)
- `feature/*` - Új funkció ágak
- `claude/*` - AI által generált ágak (Claude Code)

### Merge Policy

```bash
# Feature branch merge (always --no-ff)
git checkout main
git merge --no-ff claude/feature-xyz
```

**Miért `--no-ff`?** Tiszta történet, minden feature explicit commit ponttal jelenik meg.

---

## 📝 Kapcsolódó Dokumentumok

- `ARCHITECTURE.md` - Rendszerarchitektúra részletesen
- `DATABASE_SCHEMA.md` - Teljes adatbázis séma (7 service)
- `FILE_STRUCTURE.txt` - Könyvtárstruktúra
- `skills/` - Claude AI Skill könyvtár (modulonkénti útmutatók)
- `docs/integration/` - Számlázz.hu, NTAK integrációs dokumentációk

---

## 🎯 Következő Lépések (Immediate TODO)

1. **Fázis 2 Befejezése:**
   - [ ] Logistics API végpontok implementálása
   - [ ] Frontend térképes UI (Google Maps)
   - [ ] WebSocket tracking

2. **Production Readiness:**
   - [ ] Környezeti változók audit (`.env` minden service-nél)
   - [ ] GitHub Actions CI/CD pipeline
   - [ ] Kubernetes manifests (opcionális)

3. **Dokumentáció Frissítés:**
   - [ ] API dokumentáció (minden végpont példákkal)
   - [ ] User Guide (PDF export)

---

## ⚠️ KRITIKUS MEGJEGYZÉSEK

1. **Adatbázis Migráció:**
   - Jelenleg `Base.metadata.create_all()` (development)
   - Production-ban használj **Alembic migration**-öket!

2. **JWT Secret:**
   - SOHA ne commit-old a `.env` fájlt!
   - Production-ban használj erős random secret-et:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```

3. **NTAK és Számlázz.hu:**
   - Teszt Agent ID-k használatban (dummy küldés)
   - Production-ban valós hitelesítő adatokkal!

---

**Utoljára Frissítette:** Claude Code AI
**Kontextus ID:** SPRINT_PLAN_V3.0_2025-01-18
**Git Branch:** main (commit: latest)

---

🚀 **A V3.0 egy élő, folyamatosan fejlődő terv. Minden fázis lezárása után frissítsd ezt a dokumentumot!**
