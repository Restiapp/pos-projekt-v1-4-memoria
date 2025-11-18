/**
 * Gift Card típusok - Backend API sémákkal szinkronban
 * Backend: backend/service_crm/schemas/gift_card.py
 */

// Gift Card típusok

export interface GiftCard {
  id: number;
  card_code: string; // Unique gift card code (pl. "GIFT-2024-ABC123")
  pin_code?: string; // Optional PIN code for security
  initial_balance: number; // Decimal (2 places) - HUF
  current_balance: number; // Decimal (2 places) - HUF
  customer_id?: number; // null if unassigned
  purchased_by_customer_id?: number;
  purchase_order_id?: number;
  valid_until?: string; // ISO datetime string - null = no expiration
  is_active: boolean;
  issued_at: string; // ISO datetime string
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  last_used_at?: string; // ISO datetime string
  // Computed properties
  is_valid: boolean; // active, has balance, not expired
  is_assigned: boolean; // assigned to a customer
  usage_percentage: number; // 0-100%
}

export interface GiftCardCreate {
  card_code: string;
  pin_code?: string;
  initial_balance: number;
  customer_id?: number;
  purchased_by_customer_id?: number;
  purchase_order_id?: number;
  valid_until?: string; // ISO datetime string
  is_active: boolean;
}

export interface GiftCardUpdate {
  pin_code?: string;
  valid_until?: string;
  is_active?: boolean;
  customer_id?: number;
}

export interface GiftCardListResponse {
  items: GiftCard[];
  total: number;
  page: number;
  page_size: number;
}

export interface GiftCardRedemption {
  card_code: string;
  pin_code?: string;
  amount: number; // HUF amount to redeem
  order_id?: number;
}

export interface GiftCardRedemptionResponse {
  success: boolean;
  message: string;
  redeemed_amount?: number; // HUF
  remaining_balance?: number; // HUF
  gift_card?: GiftCard;
}

export interface GiftCardBalanceUpdate {
  amount: number; // Decimal - positive to add, negative to subtract
  reason?: string;
}
