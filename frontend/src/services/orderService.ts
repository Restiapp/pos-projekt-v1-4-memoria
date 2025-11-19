/**
 * Order Service - Order API calls
 *
 * Backend endpoints (service_orders:8002):
 *   - GET /api/v1/orders
 *   - POST /api/v1/orders
 *   - GET /api/v1/orders/{id}
 *   - PUT /api/v1/orders/{id}
 *   - DELETE /api/v1/orders/{id}
 *   - POST /api/v1/orders/{order_id}/items
 *   - GET /api/v1/orders/{order_id}/items
 *
 * Frontend calls:
 *   - GET /api/orders → Vite proxy → http://localhost:8002/api/v1/orders
 *   - POST /api/orders → Vite proxy → http://localhost:8002/api/v1/orders
 */

import apiClient from './api';
import type {
  Order,
  OrderCreate,
  OrderUpdate,
  OrderResponse,
  OrderListResponse,
  OrderItem,
  OrderItemCreate,
  OrderItemResponse,
} from '@/types/order';

// =====================================================
// ORDERS
// =====================================================

/**
 * GET /api/orders - Orders list (paginated)
 * Proxy Target: http://localhost:8002/api/v1/orders
 */
export const getOrders = async (
  skip: number = 0,
  limit: number = 100,
  order_type?: string,
  status?: string,
  table_id?: number
): Promise<OrderListResponse> => {
  const params: Record<string, any> = { skip, limit };
  if (order_type) params.order_type = order_type;
  if (status) params.status = status;
  if (table_id) params.table_id = table_id;

  const response = await apiClient.get<OrderListResponse>('/api/orders', {
    params,
  });
  return response.data;
};

/**
 * GET /api/orders/{id} - Order details
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}
 */
export const getOrderById = async (id: number): Promise<OrderResponse> => {
  const response = await apiClient.get<OrderResponse>(`/api/orders/${id}`);
  return response.data;
};

/**
 * POST /api/orders - Create new order
 * Proxy Target: http://localhost:8002/api/v1/orders
 */
export const createOrder = async (
  orderData: OrderCreate
): Promise<OrderResponse> => {
  const response = await apiClient.post<OrderResponse>('/api/orders', orderData);
  return response.data;
};

/**
 * PUT /api/orders/{id} - Update order
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}
 */
export const updateOrder = async (
  id: number,
  orderData: OrderUpdate
): Promise<OrderResponse> => {
  const response = await apiClient.put<OrderResponse>(
    `/api/orders/${id}`,
    orderData
  );
  return response.data;
};

/**
 * DELETE /api/orders/{id} - Delete order
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}
 */
export const deleteOrder = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/orders/${id}`);
};

// =====================================================
// ORDER ITEMS
// =====================================================

/**
 * POST /api/orders/{order_id}/items - Add item to order
 * Proxy Target: http://localhost:8002/api/v1/orders/{order_id}/items
 */
export const addItemToOrder = async (
  orderId: number,
  itemData: OrderItemCreate
): Promise<OrderItemResponse> => {
  const response = await apiClient.post<OrderItemResponse>(
    `/api/orders/${orderId}/items`,
    itemData
  );
  return response.data;
};

/**
 * GET /api/orders/{order_id}/items - Get items for order
 * Proxy Target: http://localhost:8002/api/v1/orders/{order_id}/items
 */
export const getOrderItems = async (
  orderId: number
): Promise<OrderItemResponse[]> => {
  const response = await apiClient.get<OrderItemResponse[]>(
    `/api/orders/${orderId}/items`
  );
  return response.data;
};

/**
 * DELETE /api/orders/items/{item_id} - Delete order item
 * Proxy Target: http://localhost:8002/api/v1/orders/items/{item_id}
 */
export const deleteOrderItem = async (itemId: number): Promise<void> => {
  await apiClient.delete(`/api/orders/items/${itemId}`);
};
