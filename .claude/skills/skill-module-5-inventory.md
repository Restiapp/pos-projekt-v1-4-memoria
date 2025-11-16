# Claude Skill: Modul 5 - Készletkezelés

**Cél:** A készletmozgások követése a kettős raktárkezelési modell alapján, és a beszerzések automatizálása.

**Releváns Adatbázis Sémák:** `inventory_items`, `recipes`, `supplier_invoices`, `daily_inventory_sheets`, `daily_inventory_sheet_items`, `daily_inventory_counts`.

**Releváns API Végpontok:** `/inventory/items`, `/inventory/invoices/upload`, `/inventory/daily-counts`.

## Üzleti Logika:

1. **Kettős Raktárkezelés:**
    * **A) Perpetuális (automatikus) raktár:**
        * Amikor egy `orders` státusza `LEZART`-ra változik, a rendszer eseményt generál.
        * Egy listener szolgáltatás lekérdezi az `order_items` táblából az eladott termékeket.
        * A `recipes` tábla alapján megkeresi a termékekhez tartozó alapanyagokat (`inventory_items`).
        * Csökkenti az `inventory_items.current_stock_perpetual` értékét a receptben meghatározott mennyiséggel.
    * **B) Napi (manuális) karton:**
        * A felhasználó definiál egy leltárívet (`daily_inventory_sheets`).
        * A `/inventory/daily-counts` végponton keresztül rögzíti a fizikai darabszámot a `daily_inventory_counts` tábla `counts` JSONB oszlopába. Ez a két rendszer párhuzamosan fut, összehasonlítási alapot biztosítva.
2. **AI Számla Beolvasás (OCR):**
    * `/inventory/invoices/upload` végpontra feltöltött számlakép (PDF/JPG) a Google Document AI (Invoice Parser) szolgáltatásnak kerül továbbításra.
    * A Document AI strukturált JSON-t ad vissza a tételekről, árakról.
    * A rendszer ezt a JSON-t feldolgozza és automatikus bevételezési javaslatot készít, amit a felhasználó hagy jóvá.

**Releváns Könyvtárak:** FastAPI, PostgreSQL (psycopg2), Google Document AI Client Library.
