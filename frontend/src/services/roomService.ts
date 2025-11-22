/**
 * Room Service
 */

import { api } from '@/utils/api';
import type { Room, RoomCreate, RoomUpdate } from '@/types/room';

export const getRooms = async (): Promise<Room[]> => {
    const response = await api.get<Room[]>('/rooms/');
    return response.data;
};

export const getRoom = async (id: number): Promise<Room> => {
    const response = await api.get<Room>(`/rooms/${id}`);
    return response.data;
};

export const createRoom = async (data: RoomCreate): Promise<Room> => {
    const response = await api.post<Room>('/rooms/', data);
    return response.data;
};

export const updateRoom = async (id: number, data: RoomUpdate): Promise<Room> => {
    const response = await api.put<Room>(`/rooms/${id}`, data);
    return response.data;
};

export const deleteRoom = async (id: number): Promise<void> => {
    await api.delete(`/rooms/${id}`);
};
