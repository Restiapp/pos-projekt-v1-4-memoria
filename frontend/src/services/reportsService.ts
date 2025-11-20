/**
 * Reports Service - Analytics & Reporting API
 * Szolgáltatás a riportok és statisztikák lekérdezéséhez
 */

import apiClient from './api';
import type { ReportsResponse, DateRange } from '@/types/reports';

/**
 * Analitikai adatok lekérdezése dátumtartományra
 *
 * @param dateRange - Kezdő és záró dátum
 * @returns ReportsResponse - Teljes riport adatok
 */
export async function getReportsData(dateRange: DateRange): Promise<ReportsResponse> {
  const params = new URLSearchParams({
    start_date: dateRange.start_date,
    end_date: dateRange.end_date,
  });

  const response = await apiClient.get<ReportsResponse>(
    `/api/reports?${params.toString()}`
  );

  return response.data;
}

/**
 * Napi értékesítési adatok lekérdezése
 *
 * @param dateRange - Kezdő és záró dátum
 * @returns Napi bontású értékesítési adatok
 */
export async function getDailySales(dateRange: DateRange) {
  const params = new URLSearchParams({
    start_date: dateRange.start_date,
    end_date: dateRange.end_date,
  });

  const response = await apiClient.get(
    `/api/reports/daily-sales?${params.toString()}`
  );

  return response.data;
}

/**
 * Top termékek lekérdezése
 *
 * @param dateRange - Kezdő és záró dátum
 * @param limit - Maximum termékek száma (alapértelmezett: 10)
 * @returns Top termékek listája
 */
export async function getTopProducts(dateRange: DateRange, limit: number = 10) {
  const params = new URLSearchParams({
    start_date: dateRange.start_date,
    end_date: dateRange.end_date,
    limit: limit.toString(),
  });

  const response = await apiClient.get(
    `/api/reports/top-products?${params.toString()}`
  );

  return response.data;
}

/**
 * Alapanyag-felhasználás lekérdezése
 *
 * @param dateRange - Kezdő és záró dátum
 * @returns Alapanyag-felhasználási adatok
 */
export async function getIngredientConsumption(dateRange: DateRange) {
  const params = new URLSearchParams({
    start_date: dateRange.start_date,
    end_date: dateRange.end_date,
  });

  const response = await apiClient.get(
    `/api/reports/ingredient-consumption?${params.toString()}`
  );

  return response.data;
}

/**
 * Exportálási funkció (CSV, Excel)
 *
 * @param dateRange - Kezdő és záró dátum
 * @param format - Export formátum ('csv' | 'excel')
 */
export async function exportReport(dateRange: DateRange, format: 'csv' | 'excel') {
  const params = new URLSearchParams({
    start_date: dateRange.start_date,
    end_date: dateRange.end_date,
    format,
  });

  const response = await apiClient.get(
    `/api/reports/export?${params.toString()}`,
    { responseType: 'blob' }
  );

  // Fájl letöltése
  const blob = new Blob([response.data]);
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `report_${dateRange.start_date}_${dateRange.end_date}.${format}`;
  link.click();
  window.URL.revokeObjectURL(url);
}

const reportsService = {
  getReportsData,
  getDailySales,
  getTopProducts,
  getIngredientConsumption,
  exportReport,
};

export default reportsService;
