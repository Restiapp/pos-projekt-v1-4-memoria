/**
 * Coupon típusok - Backend API sémákkal szinkronban
 * Backend: backend/service_crm/schemas/coupon.py
 */

// Discount Type Enum
export enum DiscountType {
  PERCENTAGE = 'PERCENTAGE',      // Százalékos kedvezmény (0-100%)
  FIXED_AMOUNT = 'FIXED_AMOUNT',  // Fix összegű kedvezmény (HUF)
}

// Coupon típusok

export interface Coupon {
  id: number;
  code: string; // Unique coupon code (pl. "WELCOME10")
  description?: string;
  discount_type: DiscountType;
  discount_value: number; // Decimal (2 places) - percentage (0-100) or HUF amount
  min_purchase_amount?: number; // Decimal (2 places) - minimum order value (HUF)
  usage_limit?: number; // null = unlimited
  usage_count: number; // Current usage count
  customer_id?: number; // null = public coupon
  valid_from: string; // ISO datetime string
  valid_until?: string; // ISO datetime string - null = no expiration
  is_active: boolean;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface CouponCreate {
  code: string;
  description?: string;
  discount_type: DiscountType;
  discount_value: number;
  min_purchase_amount?: number;
  usage_limit?: number;
  customer_id?: number;
  valid_from: string; // ISO datetime string
  valid_until?: string; // ISO datetime string
  is_active: boolean;
}

export interface CouponUpdate {
  description?: string;
  discount_type?: DiscountType;
  discount_value?: number;
  min_purchase_amount?: number;
  usage_limit?: number;
  valid_from?: string;
  valid_until?: string;
  is_active?: boolean;
}

export interface CouponListResponse {
  items: Coupon[];
  total: number;
  page: number;
  page_size: number;
}

export interface CouponValidationRequest {
  code: string;
  order_amount: number; // HUF
  customer_id?: number;
}

export interface CouponValidationResponse {
  valid: boolean;
  message: string;
  discount_amount?: number; // HUF (if valid)
  coupon?: Coupon;
}
