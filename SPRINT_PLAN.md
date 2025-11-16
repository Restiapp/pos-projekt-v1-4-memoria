# 48 Órás Hiperagresszív Sprint Terv

A feladatok a Claude Skill könyvtárra és a többi generált dokumentumra hivatkoznak.

## 1. Nap: Alapok és Központi Logika (Óra: 0-24)

**Infrastruktúra és Setup (Párhuzamosan végezhető)**

  * [ ] [Infra] Hozd létre a GitHub repozitóriumot a FILE_STRUCTURE.txt alapján. (Ref: FILE_STRUCTURE.txt)
  * [ ] [Infra] Állítsd be a PostgreSQL adatbázist és futtasd le a kezdeti sémát. (Ref: DATABASE_SCHEMA.md)
  * [ ] [Infra] Hozd létre a GCS bucket-ot a képek számára. (Ref: ARCHITECTURE.md)
  * [ ] [Frontend] Inicializáld a React (Vite) projektet és hozd létre az alap navigációt.

**Backend - Modul 0 (Menü)**

  * [ ] [M0] Implementáld a /products és /categories CRUD végpontokat a Terméktörzs szolgáltatásban. (Ref: skill-module-0-menu.md)
  * [ ] [M0] Tervezd meg és implementáld a /modifier-groups és a kapcsolódó /modifiers végpontokat. (Ref: skill-module-0-menu.md)
  * [ ] [M0] Hozd létre a GCS Signed URL generáló logikát a képfeltöltéshez. (Ref: ARCHITECTURE.md)
  * [ ] [M0] Írd meg a Cloud Function-t a képek átméretezéséhez Pillow-val. (Ref: ARCHITECTURE.md)

**Backend - Modul 1 (Rendelések)**

  * [ ] [M1] Implementáld az új rendelés létrehozását (POST /orders) és a rendelés lekérdezését (GET /orders/{id}). (Ref: skill-module-1-orders.md)
  * [ ] [M1] Fejleszd ki a tétel hozzáadása (POST /orders/{id}/items) logikát, beleértve a `selected_modifiers` JSON mentését. (Ref: skill-module-1-orders.md)
  * [ ] [M2] Hozd létre az asztal (/tables) és személy (/seats) alapvető adatmodelljét és végpontjait. (Ref: DATABASE_SCHEMA.md)

**Frontend**

  * [ ] [FE] Hozz létre egy egyszerű terméklista komponenst, ami a /products végpontról tölt be adatokat.
  * [ ] [FE] Készíts egy "Új Rendelés" oldalt, ami lehetővé teszi termékek hozzáadását egy kosárhoz.

## 2. Nap: Funkciók és Integrációk (Óra: 24-48)

**Backend - Kritikus Üzleti Logika**

  * [ ] [M1] Implementáld az NTAK ÁFA-váltás logikáját a PATCH /orders/{id}/status/set-vat-to-local végponton. (Ref: skill-module-1-orders.md)
  * [ ] [M4] Implementáld a rendelés lezárását és a fizetések rögzítését (POST /orders/{id}/payments). (Ref: skill-module-4-billing.md)
  * [ ] [M8] A rendelés lezárási eseményre triggereld az NTAK "Rendelésösszesítő" adatcsomag generálását. (Dummy küldés). (Ref: skill-module-8-ntak.md)
  * [ ] [M5] A rendelés lezárási eseményre triggereld a perpetuális készletcsökkentést a receptek alapján. (Ref: skill-module-5-inventory.md)

**Backend - AI és Kiegészítő Modulok**

  * [ ] [M0] Integráld a Vertex AI Translation API hívást a termék mentési folyamatba. (Ref: skill-module-0-menu.md)
  * [ ] [M5] Állítsd be a /inventory/invoices/upload végpontot, ami a feltöltött fájlt továbbítja a Document AI felé. (Ref: skill-module-5-inventory.md)
  * [ ] [M3] Hozz létre egy egyszerű /kds/items végpontot, ami a nyitott rendelési tételeket adja vissza. (Ref: skill-module-3-kds.md)
  * [ ] [M6] Implementáld az alapvető jogosultságkezelési middleware-t az API Gateway-en vagy a szolgáltatásokban. (Ref: skill-module-6-employees.md)

**Frontend**

  * [ ] [FE] Fejleszd ki a vizuális Asztaltérkép nézetet, ami az /tables végpontról töltődik.
  * [ ] [FE] Hozz létre egy egyszerű Konyhai Kijelző (KDS) felületet.
  * [ ] [FE] Implementáld a fizetési képernyőt, ahol a számla lezárható.
  * [ ] [FE] Teszteld az offline működést egy egyszerű rendelés felvételével kapcsolat nélkül (PWA/IndexedDB koncepció).

**Sprint Zárás**

  * [ ] [Mindenki] Kódreview, tesztelés és a generált dokumentációk frissítése a tapasztalatok alapján.
  * [ ] [Mindenki] Demo előkészítése.
