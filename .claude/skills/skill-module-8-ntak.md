# Claude Skill: Modul 8 - Adminisztráció és NTAK

**Cél:** A kötelező NTAK adatszolgáltatás biztosítása és a belső adminisztratív funkciók (HACCP, riportok) kezelése.

**Releváns Adatbázis Sémák:** `orders`, `payments` (adatszolgáltatáshoz), `haccp_logs` (feltételezve, hogy létezik, bár a sémában nem volt explicit, de a funkciókban igen).

**Releváns API Végpontok:** `/ntak/send-summary/{orderId}`, `/reports/sales`, `/haccp/logs`.

## Üzleti Logika:

1. **NTAK Adatszolgáltatás:**
    * **"Rendelésösszesítő":**
        * **Trigger:** Egy rendelés lezárása (`/orders/{id}/status/close` hívásakor, a fizetés sikeres rögzítése után).
        * **Folyamat:** A rendszer összegyűjti a rendelés adatait (tételek, fizetési mód, végleges ÁFA a `final_vat_rate` alapján), létrehozza az NTAK által megkövetelt formátumú adatcsomagot, és elküldi az NTAK felé. A küldés eredményét az `orders.ntak_data` JSONB oszlopban tárolja.
    * **"Sztornó":**
        * **Trigger:** Lezárt rendelés sztornózása.
        * **Folyamat:** Hasonlóan a rendelésösszesítőhöz, egy speciális sztornó üzenetet generál és küld az NTAK felé.
2. **Offline Mód:** A frontend (pl. PWA) egy belső adatbázisban (pl. IndexedDB) tárolja a rendeléseket internetkapcsolat nélkül. Amint a kapcsolat helyreáll, egy szinkronizációs szolgáltatás feltölti a pufferelt adatokat a központi szerverre.

**Releváns Könyvtárak:** FastAPI, PostgreSQL (psycopg2), Requests/HTTPX (NTAK API hívásokhoz).
