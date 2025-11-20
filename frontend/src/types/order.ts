/**
 * Order típusok - Backend API sémákkal szinkronban
 * Backend: backend/service_orders/schemas/
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
  table_id: number | null;
  customer_id: number | null;
  courier_id: number | null; // V4.0: Futár hivatkozás
  total_amount: number | null;
  final_vat_rate: number;
  ntak_data: Record<string, any> | null;
  notes: string | null;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface OrderListResponse {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
}
