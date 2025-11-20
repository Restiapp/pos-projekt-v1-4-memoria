/**
 * KDS (Kitchen Display System) típusdefiníciók
 * Backend API sémáknak megfelelően (service_orders:8002)
 */

// KDS Állomások típusa
export type KdsStation = 'KONYHA' | 'PIZZA' | 'PULT';

// KDS Státuszok (Backend enum-nak megfelelően)
export enum KdsStatus {
  PENDING = 'PENDING',     // Várakozik
  PREPARING = 'PREPARING', // Készül
  READY = 'READY',         // Kész
}

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
  course: string | null;   // Fogás típus (pl. "Előétel", "Főétel", "Desszert")
  table_number?: string;   // Asztalszám (opcionális, ha rendeléshez tartozik)
}

// API Response típus (GET /api/v1/kds/stations/{station}/items)
export interface KdsItemsResponse {
  items: KdsItem[];
  total: number;
  station: KdsStation;
}

// Státusz frissítés Request típus (PATCH /api/v1/items/{item_id}/kds-status)
export interface UpdateKdsStatusRequest {
  kds_status: KdsStatus;
}
