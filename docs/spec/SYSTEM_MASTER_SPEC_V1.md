# SYSTEM MASTER SPEC V1 - RESTI POS

**Version:** 1.0
**Status:** CANONICAL / MASTER
**Last Updated:** 2025-11-30

> **EZ A FO SPECIFIKACIO!**
> Minden AI ugynok (Web Claude, Jules, VS Claude) eloszor ezt a dokumentumot olvassa el a fejlesztes elott.

---

## 1. Rendszer attekintes

A RESTI POS egy ettermi / bar / kiszallitasos kornyezetre tervezett, mikroszerviz alapu Point of Sale rendszer.

### 1.1 Fo modulok

| Modul | Leiras |
|-------|--------|
| **Floorplan** | Termek, asztalok definialasa, drag & drop szerkeszto |
| **Barpult** | Pultos vendegelleatas, ital KDS, elviteles |
| **Vendegter (Felszolgalo)** | Asztal kivalasztas, rendeles rogzites, hullamok kezelese |
| **VIP** | Kulonleges vendegterulet, "egy nagy asztal" modell |
| **Kiszallitas** | Delivery rendelesek, zonak, ETA |
| **Futarok** | Kurir hozzarendeles, utvonalak |
| **KDS palyak** | Konyha, Pizza, Menu, Bar kijelzok |
| **Fizetes** | ÁFA logika, szamlazz.hu, storni |
| **Zarasok** | Egyeni, reszegysegi, napi zaras |

### 1.2 Mikroszerviz architektura

Reszletes leiras: `docs/spec/ARCHITECTURE_TARGET_V1.md`

**Szolgaltatasok:**
- `service_menu` - Termekek, kategoriak, receptek
- `service_orders` - Rendelesek, asztalok, KDS, fizetesek
- `service_inventory` - Keszlet, mozgasok, hulladek
- `service_crm` - Vendegelek, hűsegpont, kampanyok
- `service_logistics` - Szallitas, zonak, futarok
- `service_admin` - RBAC, felhasznalok, penzugyi naplo

---

## 2. UI / UX alapelvek

Reszletes leiras: `docs/ui-ux/UI_UX_FOUNDATION.md`

### 2.1 Fo elvek
- **Gyorsan atlathato**: kritikus info 1-2 pillantasra
- **Keves kattintas**: max 2-3 interakcio
- **Ujj-barat**: min. 44x44 px gombok
- **Konzisztens**: ugyanaz az elem mindenhol ugyanugy nez ki
- **Hibabiztos**: confirm dialog vedelem fontos muveleteknél

### 2.2 Vizualis stilus
- **Dark POS theme**: sotet hatter (`#050B10`), neon akcentek
- **Resti-zold primary**: `#16A085`
- **Mantine UI library**: komponens rendszer

### 2.3 Hatter mintak (Background Patterns)
A termek es asztalok egyedi hattermintakkal rendelkezhetnek:
- CSS gradient mintak
- Max 1000 karakter a `background_image_url` mezőben

---

## 3. Floorplan & Termek

Reszletes leiras: `docs/spec/FLOORPLAN_DOMAIN_V1.md`

### 3.1 Adatmodellek
- **Room**: id, name, type, width, height, background_image_url
- **Table**: id, room_id, table_number, position_x/y, capacity, shape

### 3.2 Admin Floor Plan Editor
- Drag & drop asztal elhelyezes
- Szinek, mintak, atlatszosag
- Terem tipusok: INDOOR, BAR, TERRACE_SMOKING, TERRACE_NONSMOKING, VIP

### 3.3 Operator TableMap
- Asztalok statusz szinekkel
- Termek kozti valtas (tabok)

---

## 4. Barpult modul

### 4.1 Funkciok
- Pultos vendegek kezelese (sorban vagy baregysegben)
- Elviteles rendelesek rogzitese
- Ital-KDS nezet (jobb oldali panel)

### 4.2 KDS ital nezet kapcsolata
- Ticket kartyak
- Ido szin logika (sarga/piros)
- "Kesz" gomb → ticket archivalas

---

## 5. Vendegter / Felszolgalo modul

**FONTOS:** Reszletes, aktualis specifikacio: `docs/spec/GUEST_FLOOR_ORDERS_SPEC_V1.md`

### 5.1 Fo logika
1. Felszolgalo kivalaszt egy asztalt
2. Rogziti az osszes tetelt (ejenkent, teljes asztal)
3. Bekulddes elott → **kor kiosztas nezet** megnyilik

### 5.2 Kor / Hullam rendszer (PIROS / SARGA / JELOLETLEN)

> **FONTOS VALTOZAS:** Tobbe NEM hasznalunk fix "eloétel / foétel / desszert" kategoria alapu koroket!

