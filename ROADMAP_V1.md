# RESTI POS – FEJLESZTÉSI ROADMAP (v1)

## 🔵 FÁZIS 1 – ALAPRENDSZER + FUNKCIONÁLIS GERINC
*(A legfontosabb rendszerlogika: még UI nélkül is működnie kell)*

### 1. Terem- és asztalkezelő rendszer
*   **Teremstruktúra CRUD:** Helyiségek létrehozása, módosítása.
*   **Drag & Drop:** Asztalok vizuális elhelyezése a térképen.
*   **Státusz logika:** Szabad, Foglalt, Fizetés alatt, Takarítás.
*   **Konfiguráció:** Asztalszám, férőhely, dohányzó/nem dohányzó.
*   **Nézetek:** Külön nézet pincérnek (gyors), üzletvezetőnek (szerkesztő).

### 2. Rendelésindítás + Sorszámkezelő modul
*   **Sorszám:** Globális, egyedi sorszám generálás.
*   **Vendég:** Keresés (CRM) vagy 0-s anonim rendelés.
*   **Státusz:** Folyamatban / Átmozgatott / Fizetve.

### 3. Konyhai pályák (KDS) ALAP rendszer
*   **Pálya Modell:** "Hidegkonyha", "Melegkonyha", "Bárpult".
*   **Routing Logika:** Tétel -> Kategória -> Pálya hozzárendelés.
*   **Szétosztás:** Egy rendelés tételei szétmennek több pályára.
*   **KÉSZ státusz:** Pályánként külön kezelve.

### 4. Időfigyelő motor
*   **Timer:** Blokk létrehozásától ketyegő óra.
*   **Alerts:** Sárga/Piros időhatárok átlépése.

### 5. Fizetési modul BACKEND
*   **Módok:** Készpénz, Kártya, SZÉP, Átutalás.
*   **Kedvezmények:** Százalékos, Fix, Keret alapú.
*   **Zárás:** Fizetés -> Rendelés lezárása (Inventory trigger).
*   **ÁFA:** Helyben (5%) vs Elvitel (27%) automatikus váltás.

### 6. Számlázz.hu API integráció
*   **Valós Integráció:** Nem Mock.
*   **Adatok:** Automatikus kitöltés rendelésből.
*   **Státusz:** Számlázva -> Fizetett.

---

## 🔵 FÁZIS 2 – MŰKÖDÉSI MODULOK + UI
*(Vizuális, napi működés)*

### 7. KDS UI
*   Pályánkénti nézet, Drag & Drop sorrend, Sürgős jelölés.

### 8. Vendégtéri UI
*   Teremlista, Asztalnézet, Rendelésfelvétel (gyors), Státuszok.

### 9. Bárpult UI
*   Osztott nézet, Elvitel lista, Italos KDS.

### 10. VIP UI (Dispatcher)
*   VIP asztal, Futárra adás, Térképes nézet.

### 11. Kiszállítási Modul Frontend
*   Folyamat: Új -> Kész -> Futár -> Úton -> Leszállítva.
*   Zónaszerkesztő, Vidéki ETA.

### 12. Futár Modul
*   Zárások listázása, Km-óra rögzítés.

---

## 🔵 FÁZIS 3 – ZÁRÁSOK, REPORTING, ADMIN
*(Üzleti befejező rendszer)*

### 13. Stornó és Módosítás
*   Indoklás kötelező, Naplózás.

### 14. Kedvezmény Modul (Full)
*   Kategóriák, Kuponok, Ajándékkártyák.

### 15. Pontgyűjtés Modul
*   Számítás, Beváltás, Történet.

### 16. Zárások Modul
*   Egyéni, Front, Kiszállítás, Napi Összesített.
*   Bontások: ÁFA, Fizetési mód.

### 17. Admin Modul
*   Terem, Dolgozók, Menü, Jogosultságok.
