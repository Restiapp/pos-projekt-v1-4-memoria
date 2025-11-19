/**
 * Invoice Service - Számlázz.hu API hívások
 *
 * Backend endpoints (service_admin:8008):
 *   - POST /api/v1/integrations/szamlazz_hu/create-invoice
 *
 * Frontend hívások:
 *   - POST /api/integrations/szamlazz_hu/create-invoice → Vite proxy → http://localhost:8008/api/v1/integrations/szamlazz_hu/create-invoice
 */

import apiClient from './api';
import type {
  InvoiceCreateRequest,
  InvoiceCreateResponse,
} from '@/types/invoice';

/**
 * Számla létrehozása Számlázz.hu rendszerben
 * POST /api/integrations/szamlazz_hu/create-invoice
 * Proxy Target: http://localhost:8008/api/v1/integrations/szamlazz_hu/create-invoice
 */
export const createInvoice = async (
  request: InvoiceCreateRequest
): Promise<InvoiceCreateResponse> => {
  try {
    const response = await apiClient.post<InvoiceCreateResponse>(
      '/api/integrations/szamlazz_hu/create-invoice',
      request
    );
    return response.data;
  } catch (error) {
    console.error('Error creating invoice:', error);
    throw error;
  }
};
