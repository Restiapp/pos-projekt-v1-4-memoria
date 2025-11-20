/**
 * KDS Service - Konyhai Kijelző API hívások
 *
 * Backend endpoints (service_orders:8002):
 *   - GET /api/v1/kds/stations/{station}/items
 *   - PATCH /api/v1/items/{item_id}/kds-status
 *
 * Frontend hívások (Vite proxy):
 *   - GET /api/kds/stations/{station}/items → http://localhost:8002/api/v1/kds/stations/{station}/items
 *   - PATCH /api/items/{item_id}/kds-status → http://localhost:8002/api/v1/items/{item_id}/kds-status
 */

import apiClient from './api';
import type { KdsItem, KdsStation, KdsStatus, UpdateKdsStatusRequest } from '@/types/kds';

/**
 * Adott állomáshoz tartozó tételek lekérése
 * @param station - Állomás neve ('KONYHA', 'PIZZA', 'PULT')
 * @returns KDS tételek listája
 */
export const getItemsByStation = async (station: KdsStation): Promise<KdsItem[]> => {
  try {
    // CRITICAL FIX (C7.1): Add /orders prefix to match backend router
    const response = await apiClient.get<KdsItem[]>(`/api/orders/kds/stations/${station}/items`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching KDS items for station ${station}:`, error);
    throw error;
  }
};

/**
 * Tétel státuszának frissítése
 * @param itemId - Tétel azonosító
 * @param status - Új státusz ('PENDING', 'PREPARING', 'READY')
 * @returns Frissített KDS tétel
 */
export const updateItemStatus = async (
  itemId: number,
  status: KdsStatus
): Promise<KdsItem> => {
  try {
    // CRITICAL FIX: Send status as QUERY parameter (?status=PREPARING), not in body
    const response = await apiClient.patch<KdsItem>(
      `/api/orders/items/${itemId}/kds-status?status=${status}`
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating KDS status for item ${itemId}:`, error);
    throw error;
  }
};
