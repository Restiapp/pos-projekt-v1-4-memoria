/**
 * Invoice Service - Számlázás API hívások
 *
 * Backend endpoints (service_admin:8001):
 *   - POST /api/integrations/szamlazz_hu/create-invoice
 *   - POST /api/integrations/szamlazz_hu/cancel-invoice
 *   - GET /api/integrations/szamlazz_hu/invoice/{invoice_number}/pdf
 */

import apiClient from './api';

// Számla tétel
export interface InvoiceItem {
  name: string;
  quantity: number;
  unit: string; // 'db', 'kg', 'l', stb.
  unit_price: number; // Bruttó egységár
  vat_rate: number; // ÁFA kulcs (%)
}

// Számla létrehozás request
export interface CreateInvoiceRequest {
  order_id: number;
  customer_name: string;
  customer_email?: string;
  items: InvoiceItem[];
  payment_method: 'CASH' | 'CARD' | 'TRANSFER';
  notes?: string;
}

// Számla létrehozás response
export interface CreateInvoiceResponse {
  success: boolean;
  invoice_number: string | null;
  pdf_url: string | null;
  message: string | null;
  order_id: number;
}

// Számla sztornózás request
export interface CancelInvoiceRequest {
  invoice_number: string;
  reason?: string;
}

// Számla sztornózás response
export interface CancelInvoiceResponse {
  success: boolean;
  message: string;
  invoice_number: string;
}

/**
 * Számla létrehozása Számlázz.hu rendszerben
 * @param data - Számla adatok
 * @returns Számla létrehozás eredménye
 */
export const createInvoice = async (
  data: CreateInvoiceRequest
): Promise<CreateInvoiceResponse> => {
  try {
    const response = await apiClient.post<CreateInvoiceResponse>(
      `/api/integrations/szamlazz_hu/create-invoice`,
      data
    );
    return response.data;
  } catch (error) {
    console.error('Error creating invoice:', error);
    throw error;
  }
};

/**
 * Számla sztornózása
 * @param invoiceNumber - Számla azonosító
 * @param reason - Sztornózás indoka (opcionális)
 * @returns Sztornózás eredménye
 */
export const cancelInvoice = async (
  invoiceNumber: string,
  reason?: string
): Promise<CancelInvoiceResponse> => {
  try {
    const response = await apiClient.post<CancelInvoiceResponse>(
      `/api/integrations/szamlazz_hu/cancel-invoice`,
      { invoice_number: invoiceNumber, reason }
    );
    return response.data;
  } catch (error) {
    console.error(`Error canceling invoice ${invoiceNumber}:`, error);
    throw error;
  }
};

/**
 * Számla PDF letöltése
 * @param invoiceNumber - Számla azonosító
 * @returns PDF URL
 */
export const getInvoicePdf = async (invoiceNumber: string): Promise<string> => {
  try {
    const response = await apiClient.get<{ pdf_url: string }>(
      `/api/integrations/szamlazz_hu/invoice/${invoiceNumber}/pdf`
    );
    return response.data.pdf_url;
  } catch (error) {
    console.error(`Error fetching invoice PDF ${invoiceNumber}:`, error);
    throw error;
  }
};

/**
 * Számlázz.hu kapcsolat ellenőrzése
 * @returns Kapcsolat státusza
 */
export const checkInvoiceServiceHealth = async (): Promise<{
  connected: boolean;
  message: string;
}> => {
  try {
    const response = await apiClient.get<{
      connected: boolean;
      message: string;
    }>(`/api/integrations/szamlazz_hu/health`);
    return response.data;
  } catch (error) {
    console.error('Error checking invoice service health:', error);
    throw error;
  }
};
