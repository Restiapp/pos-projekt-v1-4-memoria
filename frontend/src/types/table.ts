/**
 * Table and Seat type definitions aligned with backend schemas.
 */

export type TableStatus =
  | 'FREE'
  | 'ORDERING'
  | 'IN_PROGRESS'
  | 'PAYING'
  | 'RESERVED'
  | 'INACTIVE';

export type TableShape = 'rect' | 'round' | 'square' | 'rectangle';

export interface Table {
  id: number;
  table_number: string;
  room_id?: number | null;
  position_x: number | null;
  position_y: number | null;
  width: number;
  height: number;
  rotation: number;
  shape: TableShape;
  capacity: number | null;
  metadata_json?: Record<string, unknown> | null;
  // Frontend-only enrichment fields (derived from metadata or future API extensions)
  status?: TableStatus;
  is_active?: boolean;
  is_online_bookable?: boolean;
  is_smoking?: boolean;
}

export interface Seat {
  id: number;
  table_id: number;
  seat_number: number;
}

export interface TableWithOccupancy extends Table {
  occupied_seats: number;
  is_available: boolean;
}

export interface TableCreate {
  table_number: string;
  room_id?: number | null;
  position_x?: number | null;
  position_y?: number | null;
  width?: number;
  height?: number;
  rotation?: number;
  shape?: TableShape;
  capacity?: number | null;
  metadata_json?: Record<string, unknown> | null;
}

export interface TableUpdate {
  table_number?: string;
  room_id?: number | null;
  position_x?: number | null;
  position_y?: number | null;
  width?: number;
  height?: number;
  rotation?: number;
  shape?: TableShape;
  capacity?: number | null;
  metadata_json?: Record<string, unknown> | null;
}
