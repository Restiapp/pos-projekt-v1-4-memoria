> **ARCHIVED SKILL**
> Az aktualis Skill & Guideline fajlokat a `docs/skills/` mappaban talalod.
> Fo specifikacio: `docs/spec/SYSTEM_MASTER_SPEC_V1.md`

# Claude Skill: Modul 4 - Számlázás és Fizetés

**Cél:** Dinamikus fizetési módok kezelése (SZÉP kártyák) és számla felosztása.

**Releváns Adatbázis Sémák:** `orders`, `order_items`, `payments`, `seats`.

**Releváns API Végpontok:** `/orders/{id}/payments`, `/orders/{id}/split-check`, `/orders/{id}/status/close`.

## Üzleti Logika:

1. **Többféle Fizetési Mód:** Egy rendelésnél több fizetési mód is rögzíthető (pl. részben SZÉP kártya, részben készpénz).
2. **Számla Felosztása:** A `/orders/{id}/split-check` végpont a `seats` alapján előnézetet ad, hogy melyik személy mennyit fizet.
3. **Rendelés Lezárása:** A `/orders/{id}/status/close` végpont lezárja a rendelést, ami kiváltja az NTAK adatszolgáltatást és a készletcsökkentést.

**Releváns Könyvtárak:** FastAPI, PostgreSQL (psycopg2).
