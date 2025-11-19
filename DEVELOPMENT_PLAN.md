# Fejlesztési Terv

*Jelmagyarázat:*
- `[B]`: Backend
- `[F]`: Frontend
- `[T]`: Teszt / QA
- `[X]`: Cross-service / Infra
- `[PÁRHUZAMOS]`: Párhuzamosan végezhető feladat

---

## 0. Globális / közös előkészítő taskok

### X0 – Repo dokumentáció az AI-k számára [X] [PÁRHUZAMOS]
- **Cél:** Egységes “README” az ágenseknek (Claude, Gemini, Jules, GPT 5.1).
- **Feladatok:**
  - `CLAUDE.md`:
    - stack rövid összefoglaló
    - futtatási parancsok (docker compose, pytest, front build)
    - fő mappastruktúra + service_* leírás
  - `GEMINI_AGENT.md`:
    - hogyan futnak a mikroszolgák
    - hogyan futnak az API / e2e tesztek
- **Elfogadás:** repo gyökerében megvannak a fájlok, CI-ben linkelve.

---

## A. EPIC – Vendégtér + Kassza (“On-prem Dining Flow”)

### A1 – Asztaltérkép API véglegesítése (szekciók, merge, move) [B] [PÁRHUZAMOS]
- **Leírás:** A `service_orders` (vagy dedikált `service_tables`) kiegészítése, hogy a frontend minden szükséges műveletet el tudjon végezni az asztaltérképen.
- **Feladatok:**
  - `tables` modell/ORM ellenőrzése: `section`, `parent_table_id`, `capacity` mezők.
  - Endpointok: `GET /tables?section=...`, `POST /tables/{id}/move`, `POST /tables/merge`, `POST /tables/split`.
  - RBAC: csak megfelelő role módosíthat asztalokat.
- **Elfogadás:** OpenAPI spec-ben minden endpoint megjelenik; Unit teszt: merge + move működik.

### A2 – Vendégszám + CRM integráció rendelésre [B] [PÁRHUZAMOS A1-gyel]
- **Leírás:** `orders.customer_id` összekötése a `crm.customers.customer_uid` rendszerével.
- **Feladatok:**
  - `POST /orders` request body bővítése: opcionális `customer_uid`, `guest_count`.
  - Új vendég létrehozása `service_crm`-ben, ha `customer_uid` nincs.
  - Létező vendég ellenőrzése.
- **Elfogadás:** Integrációs teszt: új vendég, meglévő vendég, nem létező vendég (4xx hiba) esetei.

### A3 – Fogások (course) és jegyzet (notes) végigvezetése [B] [PÁRHUZAMOS]
- **Leírás:** `order_items.course`, `order_items.notes`, `orders.notes` funkcionális használata.
- **Feladatok:**
  - API szinten a mezők felvétele/ellenőrzése a create/update order endpointokban.
  - KDS payloadban is szerepeljen a `course` + `notes`.
  - Modell validáció: csak előre definiált `course` értékek.
- **Elfogadás:** Unit tesztek: `course`/`notes` mezők roundtrip (API → DB → API).

### A4 – Kedvezmény modell (discount_details) implementálása [B] [PÁRHUZAMOS]
- **Leírás:** Rugalmas kedvezmény JSONB (`order_items.discount_details`, rendelés-szintű kedvezmény).
- **Feladatok:**
  - Struktúra: `{ "type": "percentage|fixed|coupon|owner", "value": 10, ... }`.
  - Végpontok: `POST /orders/{id}/apply-discount`, `PATCH /orders/{id}/items/{itemId}/discount`.
  - RBAC: csak meghatározott role adhat kedvezményt.
- **Elfogadás:** Unit teszt: korrekt nettó/bruttó számítás; Audit log.

### A5 – Fizetési API + split fizetés [B]
- **Leírás:** Fizetési modell véglegesítése, több fizetési mód kombinációjával.
- **Feladatok:**
  - `payments` tábla: `order_id`, `method`, `amount`, `currency`, `timestamp`, `user_id`.
  - Endpointok: `GET /payments/methods`, `POST /orders/{id}/payments`.
- **Elfogadás:** Integrációs teszt: 100% KP, részben SZÉP + KP, túlfizetés (hiba).

### A6 – Számlázz.hu integráció (alapszint) [B]
- **Leírás:** Számla generálás fizetés után, Számlázz.hu API-val.
- **Feladatok:**
  - Konfiguráció: API kulcs, számlatömb.
  - Endpoint: `POST /integrations/szamlazz_hu/create-invoice`.
- **Elfogadás:** Sandbox környezetben számla létrehozása működik; Hibakezelés logolva.

### A7 – NTAK trigger + készletcsökkentés event [B]
- **Leírás:** Order lezárásakor NTAK adat generálás + készletcsökkentés event alapon.
- **Feladatok:**
  - `PATCH /orders/{id}/status/close`: fizetés ellenőrzése, NTAK payload (`orders.ntak_data`), pub/sub esemény (`order.closed`).
  - `service_inventory` subscriber: `order.closed` esemény alapján készletcsökkentés.
- **Elfogadás:** Integrációs teszt: order close → inventory `current_stock` változik.

### A8 – Cash drawer + daily closure API [B]
- **Leírás:** Készpénzmozgások és műszakzárás API-k.
- **Feladatok:**
  - `cash_movements` CRUD: `POST /cash-drawer/deposit|withdraw`.
  - `daily_closures`: `POST /daily-closures` (összesítő).
