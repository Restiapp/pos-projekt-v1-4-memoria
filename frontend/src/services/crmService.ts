/**
 * CRM Service - CRM API hívások (Customers, Coupons, Gift Cards)
 *
 * Backend endpoints (service_crm:8004):
 *   - GET /api/v1/customers
 *   - POST /api/v1/customers
 *   - PUT /api/v1/customers/{id}
 *   - DELETE /api/v1/customers/{id}
 *   - GET /api/v1/coupons
 *   - POST /api/v1/coupons
 *   - PUT /api/v1/coupons/{id}
 *   - DELETE /api/v1/coupons/{id}
 *   - GET /api/v1/gift_cards
 *   - POST /api/v1/gift_cards
 *   - PUT /api/v1/gift_cards/{id}
 *   - DELETE /api/v1/gift_cards/{id}
 *
 * Frontend hívások:
 *   - GET /api/customers → Vite proxy → http://localhost:8004/api/v1/customers
 *   - POST /api/customers → Vite proxy → http://localhost:8004/api/v1/customers
 */

import apiClient from './api';
import type {
  Customer,
  CustomerCreate,
  CustomerUpdate,
  CustomerListResponse,
  LoyaltyPointsUpdate,
} from '@/types/customer';
import type {
  Coupon,
  CouponCreate,
  CouponUpdate,
  CouponListResponse,
  CouponValidationRequest,
  CouponValidationResponse,
} from '@/types/coupon';
import type {
  GiftCard,
  GiftCardCreate,
  GiftCardUpdate,
  GiftCardListResponse,
  GiftCardRedemption,
  GiftCardRedemptionResponse,
  GiftCardBalanceUpdate,
} from '@/types/giftCard';

// =====================================================
// CUSTOMERS
// =====================================================

/**
 * GET /api/customers - Vendégek listája (lapozással)
 * Proxy Target: http://localhost:8004/api/v1/customers
 */
export const getCustomers = async (
  page: number = 1,
  page_size: number = 20,
  is_active?: boolean,
  search?: string
): Promise<CustomerListResponse> => {
  const params: Record<string, any> = { page, page_size };
  if (is_active !== undefined) {
    params.is_active = is_active;
  }
  if (search) {
    params.search = search;
  }

  const response = await apiClient.get<CustomerListResponse>('/api/customers', {
    params,
  });
  return response.data;
};

/**
 * GET /api/customers/{id} - Vendég részletei
 * Proxy Target: http://localhost:8004/api/v1/customers/{id}
 */
export const getCustomerById = async (id: number): Promise<Customer> => {
  const response = await apiClient.get<Customer>(`/api/customers/${id}`);
  return response.data;
};

/**
 * GET /api/customers/by-uid/{customer_uid} - Vendég keresése vendégszám alapján
 * Proxy Target: http://localhost:8004/api/v1/customers/by-uid/{customer_uid}
 */
export const getCustomerByUid = async (customer_uid: string): Promise<Customer | null> => {
  try {
    const response = await apiClient.get<Customer>(`/api/customers/by-uid/${customer_uid}`);
    return response.data;
  } catch (error: any) {
    // Return null if customer not found (404)
    if (error.response?.status === 404) {
      return null;
    }
    throw error;
  }
};

/**
 * POST /api/customers - Új vendég létrehozása
 * Proxy Target: http://localhost:8004/api/v1/customers
 */
export const createCustomer = async (
  customerData: CustomerCreate
): Promise<Customer> => {
  const response = await apiClient.post<Customer>('/api/customers', customerData);
  return response.data;
};

/**
 * PUT /api/customers/{id} - Vendég frissítése
 * Proxy Target: http://localhost:8004/api/v1/customers/{id}
 */
export const updateCustomer = async (
  id: number,
  customerData: CustomerUpdate
): Promise<Customer> => {
  const response = await apiClient.put<Customer>(
    `/api/customers/${id}`,
    customerData
  );
  return response.data;
};

/**
 * DELETE /api/customers/{id} - Vendég törlése
 * Proxy Target: http://localhost:8004/api/v1/customers/{id}
 */
