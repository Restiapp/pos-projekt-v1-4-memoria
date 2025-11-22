# UI_UX_FOUNDATION – RESTI POS
_Version: 1.0_

Ez a dokumentum a RESTI POS rendszer vizuális és interakciós alapját írja le.  
Célja, hogy a teljes fejlesztői csapat (frontend, backend, UX, QA) **közös nyelven** beszéljen a felületekről.

---

## 1. ALAPELVEK

### 1.1 Környezet
- Étterem, bár, konyha, futár-diszpécser környezet.
- Gyakran **félhomályos vendégtér** és **erős fényű konyha**.
- Érintős eszközök: tablet, nagy érintős monitor, esetenként laptop.

### 1.2 Fő célok
- **Gyorsan átlátható**: kritikus információ 1–2 pillantásra érthető legyen.
- **Kevés kattintás**: minden kulcsfeladat max. 2–3 interakcióból elérhető.
- **Ujj-barát**: gombok, interakciós zónák min. 44×44 px.
- **Konzisztens**: ugyanaz az elem mindenhol ugyanúgy néz ki és viselkedik.
- **Hibabiztos**: fontos műveleteket (fizetés, stornó) confirm-dialog védi.

### 1.3 Szerepkör-alapú UI

Minden nézet alapelve:
- **Bárpultos**: italok, pult, elviteles, ital-KDS.
- **Felszolgáló**: vendégtér, terasz, szeparé, fizetés.
- **Dispatcher**: VIP, kiszállítás, futárok, zónák.
- **Konyha / Pizza / Menü / Bár-KDS**: egyszerű, nagy ticketek, időzítéssel.
- **Admin**: beállítások, törzsadat, riportok.

Minden szerepkör **dedikált kezdőképernyővel** rendelkezik bejelentkezés után.

---

## 2. VIZUÁLIS STÍLUS

### 2.1 Színrendszer (dark POS theme)

> Hex kódok iránymutatóak, a UI designer finomíthatja, a logika maradjon.

**Alap háttér:**
- `#050B10` – nagyon sötét, kékes-fekete (app háttér).
- `#101821` – kártya háttér, felületi blokkok.

**Elsődleges akcent szín:**
- `#16A085` – „Resti-zöld” (primary gombok, kiemelések).

**Másodlagos akcent:**
- `#2980B9` – információs / neutrális akcent.

**Státusz színek:**
- Info: `#3498DB`
- Siker: `#2ECC71`
- Figyelmeztetés (sárga): `#F1C40F`
- Hiba / késés (piros): `#E74C3C`
- Inaktív / disabled: `#7F8C8D`

**Szöveg:**
- Fő szöveg: `#F5F7FA`
- Másodlagos: `#A0ACB8`
- Halvány jelölés / placeholder: `#6C7A89`

**Border / elválasztók:**
- Vékony border: `#1F2A33`

### 2.2 Tipográfia

Ajánlott: **Inter**, **Roboto**, vagy hasonló modern sans-serif.

- **Title XL (pl. asztalszám, sorszám)**  
  - 24–28 px, félkövér
- **Title L (oldal cím)**  
  - 20–22 px, félkövér
- **Body**  
  - 14–16 px, normál
- **Label / helper text**  
  - 12–14 px, medium/szürkés

Font weight:
- 400 (normal)
- 500–600 (kiemelések, címekhez)

### 2.3 Szegélyek és shadow

- Kártyák: `border-radius: 12–16px`
- Gombok: `border-radius: 8px`
- Shadow (kártyákhoz, modálokhoz):  
  `0 10px 25px rgba(0, 0, 0, 0.4)`

---

## 3. GLOBÁLIS LAYOUT

### 3.1 Felső menüsáv (Top Bar)

Minden fő nézet tetején jelenik meg.

**Tartalom:**
- Bal oldal:
  - App logó vagy „RESTI POS” felirat.
  - Aktuális nézet neve (pl. „Bárpult”, „Vendégtér”, „Konyha – Pizza pálya”).
