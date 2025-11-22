/**
 * KDS Service - Konyhai Kijelző API hívások
 *
 * Backend endpoints (service_orders:8002):
 *   - GET /api/v1/kds/stations/{station}/items
 *   - PATCH /api/v1/kds/items/{item_id}/status
 *   - PATCH /api/v1/kds/items/{item_id}/urgent
 *
 * Frontend hívások (Vite proxy):
 *   - GET /api/orders/kds/stations/{station}/items → http://localhost:8002/api/v1/kds/stations/{station}/items
 *   - PATCH /api/orders/items/{item_id}/kds-status → http://localhost:8002/api/v1/kds/items/{item_id}/status
 *   - PATCH /api/orders/kds/items/{item_id}/urgent → http://localhost:8002/api/v1/kds/items/{item_id}/urgent
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

/**
 * Toggle the urgent flag for a KDS item
 * @param itemId - Item ID
 * @param isUrgent - New urgent flag value (true/false)
 * @returns Updated KDS item
 */
export const toggleUrgentFlag = async (
  itemId: number,
  isUrgent: boolean
): Promise<KdsItem> => {
  try {
    const response = await apiClient.patch<any>(
      `/api/orders/kds/items/${itemId}/urgent`,
      { is_urgent: isUrgent }
    );

    // Map backend status to frontend format
    const item = {
      ...response.data,
      kds_status: KDS_STATUS_FROM_BACKEND[response.data.kds_status] || response.data.kds_status,
    };

    return item;
  } catch (error) {
    console.error(`Error toggling urgent flag for item ${itemId}:`, error);
    throw error;
  }
};

/**
 * Drink item for bar KDS queue
 */
export interface DrinkItem {
  id: number;
  orderNumber: number;
  itemName: string;
  quantity: number;
  status: string;
  urgent: boolean;
  createdAt: string;
  minutesWaiting: number;
  notes?: string;
}

/**
 * Get all drink items for the bar KDS queue
 * @returns List of drink items with queue metadata
 */
export const getDrinkItems = async (): Promise<DrinkItem[]> => {
  try {
    const response = await apiClient.get<DrinkItem[]>('/api/orders/kds/drinks');
    return response.data;
  } catch (error) {
    console.error('Error fetching drink items:', error);
    throw error;
  }
};
