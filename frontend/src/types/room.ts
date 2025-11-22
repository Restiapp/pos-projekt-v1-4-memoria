/**
 * Room types
 */

export interface Room {
    id: number;
    name: string;
    type: string; // 'indoor' | 'outdoor'
    width: number;
    height: number;
    background_image_url?: string;
}

export interface RoomCreate {
    name: string;
    type?: string;
    width?: number;
    height?: number;
}

export interface RoomUpdate {
    name?: string;
    type?: string;
    width?: number;
    height?: number;
}
