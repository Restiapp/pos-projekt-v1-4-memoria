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
  OrderWithItems,
  OrderItem,
  AddItemsToRoundRequest,
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

/**
 * PUT /api/orders/items/{item_id} - Tétel frissítése
 * Proxy Target: http://localhost:8002/api/v1/orders/items/{item_id}
 *
 * Supports updating: quantity, unit_price, is_urgent, metadata, etc.
 */
export const updateOrderItem = async (itemId: number, itemData: any): Promise<any> => {
  const response = await apiClient.put(`/api/orders/items/${itemId}`, itemData);
  return response.data;
};

/**
 * PATCH /api/orders/items/{item_id}/urgent - Sürgős jelző beállítása
 * Proxy Target: http://localhost:8002/api/v1/orders/kds/items/{item_id}/urgent
 *
 * Toggle urgent flag for an existing order item
 * TODO: Verify backend endpoint - may need to use updateOrderItem instead
 */
export const toggleItemUrgent = async (itemId: number, isUrgent: boolean): Promise<any> => {
  const response = await apiClient.patch(`/api/orders/items/${itemId}/urgent`, {
    is_urgent: isUrgent,
  });
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
// TABLE ORDER WORKFLOW (FE-2: Guest Floor)
// =====================================================

/**
 * TODO: Backend endpoint to be implemented by Jules
 * POST /api/orders/{table_id}/open - Open or get active order for table
 *
 * Opens a new order for the specified table, or returns the existing active order.
 * Proxy Target: http://localhost:8002/api/v1/orders/{table_id}/open
 *
 * @param tableId - Table ID
 * @returns Order (newly created or existing active order)
 */
export const openOrGetActiveOrder = async (tableId: number): Promise<Order> => {
  try {
    const response = await apiClient.post<Order>(`/api/orders/${tableId}/open`);
    return response.data;
  } catch (error: any) {
    // If endpoint doesn't exist yet (404), create order manually as fallback
    if (error.response?.status === 404 || error.response?.status === 500) {
      // Fallback: Use standard createOrder with table_id
      const orderData: OrderCreate = {
        order_type: 'Helyben',
        status: 'NYITOTT',
        table_id: tableId,
        final_vat_rate: 27,
      };
      return await createOrder(orderData);
    }
    throw error;
  }
};

/**
 * TODO: Backend endpoint to be implemented by Jules
 * GET /api/orders/{table_id}/active - Get active order for table
 *
 * Returns the active order for the specified table, or null if none exists.
 * Proxy Target: http://localhost:8002/api/v1/orders/{table_id}/active
 *
 * @param tableId - Table ID
 * @returns Order or null
 */
export const getActiveOrderForTable = async (tableId: number): Promise<Order | null> => {
  try {
    const response = await apiClient.get<Order>(`/api/orders/${tableId}/active`);
    return response.data;
  } catch (error: any) {
    // If endpoint doesn't exist yet (404), use fallback to search orders
    if (error.response?.status === 404) {
      const ordersResponse = await getOrders(1, 20, 'Helyben', 'NYITOTT', tableId);
      return ordersResponse.items[0] ?? null;
    }
    throw error;
  }
};

// =====================================================
// ROUNDS MANAGEMENT (FE-3: Order Service Integration)
// =====================================================

/**
 * GET /api/orders/{id}/items - Get order with all items
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}/items
 *
 * NOTE: This endpoint may not exist yet on backend.
 * For now, we'll try to fetch it, but fall back to getOrderById if it fails.
 */
export const getOrderWithItems = async (orderId: number): Promise<OrderWithItems> => {
  try {
    const response = await apiClient.get<OrderWithItems>(`/api/orders/${orderId}/items`);
    return response.data;
  } catch (error) {
    // Fallback: Get order and items separately
    console.warn('GET /api/orders/{id}/items not available, using fallback');
    const order = await getOrderById(orderId);
    const itemsResponse = await apiClient.get<OrderItem[]>(`/api/orders/${orderId}/items`);
    return {
      ...order,
      items: itemsResponse.data || [],
    };
  }
};

/**
 * POST /api/orders/{id}/rounds/{round_number}/items - Add items to a specific round
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}/rounds/{round_number}/items
 *
 * NOTE: This endpoint may not exist yet. Fallback: add items with round_number in payload
 */
export const addItemsToRound = async (
  orderId: number,
  roundNumber: number,
  items: AddItemsToRoundRequest['items']
): Promise<OrderItem[]> => {
  try {
    const response = await apiClient.post<OrderItem[]>(
      `/api/orders/${orderId}/rounds/${roundNumber}/items`,
      { items }
    );
    return response.data;
  } catch (error) {
    // Fallback: add items one by one with round_number
    console.warn('Rounds endpoint not available, using fallback');
    const addedItems: OrderItem[] = [];
    for (const item of items) {
      const itemData = {
        ...item,
        round_number: roundNumber,
        kds_status: 'WAITING',
      };
      const addedItem = await addItemToOrder(orderId, itemData);
      addedItems.push(addedItem);
    }
    return addedItems;
  }
};

/**
 * POST /api/orders/{id}/rounds/{round_number}/send-to-kds - Send a round to kitchen
 * Proxy Target: http://localhost:8002/api/v1/orders/{id}/rounds/{round_number}/send-to-kds
 *
 * NOTE: This endpoint may not exist yet. For now, this is a TODO placeholder.
 */
export const sendRoundToKds = async (
  orderId: number,
  roundNumber: number
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await apiClient.post<{ success: boolean; message: string }>(
      `/api/orders/${orderId}/rounds/${roundNumber}/send-to-kds`
    );
    return response.data;
  } catch (error) {
    // TODO: Backend endpoint not implemented yet
    console.warn('sendRoundToKds endpoint not available yet');
    // For now, return success to allow UI testing
    return {
      success: true,
      message: `Kör ${roundNumber} elküldve a konyhának (frontend mock)`,
    };
  }
};
