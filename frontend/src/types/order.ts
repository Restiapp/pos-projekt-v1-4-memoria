/**
 * Order Types - Backend API sémákkal szinkronban
 * Backend: backend/service_orders/schemas/order.py
 * Backend: backend/service_orders/schemas/order_item.py
 */

// Order Type Enum
export enum OrderTypeEnum {
  HELYBEN = "Helyben",
  ELVITEL = "Elvitel",
  KISZALLITAS = "Kiszállítás",
}

// Order Status Enum
export enum OrderStatusEnum {
  NYITOTT = "NYITOTT",
  FELDOLGOZVA = "FELDOLGOZVA",
  LEZART = "LEZART",
  SZTORNO = "SZTORNÓ",
}

// Selected Modifier Schema
export interface SelectedModifier {
  group_name: string;
  modifier_name: string;
  price: number;
}

// Order Item Types
export interface OrderItemBase {
  order_id: number;
  product_id: number;
  seat_id?: number;
  quantity: number;
  unit_price: number;
  selected_modifiers?: SelectedModifier[];
  course?: string;
  notes?: string;
  kds_station?: string;
  kds_status?: string;
}

export interface OrderItemCreate extends OrderItemBase {}

export interface OrderItemUpdate {
  order_id?: number;
  product_id?: number;
  seat_id?: number;
  quantity?: number;
  unit_price?: number;
  selected_modifiers?: SelectedModifier[];
  course?: string;
  notes?: string;
  kds_station?: string;
  kds_status?: string;
}

export interface OrderItem extends OrderItemBase {
  id: number;
}

export interface OrderItemResponse extends OrderItem {}

// Order Types
export interface OrderBase {
  order_type: OrderTypeEnum | string;
  status: OrderStatusEnum | string;
  table_id?: number;
  customer_id?: number;
  total_amount?: number;
  final_vat_rate: number;
  ntak_data?: Record<string, any>;
  notes?: string;
}

export interface OrderCreate extends OrderBase {}

export interface OrderUpdate {
  order_type?: OrderTypeEnum | string;
  status?: OrderStatusEnum | string;
  table_id?: number;
  customer_id?: number;
  total_amount?: number;
  final_vat_rate?: number;
  ntak_data?: Record<string, any>;
  notes?: string;
}

export interface Order extends OrderBase {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface OrderResponse extends Order {}

export interface OrderListResponse {
  items: OrderResponse[];
  total: number;
  page: number;
  page_size: number;
}

// Cart Item (for local state management in the UI)
export interface CartItem {
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}
