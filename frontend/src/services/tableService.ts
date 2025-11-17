/**
 * Table Service - Asztalok és ülések API hívások
 * Használja az apiClient-et (automatikus JWT token injection)
 */

import apiClient from './api';
import type { Table, Seat } from '@/types/table';

interface TableListResponse {
  items: Table[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Összes asztal lekérése
 * Backend: GET /api/v1/tables?page=1&page_size=100
 */
export const getTables = async (): Promise<Table[]> => {
  try {
    const response = await apiClient.get<TableListResponse>('/v1/tables', {
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
 * Backend: GET /api/v1/seats/by-table/{table_id}
 */
export const getSeatsByTable = async (tableId: number): Promise<Seat[]> => {
  try {
    const response = await apiClient.get<Seat[]>(`/v1/seats/by-table/${tableId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching seats for table ${tableId}:`, error);
    throw error;
  }
};
