/**
 * Order Service - Orders API hívások
 *
 * Backend endpoints (service_orders:8002):
 *   - GET /api/v1/orders
 *   - POST /api/v1/orders
 *   - GET /api/v1/orders/{id}
 *   - PUT /api/v1/orders/{id}
 *   - DELETE /api/v1/orders/{id}
 *   - POST /api/v1/orders/{id}/assign-courier (V3.0 / LOGISTICS-FIX)
 *
 * Frontend hívások:
 *   - GET /api/orders → Vite proxy → http://localhost:8002/api/v1/orders
 *   - POST /api/orders → Vite proxy → http://localhost:8002/api/v1/orders
 */

import apiClient from './api';
import type {
  Order,
  OrderCreate,
  OrderUpdate,
  OrderListResponse,
  OrderType,
  OrderStatus,
  CourierAssignmentRequest,
  CourierAssignmentResponse,
} from '@/types/order';

// =====================================================
// ORDERS
// =====================================================

/**
 * GET /api/orders - Rendelések listája (lapozással)
 * Proxy Target: http://localhost:8002/api/v1/orders
 */
export const getOrders = async (
  page: number = 1,
  page_size: number = 20,
  order_type?: OrderType,
  status?: OrderStatus,
  table_id?: number
): Promise<OrderListResponse> => {
  const params: Record<string, any> = { skip: (page - 1) * page_size, limit: page_size };
  if (order_type) {
    params.order_type = order_type;
  }
  if (status) {
    params.status = status;
  }
  if (table_id !== undefined) {
    params.table_id = table_id;
  }

  const response = await apiClient.get<OrderListResponse>('/api/orders', {
    params,
  });
  return response.data;
};

/**
 * GET /api/orders/{id} - Rendelés részletei
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}
 */
export const getOrderById = async (id: number): Promise<Order> => {
  const response = await apiClient.get<Order>(`/api/orders/${id}`);
  return response.data;
};

/**
 * POST /api/orders - Új rendelés létrehozása
 * Proxy Target: http://localhost:8002/api/v1/orders
 */
export const createOrder = async (orderData: OrderCreate): Promise<Order> => {
  const response = await apiClient.post<Order>('/api/orders', orderData);
  return response.data;
};

/**
 * PUT /api/orders/{id} - Rendelés frissítése
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}
 */
export const updateOrder = async (id: number, orderData: OrderUpdate): Promise<Order> => {
  const response = await apiClient.put<Order>(`/api/orders/${id}`, orderData);
  return response.data;
};

/**
 * DELETE /api/orders/{id} - Rendelés törlése
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}
 */
export const deleteOrder = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/orders/${id}`);
};

// =====================================================
// COURIER ASSIGNMENT (V3.0 / LOGISTICS-FIX)
// =====================================================

/**
 * POST /api/orders/{id}/assign-courier - Futár hozzárendelése rendeléshez
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}/assign-courier
 *
 * V3.0 / LOGISTICS-FIX: Assigns a courier to a delivery order and updates
 * the courier's status to ON_DELIVERY via service_logistics.
 */
export const assignCourierToOrder = async (
  orderId: number,
  courierId: number
): Promise<CourierAssignmentResponse> => {
  const response = await apiClient.post<CourierAssignmentResponse>(
    `/api/orders/${orderId}/assign-courier`,
    { courier_id: courierId } as CourierAssignmentRequest
  );
  return response.data;
};

// =====================================================
// ORDER ITEMS
// =====================================================

/**
 * POST /api/orders/{id}/items - Tétel hozzáadása rendeléshez
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}/items
 */
export const addItemToOrder = async (orderId: number, itemData: any): Promise<any> => {
  const response = await apiClient.post(`/api/orders/${orderId}/items`, itemData);
  return response.data;
};

// =====================================================
// VAT MANAGEMENT
// =====================================================

/**
 * Update VAT rate for an order
 * Uses PUT /api/orders/{id} to update the final_vat_rate field
 *
 * @param orderId - Order ID to update
 * @param newVat - New VAT rate (5 or 27)
 * @returns Updated order
 */
export const updateVAT = async (orderId: number, newVat: number): Promise<Order> => {
  const response = await apiClient.put<Order>(`/api/orders/${orderId}`, {
    final_vat_rate: newVat,
  });
  return response.data;
};

// =====================================================
// TABLE TIME TRACKING
// =====================================================

/**
 * Get active orders for tables (time-based color coding)
 *
 * Fetches all open "Helyben" (dine-in) orders and returns a map
 * of table_id -> oldest order for that table.
 *
 * This is used for time-based color coding in the TableMap component.
 *
 * @returns Map of table_id to oldest active order
 */
export const getActiveOrdersForTables = async (): Promise<Map<number, Order>> => {
  // Fetch all open dine-in orders
  const response = await getOrders(1, 100, 'Helyben', 'NYITOTT');

  const tableOrderMap = new Map<number, Order>();

  // Group orders by table_id and keep the oldest order per table
  response.items.forEach((order: Order) => {
    if (!order.table_id) return; // Skip orders without table assignment

    const existingOrder = tableOrderMap.get(order.table_id);

    if (!existingOrder) {
      // First order for this table
      tableOrderMap.set(order.table_id, order);
    } else {
      // Keep the older order (earlier created_at timestamp)
      const existingTime = new Date(existingOrder.created_at).getTime();
      const currentTime = new Date(order.created_at).getTime();

      if (currentTime < existingTime) {
        tableOrderMap.set(order.table_id, order);
      }
    }
  });

  return tableOrderMap;
};
