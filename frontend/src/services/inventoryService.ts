/**
 * Inventory Service - Raktár API hívások
 *
 * Backend endpoints (service_inventory:8007):
 *   - GET/POST/PATCH/DELETE /api/v1/inventory/items
 *   - POST /api/v1/invoices/upload
 *   - POST /api/v1/invoices/{id}/finalize
 *   - GET/POST/PUT/DELETE /api/v1/inventory/daily-counts
 *   - POST /api/v1/inventory/waste
 *
 * Frontend hívások:
 *   - /api/inventory/* → Vite proxy → http://localhost:8007/api/v1/inventory/*
 *   - /api/invoices/* → Vite proxy → http://localhost:8007/api/v1/invoices/*
 */

import apiClient from './api';
import type {
  InventoryItem,
  InventoryItemCreateRequest,
  InventoryItemUpdateRequest,
  StockUpdateRequest,
  SupplierInvoice,
  FinalizeInvoiceRequest,
  DailyInventorySheet,
  DailyInventoryCount,
  DailyInventoryCountCreateRequest,
  DailyInventoryCountUpdateRequest,
  WasteLog,
  WasteLogCreateRequest,
  LowStockItem,
  InventoryValueResponse,
} from '@/types/inventory';

// TODO-S0-STUB: Re-export types for components that need them
export type {
  InventoryItem,
  InventoryItemCreateRequest as InventoryItemCreate,
  InventoryItemUpdateRequest as InventoryItemUpdate,
  SupplierInvoice,
  SupplierInvoice as SupplierInvoiceCreate,
  WasteLog,
  WasteLogCreateRequest as WasteLogCreate,
  StockUpdateRequest as StockMovement,
};

// ============================================================================
// Inventory Items Operations (Raktári tételek)
// ============================================================================

/**
 * Raktári tételek listázása
 * GET /api/inventory/items
 */
