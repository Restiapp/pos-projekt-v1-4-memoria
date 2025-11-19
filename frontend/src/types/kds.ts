/**
 * KDS (Kitchen Display System) típusdefiníciók
 * Backend API sémáknak megfelelően (service_orders:8002)
 */

// KDS Állomások típusa
export type KdsStation = 'KONYHA' | 'PIZZA' | 'PULT';

// KDS Státuszok (Frontend enum - UI használatra)
export enum KdsStatus {
  PENDING = 'PENDING',     // Várakozik
  PREPARING = 'PREPARING', // Készül
  READY = 'READY',         // Kész
  SERVED = 'SERVED',       // Kiszolgálva
}

// Backend API státusz értékek (Magyar)
export enum KdsStatusBackend {
  VARAKOZIK = 'VÁRAKOZIK',     // Pending/Waiting
  KESZUL = 'KÉSZÜL',           // Preparing
  KESZ = 'KÉSZ',               // Ready
  KISZOLGALVA = 'KISZOLGÁLVA', // Served
}

// Mapping: Frontend -> Backend
export const KDS_STATUS_TO_BACKEND: Record<KdsStatus, KdsStatusBackend> = {
  [KdsStatus.PENDING]: KdsStatusBackend.VARAKOZIK,
  [KdsStatus.PREPARING]: KdsStatusBackend.KESZUL,
  [KdsStatus.READY]: KdsStatusBackend.KESZ,
  [KdsStatus.SERVED]: KdsStatusBackend.KISZOLGALVA,
};

// Mapping: Backend -> Frontend
export const KDS_STATUS_FROM_BACKEND: Record<string, KdsStatus> = {
  'VÁRAKOZIK': KdsStatus.PENDING,
  'KÉSZÜL': KdsStatus.PREPARING,
  'KÉSZ': KdsStatus.READY,
  'KISZOLGÁLVA': KdsStatus.SERVED,
};

// KDS Tétel (egy rendelési tétel)
export interface KdsItem {
  id: number;              // Item ID (egyedi azonosító)
  order_id: number;        // Melyik rendeléshez tartozik
  product_name: string;    // Termék neve (pl. "Hamburger")
  quantity: number;        // Mennyiség
  kds_status: KdsStatus;   // Aktuális státusz
  station: KdsStation;     // Melyik állomáshoz tartozik
  created_at: string;      // Létrehozás időpontja (ISO datetime)
  notes: string | null;    // Megjegyzések (ha van)
  table_number?: string;   // Asztalszám (opcionális, ha rendeléshez tartozik)
}

// API Response típus (GET /api/v1/kds/stations/{station}/items)
export interface KdsItemsResponse {
  items: KdsItem[];
  total: number;
  station: KdsStation;
}

// DEPRECATED: Backend uses query parameter, not request body
// Státusz frissítés Request típus (PATCH /api/v1/items/{item_id}/kds-status?status=VALUE)
export interface UpdateKdsStatusRequest {
  kds_status: KdsStatus;
}
