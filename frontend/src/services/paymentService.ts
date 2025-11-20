/**
 * Payment Service - Fizetési műveletek API hívások
 *
 * Backend endpoints (service_orders:8002):
 *   - GET /api/v1/orders/{order_id}
 *   - GET /api/v1/orders/{order_id}/split-check
 *   - POST /api/v1/orders/{order_id}/payments
 *   - POST /api/v1/orders/{order_id}/status/close
 *
 * Frontend hívások (Vite proxy):
 *   - GET /api/orders/{order_id} → http://localhost:8002/api/v1/orders/{order_id}
 *   - GET /api/orders/{order_id}/split-check → http://localhost:8002/api/v1/orders/{order_id}/split-check
 *   - POST /api/orders/{order_id}/payments → http://localhost:8002/api/v1/orders/{order_id}/payments
 *   - POST /api/orders/{order_id}/status/close → http://localhost:8002/api/v1/orders/{order_id}/status/close
 */

import apiClient from './api';
import type {
  Order,
  Payment,
  PaymentCreateRequest,
  SplitCheckResponse,
} from '@/types/payment';

/**
 * Rendelés részleteinek lekérése
 * @param orderId - Rendelés azonosító
 * @returns Order objektum
 */
export const getOrderDetails = async (orderId: number): Promise<Order> => {
  try {
    const response = await apiClient.get<Order>(`/api/orders/${orderId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching order ${orderId}:`, error);
    throw error;
  }
};

/**
 * Split-Check számítás lekérése (számlamegosztás)
 * @param orderId - Rendelés azonosító
 * @returns SplitCheckResponse (személyenkénti bontás)
 */
export const getSplitCheck = async (
  orderId: number
): Promise<SplitCheckResponse> => {
  try {
    const response = await apiClient.get<SplitCheckResponse>(
      `/api/orders/${orderId}/split-check`
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching split-check for order ${orderId}:`, error);
    throw error;
  }
};

/**
 * Fizetés rögzítése
 * @param orderId - Rendelés azonosító
 * @param data - Fizetési adatok (payment_method, amount)
 * @returns Létrehozott Payment objektum
 */
export const recordPayment = async (
  orderId: number,
  data: Omit<PaymentCreateRequest, 'order_id'>
): Promise<Payment> => {
  try {
    const payload: PaymentCreateRequest = {
      order_id: orderId,
      ...data,
    };
    const response = await apiClient.post<Payment>(
      `/api/orders/${orderId}/payments`,
      payload
    );
    return response.data;
  } catch (error) {
    console.error(`Error recording payment for order ${orderId}:`, error);
    throw error;
  }
};

/**
 * Rendelés lezárása (fizetés után)
 * @param orderId - Rendelés azonosító
 * @returns Lezárt Order objektum
 */
export const closeOrder = async (orderId: number): Promise<Order> => {
  try {
    const response = await apiClient.post<Order>(
      `/api/orders/${orderId}/status/close`
    );
    return response.data;
  } catch (error) {
    console.error(`Error closing order ${orderId}:`, error);
    throw error;
  }
};

/**
 * Adott rendeléshez tartozó összes fizetés lekérése
 * @param orderId - Rendelés azonosító
 * @returns Payment lista
 */
export const getPaymentsForOrder = async (
  orderId: number
): Promise<Payment[]> => {
  try {
    const response = await apiClient.get<Payment[]>(
      `/api/orders/${orderId}/payments`
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching payments for order ${orderId}:`, error);
    throw error;
  }
};

/**
 * Blokk nyomtatása egy rendeléshez
 * @param orderId - Rendelés azonosító
 * @returns Nyomtatás eredménye
 */
export const printReceipt = async (
  orderId: number
): Promise<{ success: boolean; message: string; file_path: string; order_id: number }> => {
  try {
    const response = await apiClient.post<{
      success: boolean;
      message: string;
      file_path: string;
      order_id: number;
    }>(`/api/orders/${orderId}/print-receipt`);
    return response.data;
  } catch (error) {
    console.error(`Error printing receipt for order ${orderId}:`, error);
    throw error;
  }
};
