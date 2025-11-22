/**
 * Payment és Order típusdefiníciók
 * Backend API sémáknak megfelelően (service_orders:8002)
 */

// Fizetési módok enum
export type PaymentMethod =
  | 'Készpénz'
  | 'Bankkártya'
  | 'OTP SZÉP'
  | 'K&H SZÉP'
  | 'MKB SZÉP';

// Fizetés típus (Backend PaymentResponse-nak megfelelő)
export interface Payment {
  id: number;
  order_id: number;
  payment_method: PaymentMethod;
  amount: number;
  created_at: string; // ISO datetime
}

// Fizetés létrehozás Request (Backend PaymentCreate-nek megfelelő)
export interface PaymentCreateRequest {
  order_id: number;
  payment_method: PaymentMethod;
  amount: number;
}

// Split-Check egy személyre (Backend SplitCheckItemSchema-nak megfelelő)
export interface SplitCheckItem {
  seat_id: number | null;
  seat_number: number | null;
  person_amount: number;
  item_count: number;
}

// Split-Check Response (Backend SplitCheckResponse-nak megfelelő)
export interface SplitCheckResponse {
  order_id: number;
  items: SplitCheckItem[];
  total_amount: number;
}

// Order típusok (Backend OrderResponse-nak megfelelő)
export type OrderType = 'Helyben' | 'Elvitel' | 'Kiszállítás';
export type OrderStatus = 'NYITOTT' | 'FELDOLGOZVA' | 'LEZART' | 'SZTORNÓ';

export interface Order {
  id: number;
  order_type: OrderType;
  status: OrderStatus;
  table_id: number | null;
  total_amount: number | null;
  final_vat_rate: number;
  ntak_data: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

// Kedvezmény típusok
export type DiscountType = 'PERCENTAGE' | 'FIXED_AMOUNT' | 'COUPON';

export interface AppliedDiscount {
  id: number;
  order_id?: number;
  item_id?: number;
  discount_type: DiscountType;
  discount_value: number;
  discount_amount: number; // Kalkulált kedvezmény összege HUF-ban
  coupon_code?: string;
  reason?: string;
  applied_at: string;
}
