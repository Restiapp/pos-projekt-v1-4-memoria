# KDS (Kitchen Display System) Komponensek

## Feladat B2: KDS UI Frontend Implementáció

Ez a könyvtár tartalmazza a KDS (Konyhai Kijelző Rendszer) frontend komponenseit.

## Komponensek

### 1. KdsBoard.tsx
**Fő KDS komponens állomásváltó funkciókkal**

A KdsBoard a fő komponens, amely:
- ✅ Állomások közötti váltást biztosít fülek segítségével (Forró Konyha, Pizza Állomás, Ital Pult)
- ✅ Csempés nézetet (grid layout) használ a rendelési tételek megjelenítésére
- ✅ Valós idejű frissítést végez (10 másodpercenként)
- ✅ Kézi frissítés gomb
- ✅ Státusz összesítő (hány tétel várakozik, készül, kész)

**Használat:**
```tsx
import { KdsBoard } from '@/components/kds/KdsBoard';

export const KdsPage = () => {
  return (
    <div>
      <KdsBoard />
    </div>
  );
};
```

### 2. KdsCard.tsx
**Egyetlen rendelési tétel kártyája**

Megjelenít:
- ✅ Termék neve
- ✅ Mennyiség
- ✅ Jegyzetek (ha van)
- ✅ Eltelt idő (automatikusan frissül 30 másodpercenként)
- ✅ Rendelés ID és asztalszám
- ✅ Aktuális státusz
- ✅ Státuszváltó gombok

**Státusz folyamat:**
```
VÁRAKOZIK → KÉSZÜL → KÉSZ → KISZOLGÁLVA
```

**Interaktivitás:**
- Kattintásra a csempe státusza változik
- API hívás: `PATCH /api/orders/items/{itemId}/kds-status?status={newStatus}`

### 3. KdsLane.tsx
**Egyetlen állomás oszlopa (legacy, nem használt a KdsBoard-ban)**

Megjeleníti egy állomáshoz tartozó összes tételt oszlopos elrendezésben.

## API Integráció

### Backend Endpoints

**Tételek lekérése állomás szerint:**
```
GET /api/orders/kds/stations/{station}/items
```
Állomások: `KONYHA`, `PIZZA`, `PULT`

**Státusz frissítése:**
```
PATCH /api/orders/items/{itemId}/kds-status?status={newStatus}
```
Státuszok: `VÁRAKOZIK`, `KÉSZÜL`, `KÉSZ`, `KISZOLGÁLVA`

### Service Layer

A `kdsService.ts` fájl tartalmazza az API hívásokat:
- `getItemsByStation(station)` - Állomás tételeinek lekérése
- `updateItemStatus(itemId, status)` - Tétel státuszának frissítése

## Típusok

```typescript
// KDS Állomások
type KdsStation = 'KONYHA' | 'PIZZA' | 'PULT';

// KDS Státuszok (magyar nyelvű, backend szerint)
enum KdsStatus {
  VARAKOZIK = 'VÁRAKOZIK',     // Waiting
  KESZUL = 'KÉSZÜL',           // In Progress
  KESZ = 'KÉSZ',               // Ready
  KISZOLGALVA = 'KISZOLGÁLVA'  // Served
}

// KDS Tétel
interface KdsItem {
  id: number;
  order_id: number;
  product_name: string;
  quantity: number;
  kds_status: KdsStatus;
  station: KdsStation;
  created_at: string;
  notes: string | null;
  table_number?: string;
}
```

## Stílusok

### KdsBoard.css
- Füles navigáció (tabs)
- Grid layout a csempékhez (responsive)
- Vezérlő sáv stílusok
- Státusz színek és badge-ek

### KdsCard.css
- Kártya layout
- Státusz specifikus színek (border-left)
- Eltelt idő badge
- Gomb stílusok (elkezdeni, kész, kiszolgálva)

## Responsive Design

A KdsBoard teljesen reszponzív:
- **Desktop (>1024px)**: 3-4 oszlopos grid
- **Tablet (768px-1024px)**: 2-3 oszlopos grid
- **Mobil (<768px)**: 1 oszlopos grid

## Funkciók

### Automatikus Frissítés
- 10 másodpercenként automatikusan lekéri az aktív állomás tételeit
- Az eltelt idő 30 másodpercenként frissül minden kártyán

### Állomásváltás
- Fülek segítségével lehet váltani az állomások között
- Csak az aktív állomás tételei látszanak
- Gyors váltás gombokkal

### Státuszváltás
- Egy kattintással lehet léptetni a státuszt
- API hívás után automatikus frissítés
- Vizuális feedback (színek, gombok)

## Fejlesztés

### Tesztelés Dummy Adatokkal

Ha nincs backend elérhető, használhatod a következő dummy adatokat:

```typescript
const dummyItems: KdsItem[] = [
  {
    id: 1,
    order_id: 101,
    product_name: 'Hamburger',
    quantity: 2,
    kds_status: KdsStatus.VARAKOZIK,
    station: 'KONYHA',
    created_at: new Date().toISOString(),
    notes: 'Extra sajt',
    table_number: '12'
  },
  // ... további tételek
];
```

### Debug Mód

Használd a böngésző DevTools-t az API hívások nyomon követésére:
```javascript
// kdsService.ts-ben
console.log('Fetching items for station:', station);
console.log('Updating status:', itemId, status);
```

## Hibakezelés

A komponensek hibakezelést implementálnak:
- API hibák esetén console.error + alert
- Loading state betöltés közben
- Empty state, ha nincs tétel

## Továbbfejlesztési Lehetőségek

1. **WebSocket integráció** - Valós idejű push értesítések
2. **Hangjelzés** - Új rendelés érkezésekor
3. **Szűrők** - Státusz szerinti szűrés
4. **Rendezés** - Idő, prioritás szerint
5. **Teljes képernyős mód** - Nagyobb monitorokhoz
6. **Téma váltás** - Dark mode támogatás

## Verzió Történet

- **V2 (Feladat B2)**: KdsBoard komponens állomásváltással, magyar státuszok, eltelt idő
- **V1**: Eredeti KdsPage oszlopos elrendezéssel
