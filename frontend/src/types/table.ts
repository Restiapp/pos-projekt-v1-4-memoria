/**
 * Table és Seat típusdefiníciók
 * Backend API sémáknak megfelelően
 */

export interface Table {
    id: number;
    table_number: string;
    room_id?: number | null;
    position_x: number | null;
    position_y: number | null;
    width: number;
    height: number;
    rotation: number;
    shape: 'rect' | 'round';
    capacity: number | null;
    metadata_json?: any;
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
    shape?: 'rect' | 'round';
    capacity?: number | null;
}

export interface TableUpdate {
    table_number?: string;
    room_id?: number | null;
    position_x?: number | null;
    position_y?: number | null;
    width?: number;
    height?: number;
    rotation?: number;
    shape?: 'rect' | 'round';
    capacity?: number | null;
}
