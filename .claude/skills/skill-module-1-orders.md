# Claude Skill: Modul 1 - Központi Rendeléskezelés

**Cél:** A bejövő rendelések fogadása, státuszkezelése és a speciális üzleti szabályok (pl. NTAK ÁFA váltás) alkalmazása.

**Releváns Adatbázis Sémák:** `orders`, `order_items`, `tables`, `seats`.

**Releváns API Végpontok:** `/orders`, `/orders/{id}`, `/orders/{id}/items`, `/orders/{id}/status/set-vat-to-local`.

## Üzleti Logika:

1. **Többcsatornás Felvétel:** Az `orders.order_type` mező ('Helyben', 'Elvitel', 'Kiszállítás', 'Személyzet') alapján a UI különböző nézeteket jeleníthet meg.
2. **NTAK-kompatibilis ÁFA Váltás:**
    * **Trigger:** `/orders/{id}/status/set-vat-to-local` végpont hívása.
    * **Feltétel:** Csak `NYITOTT` státuszú rendeléseken hajtható végre.
    * **Akció:** Az `orders.final_vat_rate` mezőt `27.00`-ról `5.00`-ra módosítja. A rendelés lezárásakor ez a végleges ÁFA kulcs kerül felhasználásra az NTAK adatszolgáltatásban.

**Releváns Könyvtárak:** FastAPI, PostgreSQL (psycopg2).
