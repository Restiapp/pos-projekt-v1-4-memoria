# Claude Skill: Modul 6 - Munkatárs és Jogosultságkezelés

**Cél:** Finomhangolható szerepkör-alapú jogosultságkezelés.

**Releváns Adatbázis Sémák:** `employees`, `roles`, `permissions`, `role_permissions`, `employee_roles`.

**Releváns API Végpontok:** `/employees`, `/roles`, `/permissions`.

## Üzleti Logika:

1. **Role-Based Access Control (RBAC):** Minden alkalmazotthoz szerepköröket (`roles`) rendelünk (pl. 'Admin', 'Pultos', 'Szakács').
2. **Jogosultságok:** Szerepkörökhöz jogosultságokat (`permissions`) társítunk (pl. 'CAN_OPEN_CASH_DRAWER', 'CAN_EDIT_PRODUCTS').
3. **Ellenőrzés:** A backend minden védett végpont hívása előtt ellenőrzi, hogy a bejelentkezett alkalmazott rendelkezik-e a szükséges jogosultsággal.

**Megjegyzés:** A munkaidő-nyilvántartás és bérszámfejtés NEM része ennek a modulnak, azok külső rendszerekben kezelendők.

**Releváns Könyvtárak:** FastAPI, PostgreSQL (psycopg2).
