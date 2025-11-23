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
// ORDER ITEMS & ROUNDS
// =====================================================

export type KDSStatus = 'WAITING' | 'PREPARING' | 'READY' | 'SERVED' | 'CANCELLED';

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product_name?: string; // populated from product service
  seat_id?: number;
  quantity: number;
  unit_price: number;
  selected_modifiers?: Array<{
    group_name: string;
    modifier_name: string;
    price: number;
  }>;
  course?: string; // 'Előétel', 'Főétel', 'Desszert'
  notes?: string;
  kds_station?: string; // 'GRILL', 'COLD', 'BAR', 'PULT'
  kds_status: KDSStatus;
  is_urgent?: boolean;
  round_number?: number; // NEW: for grouping items into rounds
  created_at?: string;
  updated_at?: string;
}

export interface OrderWithItems extends Order {
  items: OrderItem[];
}

export interface Round {
  round_number: number;
  items: OrderItem[];
  status?: 'OPEN' | 'SENT_TO_KDS' | 'READY'; // frontend-only status tracking
}

export interface AddItemsToRoundRequest {
  items: {
    product_id: number;
    quantity: number;
    unit_price: number;
    selected_modifiers?: Array<{
      group_name: string;
      modifier_name: string;
      price: number;
    }>;
    course?: string;
    notes?: string;
    kds_station?: string;
  }[];
  round_number: number;
}
