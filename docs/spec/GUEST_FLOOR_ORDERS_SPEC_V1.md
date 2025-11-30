# GUEST FLOOR ORDERS SPEC V1 - Vendegter / Felszolgalo Modul

**Version:** 1.0
**Status:** CANONICAL / MASTER
**Last Updated:** 2025-11-30

> **FRISSITVE:** Ez a dokumentum az uj PIROS / SARGA / JELOLETLEN hullam-logikat tartalmazza.
> Tobbe **NEM** hasznalunk fix "eloétel / foétel / desszert" koroket a konyhai sorrendhez.

---

## 1. Attekintes

A Vendegter / Felszolgalo modul a POS rendszer egyik legfontosabb resze. A felszolgalok itt:
- Valasztanak asztalt
- Rogzitik a vendegelek rendeleset
- Beallitjak a hullam/kor prioritast
- Bekuldik a konyhara

---

## 2. Fo Logika

### 2.1 Rendeles rogzites folyamata

1. **Asztal kivalasztas**
   - Felszolgalo a TableMap-en kivalasztja az asztalt
   - Rendszer megjeleniti az asztal reszleteit

2. **Tetel rogzites**
   - Osszes tetel rogzitese (ejenkent VAGY teljes asztalra)
   - Mennyiseg, modifikatorok, megjegyzesek
   - Meg NEM tortenik prioritas beallitas

3. **Kor kiosztas nezet**
   - Mielott bekuldenenk a konyhara, megnyilik a kor kiosztas
   - Itt allitjuk be a PIROS / SARGA / JELOLETLEN hullamokat
   - Alapertelmezett: minden JELOLETLEN

4. **Bekuldés konyhara**
   - Teteleket a KDS rendszer fogadja
   - Prioritas szerinti sorolas

---

## 3. Hullam / Kor Rendszer

### 3.1 A harom hullam

