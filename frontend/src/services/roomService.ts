/**
 * Room Service
 */

import apiClient from './api';
import type { Room, RoomCreate, RoomUpdate } from '@/types/room';

export const getRooms = async (): Promise<Room[]> => {
  const response = await apiClient.get<Room[]>('/api/rooms', {
    params: { skip: 0, limit: 100 },
  });
  return response.data;
};

export const getRoom = async (id: number): Promise<Room> => {
  const response = await apiClient.get<Room>(`/api/rooms/${id}`);
  return response.data;
};

export const createRoom = async (data: RoomCreate): Promise<Room> => {
  const response = await apiClient.post<Room>('/api/rooms', data);
  return response.data;
};

export const updateRoom = async (id: number, data: RoomUpdate): Promise<Room> => {
  const response = await apiClient.put<Room>(`/api/rooms/${id}`, data);
  return response.data;
};

export const deleteRoom = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/rooms/${id}`);
};
