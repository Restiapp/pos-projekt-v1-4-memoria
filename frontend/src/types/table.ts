/**
 * Table és Seat típusdefiníciók
 * Backend API sémáknak megfelelően
 */

export interface Room {
  id: number;
  name: string;
  width: number;
  height: number;
  is_active: boolean;
}

export interface Table {
  id: number;
  table_number: string;
  room_id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  shape: 'RECTANGLE' | 'CIRCLE';
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
  room_id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  shape: 'RECTANGLE' | 'CIRCLE';
  capacity?: number | null;
}

/**
 * Asztal frissítése (PUT /api/tables/{id})
 */
export interface TableUpdate {
  table_number?: string;
  room_id?: number;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  rotation?: number;
  shape?: 'RECTANGLE' | 'CIRCLE';
  capacity?: number | null;
}
