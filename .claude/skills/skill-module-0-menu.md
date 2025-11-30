> **ARCHIVED SKILL**
> Az aktualis Skill & Guideline fajlokat a `docs/skills/` mappaban talalod.
> Fo specifikacio: `docs/spec/SYSTEM_MASTER_SPEC_V1.md`

# Claude Skill: Modul 0 - Terméktörzs és Menü Konfigurátor (ARCHIVED)

**Cél:** A rendszer központi termék- és menü adatbázisának kezelése, beleértve a komplex módosítókat, többnyelvűséget, értékesítési csatornákat és képkezelést.

**Releváns Adatbázis Sémák:** `products`, `categories`, `image_assets`, `modifier_groups`, `modifiers`, `product_modifier_group_associations`, `channel_visibility`.

**Releváns API Végpontok:** `/products`, `/products/{id}`, `/categories`, `/modifier-groups`.

## Üzleti Logika:

1. **Komplex Módosítók:**
    * A `modifier_groups` tábla `selection_type`, `min_selection` és `max_selection` oszlopai definiálják a szabályokat.
    * `SINGLE_CHOICE_REQUIRED`: Pl. Zsemle típus (min:1, max:1).
    * `MULTIPLE_CHOICE_OPTIONAL`: Pl. Extra feltétek (min:0, max:8).
    * A `modifiers` tábla `price_modifier` oszlopa kezeli a felárakat.
2. **Értékesítési Csatornák:** A `channel_visibility` tábla felülírhatja egy termék láthatóságát és árát csatornánként (Pult, Kiszállítás, Helybeni).
3. **AI Fordítás:** Új terméknév/leírás mentésekor aszinkron hívás a Vertex AI Translation LLM API felé, az eredményeket a `products.translations` JSONB oszlopba mentve.
4. **Képkezelés:** A frontend GCS Signed URL-t kap a feltöltéshez. A feltöltés Cloud Function-t triggerel, ami Pillow segítségével átméretez, és a CDN-en keresztül szolgáltatja ki a képeket.

**Releváns Könyvtárak:** FastAPI, PostgreSQL (psycopg2), Pillow.
