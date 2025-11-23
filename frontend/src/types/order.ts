/**
 * Order típusok - Backend API sémákkal szinkronban
 * Backend: backend/service_orders/schemas/order.py
 */

// =====================================================
// ORDER TYPES
// =====================================================

export type OrderType = 'Helyben' | 'Elvitel' | 'Kiszállítás';
export type OrderStatus = 'NYITOTT' | 'FELDOLGOZVA' | 'LEZART' | 'SZTORNÓ';

export interface Order {
  id: number;
  order_type: OrderType;
  status: OrderStatus;
  table_id?: number;
  customer_id?: number;
  courier_id?: number; // V3.0: LOGISTICS-FIX
  total_amount?: number;
  final_vat_rate: number;
  ntak_data?: Record<string, any>;
  notes?: string;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface OrderCreate {
  order_type: OrderType;
  status?: OrderStatus;
  table_id?: number;
  customer_id?: number;
  courier_id?: number;
  total_amount?: number;
  final_vat_rate?: number;
  ntak_data?: Record<string, any>;
  notes?: string;
}

export interface OrderUpdate {
  order_type?: OrderType;
  status?: OrderStatus;
  table_id?: number;
  customer_id?: number;
  courier_id?: number;
  total_amount?: number;
  final_vat_rate?: number;
  ntak_data?: Record<string, any>;
  notes?: string;
}

export interface OrderListResponse {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
}

// =====================================================
// COURIER ASSIGNMENT TYPES (V3.0 / LOGISTICS-FIX)
// =====================================================

export interface CourierAssignmentRequest {
  courier_id: number;
}

export interface CourierAssignmentResponse {
  order: Order;
  courier_id: number;
  message: string;
}

// =====================================================
// ORDER ITEM TYPES
// =====================================================

export interface OrderItem {
  id: number;
  order_id: number;
  menu_item_id?: number;
  name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  round_number?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface OrderWithItems extends Order {
  items: OrderItem[];
}

export interface OrderItemCreate {
  menu_item_id?: number;
  name: string;
  quantity: number;
  unit_price: number;
  round_number?: number;
  notes?: string;
}