- Közép:
  - Terem-választó / pálya-választó tabok (szerepkörtől függően).
- Jobb oldal:
  - Aktív felhasználó neve + szerepkör (pl. „Nóra – Felszolgáló”).
  - Idő (HH:MM).
  - Rendszer státusz ikonok (online/offline, printer státusz, Számlázz.hu kapcsolat).

**Stílus:**
- Magasság: ~64px.
- Háttér: sötét gradient (pl. `#050B10` → `#101821`).
- Bottom border: vékony vonal `#1F2A33`.

### 3.2 Oldalsó sáv (Sidebar) – főleg admin / dispatcher / nagy kijelző

- Bal oldali fix sáv: 72–80 px (desktop).
- Csak ikonok (tooltipekkel).
- Menü ikonok: Vendégtér, Bárpult, Konyha, Pizza, Menü, VIP, Kiszállítás, Zónák, Futárok, Jelentések, Beállítások.

**Tablet / kisebb kijelző:**
- A sidebar felülre költözhet, horizontális strip-ként.

### 3.3 Tartalom terület

- A fő tartalom egy vagy több **kártya**:
  - Kártyák között 16–24px margin.
  - Responsive grid: 1–2 oszlop (tablet), 2–4 oszlop (desktop).

---

## 4. KÖZÖS UI KOMPONENSEK

Ezeket **közös UI library-ből** kell felépíteni, pl. `frontend/src/components/ui/`.

### 4.1 Button

Variánsok:
- `primary` (Resti-zöld)
- `secondary` (kékes)
- `outline`
- `ghost` (ikon-gomb pl. KDS-ben)

Állapotok:
- default
- hover
- active
- disabled
- loading (spinner a szöveg előtt)

Méretek:
- `md` (alap): min. 44px magasság, 16–24 px padding.
- `lg` (KDS, POS fizetés gombok): 52–60 px magasság.

### 4.2 Input / Select / Textarea

- Egységes keret, label, placeholder stílus.
- Hibás állapot: piros border + error text.
- Kényelmes touch target (magas sorok).

### 4.3 Modal / Dialog / ConfirmDialog

- Hátteret halvány sötét overlay (scrim).
- Tartalom: középre igazított kártya, 400–600 px széles.
- Használat:
  - confirm (stornó, fizetés véglegesítés).
  - info (rendszer üzenetek).
  - form (pl. új futár, új jármű).

### 4.4 Toast Notification rendszer

- Jobb felső sarok, stack-elhető.
- Variánsok: success, error, warning, info.
- Minden fontos backend hiba / siker itt jelenjen meg, **nem alert()** ablakban.

### 4.5 Card, Badge, Chip

- Card: KDS ticketek, asztalok, futár kártyák.
- Badge: státusz jelölések (pl. „VIP”, „Kiszállítás”, „Asztal A12”).
- Chip: filterek, pl. „Sürgős”, „Vendégtér”, „Elvitel”.

### 4.6 Loading / Skeleton

- Skeleton komponens lista nézetekhez (táblázat sorok, kártyák helyett).
- Full-page loader: KDS, ha nincs adat.

---

## 5. SZEREPKÖRÖK – NÉZETEK

### 5.1 Bárpultos nézet

**Cél:** pultnál ülő vendégek, elviteles rendelések, ital-KDS egy nézetben.

**Layout (desktop/tablet):**
- Bal oldal (~60% szélesség):
  - Felső kártya: „Bárpult vendégek”
    - Listanézet:  
      - Sorszám (nagy)  
      - Név / „Anonim”  
      - Fogyasztás összege  
      - Státusz (ikon + szín)
      - CTA: „Fizetés”, „Részletek”
  - Alatta kártya: „Elviteles rendelések”
    - Lista:  
      - Sorszám  
      - Név  
      - Várható időpont  
      - Átmozgatás gomb (→ bárpult / asztal)

