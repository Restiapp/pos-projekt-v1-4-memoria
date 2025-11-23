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
// ORDER ITEM TYPES
// =====================================================

export interface SelectedModifier {
  modifier_id: number;
  modifier_name?: string;
  price_adjustment: number;
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product_name?: string;
  seat_id?: number;
  quantity: number;
  unit_price: number;
  selected_modifiers?: SelectedModifier[];
  course?: string; // e.g., 'Előétel', 'Főétel', 'Desszert'
  notes?: string;
  kds_station?: string;
  kds_status: string;
  is_urgent?: boolean; // Priority flag for urgent items ✓ Backend supported
  round_number?: number; // NEW: for grouping items into rounds
  metadata?: {
    // TODO: Backend support needed - add metadata_json Column(CompatibleJSON) to OrderItem model
    course_tag?: string;
    sync_with_course?: string; // e.g., 'starter', 'main', 'dessert'
    [key: string]: any;
  };
  created_at?: string;
  updated_at?: string;
}

export interface CartItem {
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  is_urgent?: boolean;
  metadata?: {
    course_tag?: string;
    sync_with_course?: string;
    [key: string]: any;
  };
}

export interface OrderItemCreate {
  order_id: number;
  product_id: number;
  seat_id?: number;
  quantity: number;
  unit_price: number;
  selected_modifiers?: SelectedModifier[];
  course?: string;
  notes?: string;
  kds_status?: string;
  is_urgent?: boolean;
  metadata?: Record<string, any>;
}

export interface OrderItemUpdate {
  quantity?: number;
  unit_price?: number;
  selected_modifiers?: SelectedModifier[];
  course?: string;
  notes?: string;
  kds_status?: string;
  is_urgent?: boolean;
  metadata?: Record<string, any>;
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
    selected_modifiers?: SelectedModifier[];
    course?: string;
    notes?: string;
    kds_station?: string;
  }[];
  round_number: number;
}
