> **ARCHIVED SKILL**
> Az aktualis Skill & Guideline fajlokat a `docs/skills/` mappaban talalod.
> Fo specifikacio: `docs/spec/SYSTEM_MASTER_SPEC_V1.md`

# Claude Skill: Modul 2 - Asztalkezelés

**Cél:** Vizuális asztaltérkép kezelése és személyenkénti (seat-based) rendelésfelvétel.

**Releváns Adatbázis Sémák:** `tables`, `seats`, `orders`, `order_items`.

**Releváns API Végpontok:** `/tables`, `/tables/{id}/seats`, `/orders/{id}/items`.

## Üzleti Logika:

1. **Asztaltérkép:** Az asztalok pozíciója (`position_x`, `position_y`) alapján a frontend vizuálisan jeleníti meg az asztalokat.
2. **Személyenkénti Rendelés:** Egy asztalnál többen is ülhetnek. Minden `seat` egy személy. Az `order_items` tábla `seat_id` oszlopa kapcsolja a rendelési tételeket egy adott személyhez, lehetővé téve a számla személyenkénti felosztását.

**Releváns Könyvtárak:** FastAPI, PostgreSQL (psycopg2).
