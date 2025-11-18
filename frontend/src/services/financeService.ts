/**
 * Finance Service - Pénzügyi API hívások
 *
 * Backend endpoints (service_admin:8008):
 *   - POST /api/v1/finance/cash-drawer/deposit
 *   - POST /api/v1/finance/cash-drawer/withdraw
 *   - GET /api/v1/finance/cash-drawer/balance
 *   - POST /api/v1/finance/daily-closures
 *   - PATCH /api/v1/finance/daily-closures/{id}/close
 *   - GET /api/v1/finance/daily-closures
 *   - GET /api/v1/finance/daily-closures/{id}
 *
 * Frontend hívások:
 *   - POST /api/finance/cash-drawer/deposit → Vite proxy → http://localhost:8008/api/v1/finance/cash-drawer/deposit
 *   - stb.
 */

import apiClient from './api';
import type {
  CashMovement,
  CashDepositRequest,
  CashWithdrawRequest,
  CashBalanceResponse,
  DailyClosure,
  DailyClosureCreateRequest,
  DailyClosureUpdateRequest,
} from '@/types/finance';

// ============================================================================
// Cash Drawer Operations (Pénztár műveletek)
// ============================================================================

/**
 * Készpénz befizetés rögzítése
 * POST /api/finance/cash-drawer/deposit
 * Proxy Target: http://localhost:8008/api/v1/finance/cash-drawer/deposit
 */
export const cashDeposit = async (
  request: CashDepositRequest
): Promise<CashMovement> => {
  try {
    const response = await apiClient.post<CashMovement>(
      '/api/finance/cash-drawer/deposit',
      request
    );
    return response.data;
  } catch (error) {
    console.error('Error recording cash deposit:', error);
    throw error;
  }
};

/**
 * Készpénz kivétel rögzítése
 * POST /api/finance/cash-drawer/withdraw
 * Proxy Target: http://localhost:8008/api/v1/finance/cash-drawer/withdraw
 */
export const cashWithdraw = async (
  request: CashWithdrawRequest
): Promise<CashMovement> => {
  try {
    const response = await apiClient.post<CashMovement>(
      '/api/finance/cash-drawer/withdraw',
      request
    );
    return response.data;
  } catch (error) {
    console.error('Error recording cash withdrawal:', error);
    throw error;
  }
};

/**
 * Aktuális készpénz egyenleg lekérdezése
 * GET /api/finance/cash-drawer/balance
 * Proxy Target: http://localhost:8008/api/v1/finance/cash-drawer/balance
 */
export const getCashBalance = async (): Promise<CashBalanceResponse> => {
  try {
    const response = await apiClient.get<CashBalanceResponse>(
      '/api/finance/cash-drawer/balance'
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching cash balance:', error);
    throw error;
  }
};

// ============================================================================
// Daily Closure Operations (Napi Zárás műveletek)
// ============================================================================

/**
 * Napi zárás létrehozása
 * POST /api/finance/daily-closures
 * Proxy Target: http://localhost:8008/api/v1/finance/daily-closures
 */
export const createDailyClosure = async (
  request: DailyClosureCreateRequest
): Promise<DailyClosure> => {
  try {
    const response = await apiClient.post<DailyClosure>(
      '/api/finance/daily-closures',
      request
    );
    return response.data;
  } catch (error) {
    console.error('Error creating daily closure:', error);
    throw error;
  }
};

/**
 * Napi zárás lezárása
 * PATCH /api/finance/daily-closures/{id}/close
 * Proxy Target: http://localhost:8008/api/v1/finance/daily-closures/{id}/close
 */
export const closeDailyClosure = async (
  closureId: number,
  request: DailyClosureUpdateRequest
): Promise<DailyClosure> => {
  try {
    const response = await apiClient.patch<DailyClosure>(
      `/api/finance/daily-closures/${closureId}/close`,
      request
    );
    return response.data;
  } catch (error) {
    console.error(`Error closing daily closure ${closureId}:`, error);
    throw error;
  }
};

/**
 * Napi zárások listázása szűrési feltételekkel
 * GET /api/finance/daily-closures
 * Proxy Target: http://localhost:8008/api/v1/finance/daily-closures
 */
export const getDailyClosures = async (params?: {
  start_date?: string;
  end_date?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<DailyClosure[]> => {
  try {
    const response = await apiClient.get<DailyClosure[]>(
      '/api/finance/daily-closures',
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching daily closures:', error);
    throw error;
  }
};

/**
 * Napi zárás részleteinek lekérdezése
 * GET /api/finance/daily-closures/{id}
 * Proxy Target: http://localhost:8008/api/v1/finance/daily-closures/{id}
 */
export const getDailyClosureById = async (
  closureId: number
): Promise<DailyClosure> => {
  try {
    const response = await apiClient.get<DailyClosure>(
      `/api/finance/daily-closures/${closureId}`
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching daily closure ${closureId}:`, error);
    throw error;
  }
};
