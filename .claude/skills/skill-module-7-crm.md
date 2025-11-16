# Claude Skill: Modul 7 - CRM és Külső Integrációk

**Cél:** Törzsvevői hűségprogram és külső partnerek rendeléseinek kezelése.

**Releváns Adatbázis Sémák:** `customers`.

**Releváns API Végpontok:** `/customers`, `/customers/{id}/credit`, `/external-api/orders`.

## Üzleti Logika:

1. **Hűségpontok:** Minden vásárlás után pontokat lehet gyűjteni. A `customers.loyalty_points` mező tárolja a jelenlegi egyenleget.
2. **Törzsvevői Hitel:** A `customers.credit_balance` mező a jóváhagyott hitelkeretet tárolja, amit a rendelésekből le lehet vonni.
3. **Külső Integráció:** A `/external-api/orders` végpont egy authentikált API, ahol külső partnerek (pl. Wolt, Foodora) leadhatják rendeléseiket, amelyek automatikusan bekerülnek a rendszerbe.

**Releváns Könyvtárak:** FastAPI, PostgreSQL (psycopg2).
