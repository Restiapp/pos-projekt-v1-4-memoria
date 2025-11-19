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
import type { KdsItem, KdsStation, KdsStatus } from '@/types/kds';
import { KDS_STATUS_TO_BACKEND, KDS_STATUS_FROM_BACKEND } from '@/types/kds';

/**
 * Adott állomáshoz tartozó tételek lekérése
 * @param station - Állomás neve ('KONYHA', 'PIZZA', 'PULT')
 * @returns KDS tételek listája
 */
export const getItemsByStation = async (station: KdsStation): Promise<KdsItem[]> => {
  try {
    // CRITICAL FIX (C7.1): Add /orders prefix to match backend router
    const response = await apiClient.get<KdsItem[]>(`/api/orders/kds/stations/${station}/items`);

    // Map backend status values (Hungarian) to frontend values (English)
    const items = response.data.map((item: any) => ({
      ...item,
      kds_status: KDS_STATUS_FROM_BACKEND[item.kds_status] || item.kds_status,
    }));

    return items;
  } catch (error) {
    console.error(`Error fetching KDS items for station ${station}:`, error);
    throw error;
  }
};

/**
 * Tétel státuszának frissítése
 * @param itemId - Tétel azonosító
 * @param status - Új státusz ('PENDING', 'PREPARING', 'READY', 'SERVED')
 * @returns Frissített KDS tétel
 */
export const updateItemStatus = async (
  itemId: number,
  status: KdsStatus
): Promise<KdsItem> => {
  try {
    // CRITICAL FIX: Backend expects query parameter, not request body
    // Map frontend status (English) to backend status (Hungarian)
    const backendStatus = KDS_STATUS_TO_BACKEND[status];

    // CRITICAL FIX (C7.2): Add /orders prefix to match backend router
    // Use query parameter ?status=VALUE instead of request body
    const response = await apiClient.patch<any>(
      `/api/orders/items/${itemId}/kds-status?status=${encodeURIComponent(backendStatus)}`
    );

    // Map backend status back to frontend format
    const item = {
      ...response.data,
      kds_status: KDS_STATUS_FROM_BACKEND[response.data.kds_status] || response.data.kds_status,
    };

    return item;
  } catch (error) {
    console.error(`Error updating KDS status for item ${itemId}:`, error);
    throw error;
  }
};
