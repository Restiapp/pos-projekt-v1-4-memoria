/**
 * Table és Seat típusdefiníciók
 * Backend API sémáknak megfelelően
 */

export interface Table {
  id: number;
  table_number: string;
  position_x: number | null;
  position_y: number | null;
  capacity: number | null;
}

export interface Seat {
  id: number;
  table_id: number;
  seat_number: number;
}

export interface TableWithOccupancy extends Table {
  occupied_seats: number; // Foglalt ülések száma (számított érték)
  is_available: boolean;  // Szabad-e az asztal
}

// =====================================================
// ÚJ: Admin CRUD típusok
// =====================================================

/**
 * Új asztal létrehozása (POST /api/tables)
 */
export interface TableCreate {
  table_number: string;
  position_x?: number | null;
  position_y?: number | null;
  capacity?: number | null;
}

/**
 * Asztal frissítése (PUT /api/tables/{id})
 */
export interface TableUpdate {
  table_number?: string;
  position_x?: number | null;
  position_y?: number | null;
  capacity?: number | null;
}