- Jobb oldal (~40%): **Ital-KDS**
  - Ticket-kártyák, érkezési sorrendben.
  - Kártya tartalma:
    - Sorszám nagy betűvel.
    - Asztal / vendégnév.
    - Itallisták.
    - Időzítő (elapsed time).
    - Sürgős jelölés (piros csík vagy badge).

**Interakciók:**
- Ticket drag & drop a sorrend módosítására.
- Kártyák sárgulnak / pirosodnak az idő logikája alapján.

### 5.2 Felszolgáló – Vendégtér / Terasz / Szeparé

**Felső sáv (Top tabs):**
- Vendégtér
- Terasz (Dohányzó)
- Terasz (Nem dohányzó)
- Szeparé
- Opcionális: „Összes asztal megjelenítése”

**Középső terület: asztaltérkép**

- Szabad elrendezés, `react-draggable` vagy grid alap.
- Asztal ikon formák:
  - kerek / négyzet / téglalap (típus alapján).
- Színek:
  - Zöld: szabad.
  - Kék: rendelés folyamatban.
  - Sárga: sok ideje van bent (pl. 25+ perc).
  - Piros: nagyon régóta bent (alert).
  - Szürke: inaktív / közelgő foglalás.

**Asztal kártya tartalma:**
- Fő: Asztalszám (pl. „A12”).
- Alatta: férőhely (pl. „4 fő”).
- Ha van aktív rendelés:
  - Sorszám.
  - Kis összeg (pl. „össz.: 12 450 Ft”).

**Kattintás asztalra:**
- Átvált a rendelés felületre (oldalon vagy jobb oldali panelben):
  - Vendég sorszám megadása / nullás gyűjtő.
  - Rendelés rögzítése (ételek, italok).
  - Sürgős tételek jelölése.

### 5.3 Dispatcher – VIP + Kiszállítás

**Két fő blokk egy képernyőn:**

- Bal oldal:
  - Felső kártya: **VIP Asztal**
    - Egy „VIP asztal” kártya (mint a pult), több vendég rendelésével.
  - Alatta kártya: **Kiszállításos rendelések**
    - Lista: sorszám, név, cím, összeg, ETA, zóna.

- Jobb oldal:
  - Térkép nézet:
    - Zónák polygonokkal.
    - Kiszállításra váró címek pin-ekkel.
    - Kijelölt futár útvonal jelöléséhez később.

**Interakciók:**
- Rendelés kiválasztása → futár hozzárendelése.
- Zóna információk megjelenítése (díj, minimum összeg, extra idő).

---

## 6. KONYHAI PÁLYÁK (KDS)

Külön bejelentkezéssel:
- Konyha pálya.
- Pizza pálya.
- Menü pálya.
- Bár (ital) pálya.

**Fő nézet:**
- Full screen, sötét háttér.
- Középen több oszlop:
  - Alap: érkezési sorrendben balról jobbra.
- Minden rendelés egy ticket-kártya.

**Ticket tartalom:**
- Nagy sorszám.
- Asztal vagy vendégnév (adminban váltható).
- Tétellista:
  - Sürgős tételek kiemelve (pl. piros szél / ikon).
- Időzítő (elapsed time).
- Státusz jelző keret:
  - Normál / sárga / piros.
- Jelölés, ha más pályát is érint:
  - Pl. „Tartalmaz pizzát” vagy „Tartalmaz konyhai ételt” – kis badge.

**Interakciók:**
- Drag & drop sorrend változtatás.
- „Sürgős tételek kész” jelölés → blokk hátrébb sorolódik.
- „Kész” gomb → ticket eltűnik az aktív listából, bekerül a napi archívba.

---

## 7. ÁLLAPOTOK, SZÍNZÉSEK, IDŐKÓDOK

### 7.1 Asztal állapot színek

- Zöld – szabad.
- Kék – vendég ül, rendelés alatt.
- Sárga – régóta rendelés folyamatban (pl. 25 perc).
- Piros – túl hosszú idő (pl. 35 perc+), figyelmeztetés konyhának is.
- Szürke – inaktív vagy közelgő foglalás.

