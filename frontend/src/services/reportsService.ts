/**
 * Reports Service - Dashboard Analytics API hívások
 *
 * Backend endpoints (service_admin:8008):
 *   - GET /api/v1/reports/sales
 *   - GET /api/v1/reports/top-products
 *   - GET /api/v1/reports/consumption
 *
 * Frontend hívások:
 *   - GET /api/reports/sales → Vite proxy → http://localhost:8008/api/v1/reports/sales
 *   - stb.
 */

import apiClient from './api';
import type {
  SalesReportResponse,
  TopProductsResponse,
  ConsumptionReportResponse,
  ReportQueryParams,
} from '@/types/reports';

// ============================================================================
// Sales Report Operations
// ============================================================================

/**
 * Értékesítési statisztikák lekérése (napi bontás)
 * GET /api/reports/sales
 * Proxy Target: http://localhost:8008/api/v1/reports/sales
 */
export const getSalesReport = async (
  params?: ReportQueryParams
): Promise<SalesReportResponse> => {
  try {
    const response = await apiClient.get<SalesReportResponse>(
      '/api/reports/sales',
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching sales report:', error);
    throw error;
  }
};

// ============================================================================
// Top Products Report Operations
// ============================================================================

/**
 * Top termékek lekérése eladott mennyiség alapján
 * GET /api/reports/top-products
 * Proxy Target: http://localhost:8008/api/v1/reports/top-products
 */
export const getTopProducts = async (
  params?: ReportQueryParams
): Promise<TopProductsResponse> => {
  try {
    const response = await apiClient.get<TopProductsResponse>(
      '/api/reports/top-products',
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching top products:', error);
    throw error;
  }
};

// ============================================================================
// Consumption Report Operations
// ============================================================================

/**
 * Készletfogyási riport lekérése
 * GET /api/reports/consumption
 * Proxy Target: http://localhost:8008/api/v1/reports/consumption
 */
export const getConsumptionReport = async (
  params?: ReportQueryParams
): Promise<ConsumptionReportResponse> => {
  try {
    const response = await apiClient.get<ConsumptionReportResponse>(
      '/api/reports/consumption',
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching consumption report:', error);
    throw error;
  }
};

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Formázza a dátumot YYYY-MM-DD formátumba
 */
export const formatDateForAPI = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

/**
 * Előre definiált időszakok generálása
 */
export const getDateRangePresets = () => {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const last7Days = new Date(today);
  last7Days.setDate(last7Days.getDate() - 7);

  const last30Days = new Date(today);
  last30Days.setDate(last30Days.getDate() - 30);

  const thisMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);

  const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);

  return {
    today: {
      start_date: formatDateForAPI(today),
      end_date: formatDateForAPI(today),
    },
    yesterday: {
      start_date: formatDateForAPI(yesterday),
      end_date: formatDateForAPI(yesterday),
    },
    last7Days: {
      start_date: formatDateForAPI(last7Days),
      end_date: formatDateForAPI(today),
    },
    last30Days: {
      start_date: formatDateForAPI(last30Days),
      end_date: formatDateForAPI(today),
    },
    thisMonth: {
      start_date: formatDateForAPI(thisMonthStart),
      end_date: formatDateForAPI(today),
    },
    lastMonth: {
      start_date: formatDateForAPI(lastMonthStart),
      end_date: formatDateForAPI(lastMonthEnd),
    },
  };
};