export const deleteCustomer = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/customers/${id}`);
};

/**
 * POST /api/customers/{id}/loyalty_points - Hűségpontok módosítása
 * Proxy Target: http://localhost:8004/api/v1/customers/{id}/loyalty_points
 */
export const updateLoyaltyPoints = async (
  id: number,
  pointsData: LoyaltyPointsUpdate
): Promise<Customer> => {
  const response = await apiClient.post<Customer>(
    `/api/customers/${id}/loyalty_points`,
    pointsData
  );
  return response.data;
};

// =====================================================
// COUPONS
// =====================================================

/**
 * GET /api/coupons - Kuponok listája (lapozással)
 * Proxy Target: http://localhost:8004/api/v1/coupons
 */
export const getCoupons = async (
  page: number = 1,
  page_size: number = 20,
  is_active?: boolean
): Promise<CouponListResponse> => {
  const params: Record<string, any> = { page, page_size };
  if (is_active !== undefined) {
    params.is_active = is_active;
  }

  const response = await apiClient.get<CouponListResponse>('/api/coupons', {
    params,
  });
  return response.data;
};

/**
 * GET /api/coupons/{id} - Kupon részletei
 * Proxy Target: http://localhost:8004/api/v1/coupons/{id}
 */
export const getCouponById = async (id: number): Promise<Coupon> => {
  const response = await apiClient.get<Coupon>(`/api/coupons/${id}`);
  return response.data;
};

/**
 * POST /api/coupons - Új kupon létrehozása
 * Proxy Target: http://localhost:8004/api/v1/coupons
 */
export const createCoupon = async (couponData: CouponCreate): Promise<Coupon> => {
  const response = await apiClient.post<Coupon>('/api/coupons', couponData);
  return response.data;
};

/**
 * PUT /api/coupons/{id} - Kupon frissítése
 * Proxy Target: http://localhost:8004/api/v1/coupons/{id}
 */
export const updateCoupon = async (
  id: number,
  couponData: CouponUpdate
): Promise<Coupon> => {
  const response = await apiClient.put<Coupon>(
    `/api/coupons/${id}`,
    couponData
  );
  return response.data;
};

/**
 * DELETE /api/coupons/{id} - Kupon törlése
 * Proxy Target: http://localhost:8004/api/v1/coupons/{id}
 */
export const deleteCoupon = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/coupons/${id}`);
};

/**
 * POST /api/coupons/validate - Kupon validálása
 * Proxy Target: http://localhost:8004/api/v1/coupons/validate
 */
export const validateCoupon = async (
  validationData: CouponValidationRequest
): Promise<CouponValidationResponse> => {
  const response = await apiClient.post<CouponValidationResponse>(
    '/api/coupons/validate',
    validationData
  );
  return response.data;
};

// =====================================================
// GIFT CARDS
// =====================================================

/**
 * GET /api/gift_cards - Ajándékkártyák listája (lapozással)
 * Proxy Target: http://localhost:8004/api/v1/gift_cards
 */
export const getGiftCards = async (
  page: number = 1,
  page_size: number = 20,
  is_active?: boolean
): Promise<GiftCardListResponse> => {
  const params: Record<string, any> = { page, page_size };
  if (is_active !== undefined) {
    params.is_active = is_active;
  }

  const response = await apiClient.get<GiftCardListResponse>('/api/gift_cards', {
    params,
  });
  return response.data;
};

/**
 * GET /api/gift_cards/{id} - Ajándékkártya részletei
 * Proxy Target: http://localhost:8004/api/v1/gift_cards/{id}
 */
export const getGiftCardById = async (id: number): Promise<GiftCard> => {
  const response = await apiClient.get<GiftCard>(`/api/gift_cards/${id}`);
  return response.data;
};

/**
 * POST /api/gift_cards - Új ajándékkártya létrehozása
 * Proxy Target: http://localhost:8004/api/v1/gift_cards
 */
export const createGiftCard = async (
  giftCardData: GiftCardCreate
): Promise<GiftCard> => {
  const response = await apiClient.post<GiftCard>(
    '/api/gift_cards',
    giftCardData
  );
  return response.data;
};

/**
 * PUT /api/gift_cards/{id} - Ajándékkártya frissítése
 * Proxy Target: http://localhost:8004/api/v1/gift_cards/{id}
 */
export const updateGiftCard = async (
  id: number,
  giftCardData: GiftCardUpdate
): Promise<GiftCard> => {
  const response = await apiClient.put<GiftCard>(
    `/api/gift_cards/${id}`,
    giftCardData
  );
  return response.data;
};

/**
 * DELETE /api/gift_cards/{id} - Ajándékkártya törlése
 * Proxy Target: http://localhost:8004/api/v1/gift_cards/{id}
 */
export const deleteGiftCard = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/gift_cards/${id}`);
};

/**
 * POST /api/gift_cards/redeem - Ajándékkártya beváltása
 * Proxy Target: http://localhost:8004/api/v1/gift_cards/redeem
 */
export const redeemGiftCard = async (
  redemptionData: GiftCardRedemption
): Promise<GiftCardRedemptionResponse> => {
  const response = await apiClient.post<GiftCardRedemptionResponse>(
    '/api/gift_cards/redeem',
    redemptionData
  );
  return response.data;
};

/**
 * POST /api/gift_cards/{id}/balance - Ajándékkártya egyenleg módosítása
 * Proxy Target: http://localhost:8004/api/v1/gift_cards/{id}/balance
 */
export const updateGiftCardBalance = async (
  id: number,
  balanceData: GiftCardBalanceUpdate
): Promise<GiftCard> => {
  const response = await apiClient.post<GiftCard>(
    `/api/gift_cards/${id}/balance`,
    balanceData
  );
  return response.data;
};
