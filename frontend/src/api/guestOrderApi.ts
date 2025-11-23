import axios from 'axios';

// Base URL handling - in production this would be handled by Vite proxy
const API_BASE_URL = '/api/v1';

export interface OrderItem {
  id: number;
  product_id: number;
  name?: string; // Often joined from product
  quantity: number;
  unit_price: number;
  round_number: number;
  metadata_json?: {
    is_urgent?: boolean;
    course_tag?: string;
    notes?: string;
    sync_with_course?: string;
  };
  kds_status?: string;
}

export interface OrderWithMetrics {
  id: number;
  table_id: number;
  status: string;
  total_amount: number;
  items: OrderItem[];
  start_timestamp?: string;
  elapsed_minutes?: number;
  last_round_time?: string;
}

export interface TableMetrics {
  table_id: number;
  active: boolean;
  active_order_id?: number;
  order_start_time?: string;
  minutes_since_start: number;
  last_round_minutes: number;
  color: 'green' | 'yellow' | 'red';
}

export interface AddItemRequest {
  product_id: number;
  quantity: number;
  is_urgent?: boolean;
  course_tag?: string;
  notes?: string;
}

export const guestOrderApi = {
  // Open/Get active order
  openOrder: async (tableId: number): Promise<OrderWithMetrics> => {
    const response = await axios.post(`${API_BASE_URL}/orders/${tableId}/open`);
    return response.data;
  },

  // Add items with round number
  addItems: async (orderId: number, roundNumber: number, items: AddItemRequest[]) => {
    const response = await axios.post(`${API_BASE_URL}/orders/${orderId}/items`, {
      round_number: roundNumber,
      items: items
    });
    return response.data;
  },

  // Update item flags
  updateItemFlags: async (itemId: number, flags: { is_urgent?: boolean; course_tag?: string }) => {
    const response = await axios.patch(`${API_BASE_URL}/orders/items/${itemId}/flags`, flags);
    return response.data;
  },

  // Get table metrics
  getMetrics: async (tableId: number): Promise<TableMetrics> => {
    const response = await axios.get(`${API_BASE_URL}/orders/${tableId}/metrics`);
    return response.data;
  },

  // Move order
  moveOrder: async (orderId: number, targetTableId: number) => {
    const response = await axios.post(`${API_BASE_URL}/orders/${orderId}/move-to-table/${targetTableId}`);
    return response.data;
  },

  // Send round to KDS
  sendRoundToKds: async (orderId: number, roundNumber: number) => {
    const response = await axios.post(`${API_BASE_URL}/orders/${orderId}/rounds/${roundNumber}/send-to-kds`);
    return response.data;
  }
};