### 7.2 Kiszállítás / VIP időszínek

- Sárga jelzés:
  - Kiszállítás: 40 perc után.
  - Vendégtér / VIP: 25 perc után (ételek).
- Piros jelzés:
  - Kiszállítás: 60 perc után.
  - Vendégtér / VIP: 35 perc után.

### 7.3 Idő kijelzése

- Minden KDS ticketen és kritikus rendelésen:
  - Nem a rögzítés pontos ideje, hanem **eltelt idő** (pl. „18:23” → 18 perc 23 mp).
- Betűméret nagy, jól látható.

---

## 8. FIZETÉS UI

### 8.1 Fizetési folyamat

1. Felszolgáló / pultos / dispatcher rányom a „Fizetés” gombra.
2. Fizetési modal:
   - Tételes lista (összeg + ÁFA kategória).
   - Kedvezmények beállítása.
   - Fizetési mód(ok) kiválasztása (készpénz, kártya, SZÉP, ajándékkártya, pontok).
   - Split fizetés mód támogatása.

3. „Véglegesítés” gomb:
   - Blokk lezárása.
   - POS blokk infó elkészül (számlához/pénztárhoz).
   - ÁFA véglegesítése.

4. Sikeres lezárás utáni visszajelzés:
   - Zöld toast + opcionális nyomtatási info.

### 8.2 Stornó és módosítás

- Csak megfelelő jogosultsággal.
- ConfirmDialog kötelező, „Megjegyzés” mezővel (kötelező kitölteni).
- Vizualitás:
  - piros gomb,
  - figyelmeztető ikon,
  - jól látható jelzés.

---

## 9. RESPONSIVE VISELKEDÉS

- **Tablet álló (portrait)**:
  - Felső bar + 1 hasáb (listanézet).
  - Asztaltérképnél zoomolható, scrollozható nézet.

- **Tablet fekvő (landscape)**:
  - Felső bar + osztott nézet:
    - pl. balra asztaltérkép, jobbra rendelés részletek.

- **Desktop**:
  - Topbar + sidebar + többoszlopos content.

---

## 10. ACCESSIBILITY (A11Y)

- Kontraszt: minimum WCAG AA szint elérése (sötét háttérrel).
- Ikonok + színkombináció: fontos állapotoknál **ne csak szín**, hanem ikon és szöveg is.
- Billentyű navigáció:
  - Tab sorrend logikus.
  - Enter / Space aktiválja a fő gombokat.
- ARIA attribútumok:
  - Modálok → `aria-modal`, `role="dialog"`.
  - Toast → `role="status"` vagy `role="alert"`.

---

## 11. KOMPONENS KÖNYVTÁR STRUKTÚRA (JAVASLAT)

```text
frontend/src/components/ui/
    Button.tsx
    Input.tsx
    Select.tsx
    Textarea.tsx
    Modal.tsx
    ConfirmDialog.tsx
    Toast.tsx
    Card.tsx
    Badge.tsx
    Chip.tsx
    Spinner.tsx
    Skeleton.tsx
    ErrorBoundary.tsx

frontend/src/components/layout/
    AppShell.tsx
    Sidebar.tsx
    TopBar.tsx
    ContentArea.tsx

frontend/src/components/kds/
    KdsTicket.tsx
    KdsColumn.tsx

frontend/src/components/tables/
    TableIcon.tsx
    TableGrid.tsx
    TableDetailsPanel.tsx
```

---

## 12. ÖSSZEFOGLALÁS

Ez a dokumentum meghatározza a RESTI POS **vizuális alapjait**:
- színek,
- tipográfia,
- layout,
- komponensek,
- szerepkör-alapú nézetek,
- idő- és státuszkódok.

A fejlesztés során minden új képernyőt és komponenst ehhez a designrendszerhez kell igazítani.  
A cél egy **modern, konzisztens, gyorsan átlátható, éttermi környezetben is jól használható POS felület**.

_END OF UI_UX_FOUNDATION v1.0_