| Hullam | Szin | Jelentes | Konyhai prioritas |
|--------|------|----------|-------------------|
| **PIROS** | Piros (#E74C3C) | Elso kor - azonnal | LEGMAGASABB |
| **SARGA** | Sarga (#F1C40F) | Masodik kor - raer | KOZEPES |
| **JELOLETLEN** | Feher/szurke | Maradek - vegere | NORMAL |

### 3.2 Fontos alapelv

> **"Nem az szamit, hogy az etel milyen kategoriaba tartozik, hanem hogy a felszolgalo melyik korben keri."**

Peldak:
- Ha a vendeg eloszor desszertet ker? → PIROS
- Ha a fo etelt kesobbi hullamban keri? → SARGA
- Ha az ital azonnal kell? → PIROS
- Ha mindent egyszerre kell? → minden JELOLETLEN

### 3.3 Regi rendszer vs Uj rendszer

| Regi (ELAVULT) | Uj (AKTUALIS) |
|----------------|---------------|
| course_tag = "eloétel" | wave = "FIRST" (PIROS) |
| course_tag = "foétel" | wave = "SECOND" (SARGA) |
| course_tag = "desszert" | wave = "DEFAULT" (JELOLETLEN) |
| Kategoria donti el | Felszolgalo donti el |

---

## 4. Backend API

### 4.1 OrderItem modell bovitese

```python
class OrderItem:
    # Meglevo mezok...

    # Hullam rendszer
    round_number = Column(Integer, nullable=True, default=1)
    wave = Column(String(20), default='DEFAULT')  # FIRST, SECOND, DEFAULT

    # Metadata (opcionales bovites)
    metadata_json = Column(JSONB, nullable=True)
```

### 4.2 Wave enum ertekek

```python
class OrderWave(str, Enum):
    FIRST = "FIRST"      # PIROS - elso kor
    SECOND = "SECOND"    # SARGA - masodik kor
    DEFAULT = "DEFAULT"  # JELOLETLEN - maradek
```

### 4.3 API endpoint-ok

**Rendeles letrehozas hullamokkal:**
```http
POST /api/v1/orders/{order_id}/items
Content-Type: application/json

{
  "product_id": 123,
  "quantity": 2,
  "wave": "FIRST",
  "modifiers": [...],
  "notes": "extra fuszeres"
}
```

**Hullamok modositasa (batch):**
```http
PATCH /api/v1/orders/{order_id}/waves
Content-Type: application/json

{
  "items": [
    { "item_id": 1, "wave": "FIRST" },
    { "item_id": 2, "wave": "SECOND" },
    { "item_id": 3, "wave": "DEFAULT" }
  ]
}
```

---

## 5. Frontend UI

### 5.1 Kor kiosztas nezet

A rendeles rogzitese utan, de a bekuldés elott megjelenik:

```
+-------------------------------------------+
|     KOR KIOSZTAS - Asztal A12             |
+-------------------------------------------+
|                                           |
|  [ PIROS - ELSO KOR ]                     |
|  +-- 2x Sör (drag-droppal ide)            |
|  +-- 1x Nachos                            |
|                                           |
|  [ SARGA - MASODIK KOR ]                  |
|  +-- 2x Pizza Margherita                  |
|                                           |
|  [ JELOLETLEN - MARADEK ]                 |
|  +-- 1x Tiramisu                          |
|  +-- 2x Espresso                          |
|                                           |
+-------------------------------------------+
|  [MÉGSE]              [KÜLDÉS KONYHÁRA]   |
+-------------------------------------------+
```

### 5.2 Interakciok

- **Drag & drop**: tetelek athuzhatoak hullamok kozott
- **Gyors gomb**: "Mind PIROS", "Mind JELOLETLEN"
- **Tap to toggle**: tetel koppintasra valt a kovetkezo hullamra

### 5.3 Szin kodok a UI-ban

```css
.wave-first {
  border-left: 4px solid #E74C3C;
  background: rgba(231, 76, 60, 0.1);
}
.wave-second {
  border-left: 4px solid #F1C40F;
  background: rgba(241, 196, 15, 0.1);
}
.wave-default {
  border-left: 4px solid #7F8C8D;
  background: transparent;
}
```

---

## 6. KDS (Kitchen Display) Integraciő

### 6.1 Ticket megjelenes

A KDS nezeten a teteleket a hullam szin alapjan priorizaljuk:

```
+-----------------------------+
|  TICKET #1042 - A12 asztal  |
+-----------------------------+
|  [PIROS] 2x Sör            |
|  [PIROS] 1x Nachos         |
+-----------------------------+
|  [SARGA] 2x Pizza          |
+-----------------------------+
|  1x Tiramisu               |
|  2x Espresso               |
+-----------------------------+
|  18:23 eltelt              |
|         [KESZ]             |
+-----------------------------+
```

### 6.2 Sorrendi logika

1. PIROS teteleket mindig elore vesszuk
2. Amig van PIROS, a SARGA nem indul
3. Ha minden PIROS kesz → SARGA indul
4. Vegul JELOLETLEN teteleket keszitjuk

---

## 7. Migracios megjegyzesek

### 7.1 Kodbeli course_tag mezo

A backendben tovaabbra is letezhet `course_tag` mezo, de:
- A logikai jelentese: **hullam** (pl. FIRST, SECOND, DEFAULT)
- NEM termekkategoria (eloétel, foétel stb.)
- Az uj rendszerben `wave` mezonek hivjuk

### 7.2 Adatbazis migracìo

```sql
-- Uj oszlop hozzaadasa
ALTER TABLE order_items ADD COLUMN wave VARCHAR(20) DEFAULT 'DEFAULT';

-- Regi course_tag migralasa (ha van)
UPDATE order_items SET wave =
  CASE
    WHEN course_tag = 'starter' THEN 'FIRST'
    WHEN course_tag = 'main' THEN 'SECOND'
    ELSE 'DEFAULT'
  END;
```

---

## 8. Tesztelesi checklist

- [ ] Uj rendeles rogzitese hullamok nelkul → minden DEFAULT
- [ ] Kor kiosztas nezet megnyitas
- [ ] Tetel athuzasa PIROS-ba
- [ ] Tetel athuzasa SARGA-ba
- [ ] Bekuldés konyhara
- [ ] KDS-en PIROS tetel elol van
- [ ] PIROS kesz jeloles utan SARGA jon elore
- [ ] Minden hullam kesz → ticket archiválva

---

## 9. Kapcsolodo dokumentumok

- `docs/spec/SYSTEM_MASTER_SPEC_V1.md` - Fo rendszer spec
- `docs/ui-ux/UI_UX_FOUNDATION.md` - UI/UX alapelvek
- `docs/spec/ARCHITECTURE_TARGET_V1.md` - Backend architektura

---

## 10. Verziótorténet

| Verzio | Datum | Valtozas |
|--------|-------|----------|
| 1.0 | 2025-11-30 | Elso kiadas - PIROS/SARGA/JELOLETLEN hullam logika |

---

_END OF GUEST_FLOOR_ORDERS_SPEC_V1.md_
