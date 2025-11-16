# Claude Skill: Modul 3 - Konyhai Kijelző Rendszer (KDS)

**Cél:** Valós időben jeleníti meg a rendelési tételeket a megfelelő konyhai állomásokon.

**Releváns Adatbázis Sémák:** `order_items` (különösen `kds_station` és `kds_status` oszlopok).

**Releváns API Végpontok:** `/kds/items`, `/kds/items/{itemId}/status`.

## Üzleti Logika:

1. **Állomás-alapú Szűrés:** A KDS képernyők lekérdezik a `/kds/items?station=Konyha` végpontot, így minden állomás csak a neki szánt tételeket látja.
2. **Státusz Frissítés:** A szakács a KDS felületen megváltoztatja egy tétel státuszát ('VÁRAKOZIK' -> 'KÉSZÜL' -> 'KÉSZ'), ami frissíti az `order_items.kds_status` mezőt.

**Releváns Könyvtárak:** FastAPI, PostgreSQL (psycopg2).
