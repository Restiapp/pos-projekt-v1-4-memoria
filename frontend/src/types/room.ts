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
    is_active: boolean;
    display_order: number;
}

export interface RoomCreate {
    name: string;
    type?: string;
    width?: number;
    height?: number;
    is_active?: boolean;
    display_order?: number;
}

export interface RoomUpdate {
    name?: string;
    type?: string;
    width?: number;
    height?: number;
    is_active?: boolean;
    display_order?: number;
}

export interface RoomReorder {
    room_ids: number[];
}
