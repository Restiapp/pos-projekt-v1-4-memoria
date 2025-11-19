# GitHub Actions CI/CD Documentation

## CI Pipeline Bővítés - Epic-based Testing

Ez a mappa tartalmazza a POS projekt GitHub Actions workflow-jait.

### Workflow Fájlok

#### `ci-epic-tests.yml` - Epic-alapú Tesztelés

Ez a workflow három párhuzamos job-ban futtatja a teszteket, üzleti logika (epic) szerint csoportosítva:

##### Job 1: `test_pos_onprem` (Epic A)
**Cél:** POS OnPrem funkciók tesztelése

**Lefedett szolgáltatások:**
- `service_orders` - Rendeléskezelés, asztalok, NTAK adatküldés
- `service_menu` - Terméktörzs, kategóriák, receptek

**Üzleti logika:**
- Vendégtér működése
- Rendelésfelvétel és feldolgozás
- Menükezelés és termékek

##### Job 2: `test_kds_delivery` (Epic B)
**Cél:** Kiszállítási ökoszisztéma tesztelése

**Lefedett szolgáltatások:**
- `service_logistics` - Kiszállítási zónák, futárok, tracking

**Üzleti logika:**
- Futárkezelés
- Kiszállítási zónák és díjszámítás
- Rendelés tracking

##### Job 3: `test_backoffice_crm_reports` (Epic C)
**Cél:** Háttér műveletek, CRM és riportok tesztelése

**Lefedett szolgáltatások:**
- `service_admin` - Pénzügyek, munkatársak, Számlázz.hu integráció
- `service_crm` - Vendégkezelés, hűségprogram, kuponok
- `service_inventory` - Raktárkezelés, receptek, beszállítók

**Üzleti logika:**
- Adminisztrációs funkciók
- Ügyfélkapcsolatok kezelése
- Készletnyilvántartás

### Automatikus Futtatás

A workflow automatikusan lefut:
- **Push eseménynél** a következő branch-ekre:
  - `main`
  - `develop`
  - `claude/**` (Claude AI által generált branch-ek)
  - `feature/**` (feature branch-ek)

- **Pull Request eseménynél** a következő target branch-ekre:
  - `main`
  - `develop`

### Job Kimenet

Minden job futása után egy összesítő üzenet jelenik meg:
```
✅ Epic A (POS OnPrem) tests completed
   - service_orders: Order management, tables, NTAK
   - service_menu: Products, categories, recipes
```

### Végső Összesítés

A `test_summary` job minden futás végén összesíti az eredményeket:
```
================================================
CI Pipeline - Epic-based Test Results
================================================

Epic A (POS OnPrem):           success
Epic B (KDS Delivery):         success
Epic C (BackOffice/CRM):       success

================================================
✅ All epic tests passed successfully!
```

### Előnyök

1. **Párhuzamos futás**: A három epic tesztjei egyszerre futnak, csökkentve a CI időt
2. **Üzleti kontextus**: Egyértelmű, hogy melyik üzleti funkció tesztje sikeres/sikertelen
3. **Izolált hibák**: Ha egy epic tesztjei elbuknak, a többi még mindig lefuthat
4. **Skálázhatóság**: Könnyen bővíthető további epic-ekkel

### Technikai Részletek

- **Python verzió**: 3.11
- **PostgreSQL verzió**: 16
- **Test framework**: pytest
- **Környezeti változók**:
  - `DATABASE_URL`: PostgreSQL test adatbázis
  - `JWT_SECRET_KEY`: Test JWT secret
  - `TESTING`: true (test mód jelzése)

### Tesztek Fejlesztése

Minden service `tests/` mappájában találhatók a tesztek. Jelenleg alapvető health check tesztek vannak implementálva:

- `test_health.py` - Health endpoint és service metadata tesztek

**Következő lépések a tesztek bővítéséhez:**
1. API endpoint tesztek (POST, PUT, DELETE műveletek)
2. Üzleti logika tesztek (pl. rendelés életciklus)
3. Integrácios tesztek (service-to-service kommunikáció)
4. E2E tesztek (teljes workflow-k)

### Hibakeresés

Ha egy job elbukik:
1. Nézd meg a job részletes logját a GitHub Actions UI-ban
2. Ellenőrizd a szolgáltatás health endpoint-ját
3. Ellenőrizd a PostgreSQL kapcsolatot
4. Futtasd le lokálisan: `cd backend/service_xyz && pytest tests/ -v`

### Kapcsolódó Dokumentumok

- [SPRINT_PLAN.md](../SPRINT_PLAN.md) - Teljes projekt terv és fázisok
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Mikroszolgáltatás architektúra
- [DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md) - Adatbázis séma

---

**Létrehozva:** 2025-11-19
**Feladat:** D1 - CI Pipeline Bővítés (Epic-based jobs)
**Verzió:** 1.0