- **Elfogadás:** Integrációs teszt: napi zárás után új zárás nem indítható.

### A9 – Vendégtér UI (asztaltérkép) [F] [PÁRHUZAMOS A1–A3-mal]
- **Leírás:** React view szekciónként, asztalok állapotával.
- **Feladatok:**
  - UI komponens: `TableMapView` (szekcióválasztó, asztalok státusz szerint).
  - Műveletek: asztal megnyitása, áthelyezés, merge/split.
- **Elfogadás:** E2E: asztalnyitás → rendelés view-ra navigál.

### A10 – Rendelésfelvétel UI [F]
- **Leírás:** Termékek, kategóriák, fogások, jegyzetek UI.
- **Feladatok:**
  - `OrderScreen`: termékkategóriák, `course` választó, `item notes`, allergén jelölés.
  - Vendégszám / vendégkeresés integráció (CRM autocomplete).
- **Elfogadás:** E2E: beülős rendelés rögzíthető, KDS-re eljut.

### A11 – Fizetési UI + kedvezmény UI [F]
- **Leírás:** Fizetési modal/képernyő split paymenttel, kedvezményekkel, számlanyomtató gombbal.
- **Feladatok:**
  - Fizetés komponens: fizetési módok, több sor hozzáadása.
  - Kedvezmény UI: előre definiált + ad-hoc.
  - Gombok: Számla (Számlázz.hu) + státusz jelző, NTAK státusz.
- **Elfogadás:** E2E: rendelés lezárás + fizetés → backend hívás megtörténik.

### A12 – Teszt suite – Vendégtér + Kassza [T]
- **Leírás:** Egységes tesztelés az A-szálra.
- **Feladatok:**
  - Pytest: order lifecycle, discount, inventory.
  - E2E (Playwright/Cypress): teljes “asztaltól számláig” flow.
- **Elfogadás:** CI-ben külön `test_pos_onprem` job zöld.

---

## B. EPIC – Konyha/KDS + Kiszállítás

### B1 – KDS backend modell (station, kds_status, ordering) [B]
- **Feladatok:** `order_items` mezők: `kds_station`, `kds_status`. Endpointok: `GET /kds/items`, `PATCH /kds/items/{itemId}/status`.

### B2 – KDS UI [F]
- **Feladatok:** `KdsBoard` komponens: station szűrő, tile-ok rendelésenként, színkódok.

### B3 – Logistics: zónák, szállítási díj, ígért idő [B]
- **Feladatok:** `delivery_zones` CRUD. `GET /zones/by-address`.

### B4 – Futárok + rendelés-hozzárendelés [B]
- **Feladatok:** `couriers` CRUD. `POST /orders/{id}/assign-courier`.

### B5 – Operátor UI (Delivery / Rendezvény) [F]
- **Feladatok:** Operátor view: vendégkeresés, rendelés felvétel, státusz kezelés.

### B6 – Rendeléstípus váltás (átültetés) szabályok [B]
- **Feladatok:** `PATCH /orders/{id}/change-type` + validáció.

### B7 – KDS + Delivery teszt suite [T]
- **Feladatok:** Backend és E2E tesztek a KDS + delivery flow-ra.

---

## C. EPIC – Back-office + CRM + Riportok

### C1 – OSA integráció – bejövő számlák alap [B]
- **Feladatok:** `GET /inventory/incoming-invoices/fetch-from-osa`.

### C2 – Számlák kiegyenlítése (settlement) [B]
- **Feladatok:** `POST /inventory/incoming-invoices/{id}/settle`.

### C3 – Selejt + leltár API-k [B]
- **Feladatok:** `waste_logs` CRUD. `POST /inventory/stocktaking`.

### C4 – Back-office UI – számlák, leltár, selejt [F]
- **Feladatok:** Admin felület a C1–C3 funkciókra.

### C5 – Eszköz- és járműnyilvántartás backend [B]
- **Feladatok:** `assets`, `vehicles` CRUD + figyelmeztetések.

### C6 – Eszköz- és jármű UI [F]
- **Feladatok:** Admin nézet eszközök/járművek kezelésére.

### C7 – CRM: vendégtörzs + kupon backend [B]
- **Feladatok:** `customers`, `coupons` CRUD. `POST /coupons/validate`.

### C8 – CRM / kupon UI [F]
- **Feladatok:** CRM és kuponkezelő UI. Kupon beváltás a kasszán.

### C9 – Riport backend [B]
- **Feladatok:** `GET /reports/sales`, `GET /reports/consumption`, `GET /reports/courier-performance`.

### C10 – Riport UI / vezetői dashboard [F]
- **Feladatok:** Dashboard a főbb riportoknak.

### C11 – Back-office + CRM + riport teszt suite [T]
- **Feladatok:** Teljes körű tesztek a C-epic-re.

---

## D. Cross-cutting / infra / CI

### D1 – CI pipeline bővítés epicalapú jobokra [X]
- **Feladatok:** GitHub Actions workflow-k: `test_pos_onprem`, `test_kds_delivery`, `test_backoffice_crm_reports`.

### D2 – LLM-alapú minőségellenőrző (Vertex Studio evaluator) [X]
- **Feladatok:** Vertex Studio Evaluator pipeline kritikus API-kra.

### D3 – Audit logging egységesítése [X]
- **Feladatok:** Egységes audit middleware / helper minden fontos üzleti eseményre.
