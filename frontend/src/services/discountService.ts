/**
 * Discount Service - Kedvezmény kezelés API hívások
 *
 * Backend endpoints:
 *   - POST /api/orders/{order_id}/apply-discount (rendelés szintű kedvezmény)
 *   - POST /api/orders/items/{item_id}/apply-discount (tétel szintű kedvezmény)
 *   - GET /api/coupons/validate (kuponkód validálás)
 *   - GET /api/coupons (kuponok listázása)
 */

import apiClient from './api';

// Kedvezmény típusok
export type DiscountType = 'PERCENTAGE' | 'FIXED_AMOUNT' | 'COUPON';

// Rendelés szintű kedvezmény alkalmazás request
export interface ApplyOrderDiscountRequest {
  discount_type: DiscountType;
  discount_value?: number; // Százalék (0-100) vagy fix összeg (HUF)
  coupon_code?: string; // Kuponkód (ha discount_type === 'COUPON')
  reason?: string; // Indoklás (opcionális)
}

// Tétel szintű kedvezmény alkalmazás request
export interface ApplyItemDiscountRequest {
  discount_type: DiscountType;
  discount_value?: number;
  coupon_code?: string;
  reason?: string;
}

// Kedvezmény alkalmazás response
export interface ApplyDiscountResponse {
  success: boolean;
  message: string;
  discount_amount: number; // Alkalmazott kedvezmény összege HUF-ban
  new_total: number; // Új összeg a kedvezmény után
  order_id?: number; // Rendelés ID (ha rendelés szintű)
  item_id?: number; // Tétel ID (ha tétel szintű)
}

// Kupon validálás request
export interface ValidateCouponRequest {
  code: string;
  order_amount: number;
  customer_id?: number;
}

// Kupon validálás response
export interface ValidateCouponResponse {
  valid: boolean;
  message: string;
  discount_amount: number | null;
  coupon: {
    id: number;
    code: string;
    discount_type: 'PERCENTAGE' | 'FIXED_AMOUNT';
    discount_value: number;
    description: string | null;
  } | null;
}

// Kupon lista item
export interface Coupon {
  id: number;
  code: string;
  description: string | null;
  discount_type: 'PERCENTAGE' | 'FIXED_AMOUNT';
  discount_value: number;
  min_purchase_amount: number | null;
  usage_limit: number | null;
  usage_count: number;
  valid_from: string;
  valid_until: string | null;
  is_active: boolean;
}

/**
 * Kedvezmény alkalmazása rendelésre
 * @param orderId - Rendelés azonosító
 * @param data - Kedvezmény adatok
 * @returns Kedvezmény alkalmazás eredménye
 */
export const applyDiscountToOrder = async (
  orderId: number,
  data: ApplyOrderDiscountRequest
): Promise<ApplyDiscountResponse> => {
  try {
    const response = await apiClient.post<ApplyDiscountResponse>(
      `/api/orders/${orderId}/apply-discount`,
      data
    );
    return response.data;
  } catch (error) {
    console.error(`Error applying discount to order ${orderId}:`, error);
    throw error;
  }
};

/**
 * Kedvezmény alkalmazása rendelési tételre
 * @param itemId - Tétel azonosító
 * @param data - Kedvezmény adatok
 * @returns Kedvezmény alkalmazás eredménye
 */
export const applyDiscountToItem = async (
  itemId: number,
  data: ApplyItemDiscountRequest
): Promise<ApplyDiscountResponse> => {
  try {
    const response = await apiClient.post<ApplyDiscountResponse>(
      `/api/orders/items/${itemId}/apply-discount`,
      data
    );
    return response.data;
  } catch (error) {
    console.error(`Error applying discount to item ${itemId}:`, error);
    throw error;
  }
};

/**
 * Kuponkód validálása
 * @param data - Validálási adatok (kuponkód, rendelés összeg, ügyfél ID)
 * @returns Validálás eredménye és kedvezmény számítás
 */
export const validateCoupon = async (
  data: ValidateCouponRequest
): Promise<ValidateCouponResponse> => {
  try {
    const response = await apiClient.post<ValidateCouponResponse>(
      `/api/coupons/validate`,
      data
    );
    return response.data;
  } catch (error) {
    console.error('Error validating coupon:', error);
    throw error;
  }
};

/**
 * Aktív kuponok lekérése
 * @param page - Oldal szám
 * @param pageSize - Oldal méret
 * @returns Kuponok listája
 */
export const getCoupons = async (
  page: number = 1,
  pageSize: number = 20
): Promise<{ items: Coupon[]; total: number }> => {
  try {
    const skip = (page - 1) * pageSize;
    const response = await apiClient.get<{ items: Coupon[]; total: number }>(
      `/api/coupons`,
      {
        params: {
          skip,
          limit: pageSize,
          is_active: true,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching coupons:', error);
    throw error;
  }
};
