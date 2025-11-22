/**
 * Table Service - Asztalok és ülések API hívások
 *
 * Backend endpoints (service_orders:8002):
 *   - GET /api/v1/tables
 *   - GET /api/v1/seats/by-table/{table_id}
 *
 * Frontend hívások:
 *   - GET /api/tables → Vite proxy → http://localhost:8002/api/v1/tables
 *   - GET /api/seats/by-table/{id} → Vite proxy → http://localhost:8002/api/v1/seats/by-table/{id}
 */

import apiClient from './api';
import type { Table, Seat, TableCreate, TableUpdate } from '@/types/table';
import type { Room } from '@/types/room';

interface TableListResponse {
  items: Table[];
  total: number;
  page: number;
  page_size: number;
}

// =====================================================
// ROOM MŰVELETEK
// =====================================================

export const getRooms = async (): Promise<Room[]> => {
  try {
    const response = await apiClient.get<Room[]>('/api/rooms', {
      params: { skip: 0, limit: 100 },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching rooms:', error);
    throw error;
  }
};

export const createRoom = async (roomData: Omit<Room, 'id'>): Promise<Room> => {
  try {
    const response = await apiClient.post<Room>('/api/rooms', roomData);
    return response.data;
  } catch (error) {
    console.error('Error creating room:', error);
    throw error;
  }
};

export const updateRoom = async (id: number, roomData: Partial<Omit<Room, 'id'>>): Promise<Room> => {
  try {
    const response = await apiClient.put<Room>(`/api/rooms/${id}`, roomData);
    return response.data;
  } catch (error) {
    console.error(`Error updating room ${id}:`, error);
    throw error;
  }
};

export const deleteRoom = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/rooms/${id}`);
  } catch (error) {
    console.error(`Error deleting room ${id}:`, error);
    throw error;
  }
};

// =====================================================
// TABLE MŰVELETEK
// =====================================================

/**
 * Összes asztal lekérése
 * Proxy Target: http://localhost:8002/api/v1/tables?page=1&page_size=100
 */
export const getTables = async (): Promise<Table[]> => {
  try {
    const response = await apiClient.get<TableListResponse>('/api/tables', {
      params: {
        page: 1,
        page_size: 100, // Jelenleg az összes asztal egy kérésben
      },
    });
    return response.data.items;
  } catch (error) {
    console.error('Error fetching tables:', error);
    throw error;
  }
};

/**
 * Adott asztalhoz tartozó ülések lekérése
 * Proxy Target: http://localhost:8002/api/v1/seats/by-table/{table_id}
 */
export const getSeatsByTable = async (tableId: number): Promise<Seat[]> => {
  try {
    const response = await apiClient.get<Seat[]>(`/api/seats/by-table/${tableId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching seats for table ${tableId}:`, error);
    throw error;
  }
};

// =====================================================
// ÚJ: ADMIN CRUD MŰVELETEK
// =====================================================

/**
 * Új asztal létrehozása
 * POST /api/tables
 * Proxy Target: http://localhost:8002/api/v1/tables
 */
export const createTable = async (tableData: TableCreate): Promise<Table> => {
  try {
    const response = await apiClient.post<Table>('/api/tables', tableData);
    return response.data;
  } catch (error) {
    console.error('Error creating table:', error);
    throw error;
  }
};

/**
 * Asztal frissítése
 * PUT /api/tables/{id}
 * Proxy Target: http://localhost:8002/api/v1/tables/{id}
 */
export const updateTable = async (
  id: number,
  tableData: TableUpdate
): Promise<Table> => {
  try {
    const response = await apiClient.put<Table>(`/api/tables/${id}`, tableData);
    return response.data;
  } catch (error) {
    console.error(`Error updating table ${id}:`, error);
    throw error;
  }
};

/**
 * Asztal törlése
 * DELETE /api/tables/{id}
 * Proxy Target: http://localhost:8002/api/v1/tables/{id}
 */
export const deleteTable = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/tables/${id}`);
  } catch (error) {
    console.error(`Error deleting table ${id}:`, error);
    throw error;
  }
};
