/**
 * Order Service - Order API hívások (Rendelések kezelése)
 *
 * Backend endpoints (service_orders:8002):
 *   - GET /api/v1/orders
 *   - POST /api/v1/orders/{id}/assign-courier
 *
 * Frontend hívások:
 *   - GET /api/orders → Vite proxy → http://localhost:8002/api/v1/orders
 *   - POST /api/orders/{id}/assign-courier → Vite proxy → http://localhost:8002/api/v1/orders/{id}/assign-courier
 */

import apiClient from './api';
import type { Order, OrderListResponse, OrderType, OrderStatus } from '@/types/order';

// =====================================================
// TYPES
// =====================================================

export interface AssignCourierRequest {
  courier_id: number;
}

export interface AssignCourierResponse {
  order: Order;
  courier_id: number;
  message: string;
}

// =====================================================
// ORDER OPERATIONS
// =====================================================

/**
 * GET /api/orders - Rendelések listája (lapozással és szűréssel)
 * Proxy Target: http://localhost:8002/api/v1/orders
 */
export const getOrders = async (
  skip: number = 0,
  limit: number = 100,
  orderType?: OrderType,
  status?: OrderStatus,
  tableId?: number
): Promise<OrderListResponse> => {
  const params: Record<string, any> = { skip, limit };
  if (orderType) {
    params.order_type = orderType;
  }
  if (status) {
    params.status = status;
  }
  if (tableId !== undefined) {
    params.table_id = tableId;
  }

  const response = await apiClient.get<OrderListResponse>('/api/orders', {
    params,
  });
  return response.data;
};

/**
 * POST /api/orders/{id}/assign-courier - Futár hozzárendelése rendeléshez
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}/assign-courier
 */
export const assignCourierToOrder = async (
  orderId: number,
  courierId: number
): Promise<AssignCourierResponse> => {
  const response = await apiClient.post<AssignCourierResponse>(
    `/api/orders/${orderId}/assign-courier`,
    { courier_id: courierId } as AssignCourierRequest
  );
  return response.data;
};