- **PIROS**: Elso kor (amit azonnal ker, pl. italok, bizonyos ételek)
- **SARGA**: Masodik kor (ha nagy asztal tobb hullamban eszik)
- **JELOLETLEN**: Minden, ami marad a vegere / egyben

**Nem az szamit, hogy az etel milyen kategoriaba tartozik, hanem hogy a felszolgalo melyik korben keri.**

### 5.3 Konyhai prioritas
A konyha a teteleket hullam szin alapjan priorizalja:
1. PIROS = elsőbbseg
2. SARGA = masodik hullam
3. JELOLETLEN = maradek

---

## 6. VIP es Kiszallitas

### 6.1 VIP modul
- Mint "egy nagy asztal" beülos vendegnek
- Kulonleges elszamolasi modok (INVOICE, HOUSE_ACCOUNT)
- Manager jovahagyas opcio (jovobeli feature)

### 6.2 Kiszallitas
- Zonak polygon adatokkal
- ETA szamitas zona alapjan
- ÁFA valtas logika: 5% (helyben fogyasztas) vs 27% (elvitel)

---

## 7. KDS palyak (Kitchen Display System)

### 7.1 Palyak
- **Konyha palya**: minden etel
- **Pizza palya**: pizza kategoria termekei
- **Menu palya**: aggregalt nezet koordinalashoz
- **Bar palya**: italok

### 7.2 Palya hozzarendeles
> **EGYSZERUSITES:** A palya-hozzarendeles a termek beallitasoknal tortenik (Admin → Menu/Product).
> A felszolgalo NEM dont palyarol rendeles kozben.

### 7.3 Allapot gepezet
1. **QUEUED**: Konyhara kuldve, meg nem kezdve
2. **IN_PROGRESS**: Kesiztes megkezdve
3. **READY**: Etel kész, talalas
4. **DELIVERED**: Felszolgalo/futar elvitte
5. **CANCELLED**: Stornozva

### 7.4 Surgoesseg es idozites
- Hullam szin = prioritas
- Ido alapu szinvaltas (sarga → piros)
- Konfiguralhato idohatarak (service_admin)

---

## 8. Fizetes & ÁFA logika

Reszletes leiras: `docs/spec/PAYMENT_FLOW_V1.md`

### 8.1 ÁFA kategoriak
- Helyben fogyasztas etel: **5%**
- Helyben fogyasztas ital: **27%**
- Elvitel: **27%** (altalaban)

### 8.2 Fizetesi modok
- CASH (keszpenz)
- CARD (kartya)
- SZEP kartya
- Ajandek kartya
- Huseg pontok
- INVOICE (szamla - VIP)
- HOUSE_ACCOUNT (haz szamla - VIP)

### 8.3 Storno szabalyok
- Manager PIN kotelezo
- Negativ fizetés record letrehozasa
- Ok megjelenitese audithoz

---

## 9. Zarasok rendszere

### 9.1 Zaras tipusok
- **Egyeni zaras**: Felszolgalok, pult, futar, dispatcher
- **Reszegysegi zaras**: Barpult, vendegter kulon
- **Napi zaras**: Teljes uzlet osszesites

### 9.2 Audit kovelmények
- Ki zarta le
- Mikor
- Kasszafiok egyenleg

---

## 10. Hivatkozasok / Forrasok

### Canonical dokumentumok (mindig ezeket olvasd!):
| Dokumentum | Cel |
|------------|-----|
| `docs/spec/SYSTEM_MASTER_SPEC_V1.md` | Fo rendszer specifikacio (EZ A FAJL) |
| `docs/spec/ARCHITECTURE_TARGET_V1.md` | Backend architektura |
| `docs/spec/FLOORPLAN_DOMAIN_V1.md` | Floorplan domain es API |
| `docs/spec/GUEST_FLOOR_ORDERS_SPEC_V1.md` | Vendegter / felszolgalo spec |
| `docs/spec/PAYMENT_FLOW_V1.md` | Fizetes es zaras flow |
| `docs/ui-ux/UI_UX_FOUNDATION.md` | Design es UI elvek |

### History / Log dokumentumok (csak referenciaként):
- `docs/audit/MASTER_AUDIT_REPORT.md` - Audit osszefoglalo
- `docs/roadmap/MASTER_ROADMAP.md` - Sprint roadmap
- `D3D4_FIXLOG.md` - Sprint D3+D4 javitasok logja

---

## 11. Verziotorténet

| Verzio | Datum | Valtozas |
|--------|-------|----------|
| 1.0 | 2025-11-30 | Elso kiadás - Master Spec osszefoglalo |

---

_END OF SYSTEM_MASTER_SPEC_V1.md_