export const getInventoryItems = async (params?: {
  category?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<InventoryItem[]> => {
  try {
    const response = await apiClient.get<InventoryItem[]>(
      '/api/inventory/items',
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching inventory items:', error);
    throw error;
  }
};

/**
 * Raktári tétel lekérdezése ID alapján
 * GET /api/inventory/items/{id}
 */
export const getInventoryItemById = async (
  itemId: number
): Promise<InventoryItem> => {
  try {
    const response = await apiClient.get<InventoryItem>(
      `/api/inventory/items/${itemId}`
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching inventory item ${itemId}:`, error);
    throw error;
  }
};

/**
 * Új raktári tétel létrehozása
 * POST /api/inventory/items
 */
export const createInventoryItem = async (
  request: InventoryItemCreateRequest
): Promise<InventoryItem> => {
  try {
    const response = await apiClient.post<InventoryItem>(
      '/api/inventory/items',
      request
    );
    return response.data;
  } catch (error) {
    console.error('Error creating inventory item:', error);
    throw error;
  }
};

/**
 * Raktári tétel frissítése
 * PATCH /api/inventory/items/{id}
 */
export const updateInventoryItem = async (
  itemId: number,
  request: InventoryItemUpdateRequest
): Promise<InventoryItem> => {
  try {
    const response = await apiClient.patch<InventoryItem>(
      `/api/inventory/items/${itemId}`,
      request
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating inventory item ${itemId}:`, error);
    throw error;
  }
};

/**
 * Raktári tétel törlése
 * DELETE /api/inventory/items/{id}
 */
export const deleteInventoryItem = async (itemId: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/inventory/items/${itemId}`);
  } catch (error) {
    console.error(`Error deleting inventory item ${itemId}:`, error);
    throw error;
  }
};

/**
 * Készlet módosítása (növelés/csökkentés)
 * POST /api/inventory/items/{id}/stock
 */
export const updateStock = async (
  itemId: number,
  request: StockUpdateRequest
): Promise<InventoryItem> => {
  try {
    const response = await apiClient.post<InventoryItem>(
      `/api/inventory/items/${itemId}/stock`,
      request
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating stock for item ${itemId}:`, error);
    throw error;
  }
};

/**
 * Alacsony készletű tételek lekérdezése
 * GET /api/inventory/items/reports/low-stock
 */
export const getLowStockItems = async (): Promise<LowStockItem[]> => {
  try {
    const response = await apiClient.get<LowStockItem[]>(
      '/api/inventory/items/reports/low-stock'
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching low stock items:', error);
    throw error;
  }
};

/**
 * Összes készlet érték lekérdezése
 * GET /api/inventory/items/reports/total-value
 */
export const getTotalInventoryValue = async (): Promise<InventoryValueResponse> => {
  try {
    const response = await apiClient.get<InventoryValueResponse>(
      '/api/inventory/items/reports/total-value'
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching total inventory value:', error);
    throw error;
  }
};

// ============================================================================
// Supplier Invoices Operations (Szállítói számlák - OCR)
// ============================================================================

/**
 * Számla feltöltése OCR feldolgozásra
 * POST /api/invoices/upload
 */
export const uploadInvoice = async (file: File): Promise<SupplierInvoice> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<SupplierInvoice>(
      '/api/invoices/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error uploading invoice:', error);
    throw error;
  }
};

/**
 * Számla véglegesítése
 * POST /api/invoices/{id}/finalize
 */
export const finalizeInvoice = async (
  invoiceId: number,
  request?: FinalizeInvoiceRequest
): Promise<SupplierInvoice> => {
  try {
    const response = await apiClient.post<SupplierInvoice>(
      `/api/invoices/${invoiceId}/finalize`,
      request || {}
    );
    return response.data;
  } catch (error) {
    console.error(`Error finalizing invoice ${invoiceId}:`, error);
    throw error;
  }
};

/**
 * Számlák listázása
 * GET /api/invoices
 */
export const getInvoices = async (params?: {
  ocr_status?: string;
  finalized?: boolean;
  limit?: number;
  offset?: number;
}): Promise<SupplierInvoice[]> => {
  try {
    const response = await apiClient.get<SupplierInvoice[]>(
      '/api/invoices',
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching invoices:', error);
    throw error;
  }
};

// ============================================================================
// Daily Inventory Counts Operations (Leltár - Napi számlálások)
// ============================================================================

/**
 * Leltár sablonok listázása
 * GET /api/inventory/daily-sheets
 */
export const getDailyInventorySheets = async (params?: {
  is_active?: boolean;
  limit?: number;
  offset?: number;
}): Promise<DailyInventorySheet[]> => {
  try {
    const response = await apiClient.get<DailyInventorySheet[]>(
      '/api/inventory/daily-sheets',
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching daily inventory sheets:', error);
    throw error;
  }
};

/**
 * Leltár számlálások listázása
 * GET /api/inventory/daily-counts
 */
export const getDailyInventoryCounts = async (params?: {
  sheet_id?: number;
  start_date?: string;
  end_date?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<DailyInventoryCount[]> => {
  try {
    const response = await apiClient.get<DailyInventoryCount[]>(
      '/api/inventory/daily-counts',
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching daily inventory counts:', error);
    throw error;
  }
};

/**
 * Leltár számlálás lekérdezése ID alapján
 * GET /api/inventory/daily-counts/{id}
 */
export const getDailyInventoryCountById = async (
  countId: number
): Promise<DailyInventoryCount> => {
  try {
    const response = await apiClient.get<DailyInventoryCount>(
      `/api/inventory/daily-counts/${countId}`
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching daily inventory count ${countId}:`, error);
    throw error;
  }
};

/**
 * Új leltár számlálás létrehozása
 * POST /api/inventory/daily-counts
 */
export const createDailyInventoryCount = async (
  request: DailyInventoryCountCreateRequest
): Promise<DailyInventoryCount> => {
  try {
    const response = await apiClient.post<DailyInventoryCount>(
      '/api/inventory/daily-counts',
      request
    );
    return response.data;
  } catch (error) {
    console.error('Error creating daily inventory count:', error);
    throw error;
  }
};

/**
 * Leltár számlálás frissítése
 * PUT /api/inventory/daily-counts/{id}
 */
export const updateDailyInventoryCount = async (
  countId: number,
  request: DailyInventoryCountUpdateRequest
): Promise<DailyInventoryCount> => {
  try {
    const response = await apiClient.put<DailyInventoryCount>(
      `/api/inventory/daily-counts/${countId}`,
      request
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating daily inventory count ${countId}:`, error);
    throw error;
  }
};

/**
 * Leltár számlálás törlése
 * DELETE /api/inventory/daily-counts/{id}
 */
export const deleteDailyInventoryCount = async (countId: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/inventory/daily-counts/${countId}`);
  } catch (error) {
    console.error(`Error deleting daily inventory count ${countId}:`, error);
    throw error;
  }
};

/**
 * Leltár véglegesítése (státusz frissítés)
 * PUT /api/inventory/daily-counts/{id}
 */
export const finalizeInventoryCount = async (
  countId: number
): Promise<DailyInventoryCount> => {
  try {
    const response = await apiClient.put<DailyInventoryCount>(
      `/api/inventory/daily-counts/${countId}`,
      { status: 'finalized' }
    );
    return response.data;
  } catch (error) {
    console.error(`Error finalizing inventory count ${countId}:`, error);
    throw error;
  }
};

// ============================================================================
// Waste Logging Operations (Selejt naplózás)
// ============================================================================

/**
 * Selejt naplók listázása
 * GET /api/inventory/waste
 */
export const getWasteLogs = async (params?: {
  inventory_item_id?: number;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}): Promise<WasteLog[]> => {
  try {
    const response = await apiClient.get<WasteLog[]>(
      '/api/inventory/waste',
      { params }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching waste logs:', error);
    throw error;
  }
};

/**
 * Új selejt bejegyzés létrehozása
 * POST /api/inventory/waste
 */
export const createWasteLog = async (
  request: WasteLogCreateRequest
): Promise<WasteLog> => {
  try {
    const response = await apiClient.post<WasteLog>(
      '/api/inventory/waste',
      request
    );
    return response.data;
  } catch (error) {
    console.error('Error creating waste log:', error);
    throw error;
  }
};

// ============================================================================
// TODO-S0-STUB: Missing service functions
// These are temporary stubs for functions referenced but not implemented
// ============================================================================

/**
 * TODO-S0-STUB: Get supplier invoices
 */
export const getSupplierInvoices = async (params?: {
  limit?: number;
  offset?: number;
}): Promise<SupplierInvoice[]> => {
  console.warn('TODO-S0-STUB: getSupplierInvoices needs real implementation');
  return getInvoices(params);
};

/**
 * TODO-S0-STUB: Delete supplier invoice
 */
export const deleteSupplierInvoice = async (invoiceId: number): Promise<void> => {
  console.warn('TODO-S0-STUB: deleteSupplierInvoice needs real implementation');
  // Stub - no actual implementation
};

/**
 * TODO-S0-STUB: Create supplier invoice
 */
export const createSupplierInvoice = async (request: any): Promise<SupplierInvoice> => {
  console.warn('TODO-S0-STUB: createSupplierInvoice needs real implementation');
  return uploadInvoice(request.file);
};

/**
 * TODO-S0-STUB: Get stock movements
 */
export const getStockMovements = async (params?: {
  limit?: number;
  offset?: number;
}): Promise<any[]> => {
  console.warn('TODO-S0-STUB: getStockMovements needs real implementation');
  return [];
};

/**
 * TODO-S0-STUB: Delete waste log
 */
export const deleteWasteLog = async (wasteId: number): Promise<void> => {
  console.warn('TODO-S0-STUB: deleteWasteLog needs real implementation');
  // Stub - no actual implementation
};
