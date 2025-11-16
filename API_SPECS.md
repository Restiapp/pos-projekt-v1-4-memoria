# Magas Szintű API Specifikáció (OpenAPI 3.1 Kivonat)

Ez a specifikáció a főbb REST API végpontokat vázolja fel.

```yaml
openapi: 3.1.0
info:
  title: Éttermi POS Rendszer API
  version: 1.0.0

paths:
  # Module 0: Terméktörzs és Menü
  /products:
    get:
      summary: Termékek listázása
    post:
      summary: Új termék létrehozása
  /products/{id}:
    get:
      summary: Egy termék adatainak lekérése
    put:
      summary: Termék frissítése
  /categories:
    get:
      summary: Kategóriák listázása
  /modifier-groups:
    get:
      summary: Módosító csoportok listázása
    post:
      summary: Új módosító csoport létrehozása

  # Module 1 & 2: Rendeléskezelés és Asztalok
  /orders:
    post:
      summary: Új rendelés létrehozása
    get:
      summary: Aktív rendelések listázása (szűrhető nézet szerint)
  /orders/{id}:
    get:
      summary: Egy rendelés részleteinek lekérése
  /orders/{id}/items:
    post:
      summary: Tétel hozzáadása rendeléshez
  /orders/{id}/status/set-vat-to-local:
    patch:
      summary: NTAK-kompatibilis ÁFA váltás helybeni fogyasztásra (5%)
  /orders/{id}/status/close:
    patch:
      summary: Rendelés lezárása (kiváltja a fizetést, NTAK küldést)
  /tables:
    get:
      summary: Asztaltérkép lekérése

  # Module 3: Konyhai Kijelző (KDS)
  /kds/items:
    get:
      summary: KDS tételek lekérése állomás szerint (pl. ?station=Konyha)
  /kds/items/{itemId}/status:
    patch:
      summary: KDS tétel státuszának frissítése (pl. 'KÉSZÜL', 'KÉSZ')

  # Module 4: Számlázás és Fizetés
  /orders/{id}/payments:
    post:
      summary: Fizetés rögzítése a rendeléshez
  /orders/{id}/split-check:
    get:
      summary: Számla felosztásának előnézete személyek (seat) szerint

  # Module 5: Készletkezelés
  /inventory/items:
    get:
      summary: Készletcikkek listázása
  /inventory/invoices/upload:
    post:
      summary: Szállítói számla feltöltése OCR feldolgozásra
  /inventory/daily-counts:
    post:
      summary: Napi leltár rögzítése

  # Module 7: CRM és Integrációk
  /customers:
    get:
      summary: Törzsvevők keresése
  /customers/{id}/credit:
    post:
      summary: Hitelkeret módosítása
  /external-api/orders:
    post:
      summary: Külső partner rendelésének fogadása

  # Module 8: Adminisztráció és Analitika
  /reports/sales:
    get:
      summary: Eladási riport generálása (időszak, csatorna szerint)
  /ntak/send-summary/{orderId}:
    post:
      summary: Manuális NTAK Rendelésösszesítő küldés
  /haccp/logs:
    post:
      summary: Új HACCP naplóbejegyzés (pl. hűtőhőmérséklet)
```
