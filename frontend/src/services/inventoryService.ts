/**
 * Inventory Service - API calls for inventory management
 *
 * Provides methods for:
 * - Inventory items CRUD
 * - Incoming invoices management
 * - Stock movements tracking
 * - Waste logging
 */

import apiClient from './api';

// ===== TYPES =====

export interface InventoryItem {
  id: number;
  name: string;
  unit: string;
  current_stock_perpetual: number;
  last_cost_per_unit: number | null;
}

export interface InventoryItemCreate {
  name: string;
  unit: string;
  current_stock_perpetual?: number;
  last_cost_per_unit?: number;
}

export interface InventoryItemUpdate {
  name?: string;
  unit?: string;
  current_stock_perpetual?: number;
  last_cost_per_unit?: number;
}

export interface InventoryItemListResponse {
  items: InventoryItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface OCRLineItem {
  item_name?: string;
  quantity?: number;
  unit?: string;
  unit_price?: number;
  total_price?: number;
}

export interface OCRData {
  raw_text?: string;
  supplier_name?: string;
  invoice_number?: string;
  invoice_date?: string;
  total_amount?: number;
  line_items?: OCRLineItem[];
  confidence_score?: number;
  additional_data?: Record<string, any>;
}

export interface SupplierInvoice {
  id: number;
  supplier_name: string | null;
  invoice_date: string | null;
  total_amount: number | null;
  status: string;
  ocr_data?: OCRData | null;
}

export interface SupplierInvoiceCreate {
  supplier_name?: string;
  invoice_date?: string;
  total_amount?: number;
  status?: string;
  ocr_data?: OCRData;
}

export interface SupplierInvoiceListResponse {
  items: SupplierInvoice[];
  total: number;
  page: number;
  page_size: number;
}

export interface StockMovement {
  id: number;
  inventory_item_id: number;
  inventory_item_name?: string;
  quantity_change: number;
  reason: string;
  movement_date: string;
  user_name?: string;
  notes?: string;
}

export interface WasteLog {
  id: number;
  inventory_item_id: number;
  inventory_item_name?: string;
  quantity: number;
  reason: string;
  waste_date: string;
  noted_by?: string;
  notes?: string;
}

export interface WasteLogCreate {
  inventory_item_id: number;
  quantity: number;
  reason: string;
  waste_date?: string;
  noted_by?: string;
  notes?: string;
}

// ===== INVENTORY ITEMS API =====

export const getInventoryItems = async (
  page = 1,
  limit = 20,
  nameFilter?: string
): Promise<InventoryItemListResponse> => {
  const params: Record<string, any> = {
    skip: (page - 1) * limit,
    limit,
  };

  if (nameFilter) {
    params.name_filter = nameFilter;
  }

  const response = await apiClient.get('/api/inventory/items', { params });
  return response.data;
};

export const getInventoryItem = async (id: number): Promise<InventoryItem> => {
  const response = await apiClient.get(`/api/inventory/items/${id}`);
  return response.data;
};

export const createInventoryItem = async (
  data: InventoryItemCreate
): Promise<InventoryItem> => {
  const response = await apiClient.post('/api/inventory/items', data);
  return response.data;
};

export const updateInventoryItem = async (
  id: number,
  data: InventoryItemUpdate
): Promise<InventoryItem> => {
  const response = await apiClient.patch(`/api/inventory/items/${id}`, data);
  return response.data;
};

export const deleteInventoryItem = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/inventory/items/${id}`);
};

export const updateItemStock = async (
  id: number,
  quantityChange: number,
  newCostPerUnit?: number
): Promise<InventoryItem> => {
  const response = await apiClient.post(`/api/inventory/items/${id}/stock`, {
    quantity_change: quantityChange,
    new_cost_per_unit: newCostPerUnit,
  });
  return response.data;
};

export const getLowStockItems = async (
  threshold = 10.0
): Promise<InventoryItem[]> => {
  const response = await apiClient.get('/api/inventory/items/reports/low-stock', {
    params: { threshold },
  });
  return response.data;
};

export const getTotalInventoryValue = async (): Promise<{
  total_value: number;
  currency: string;
}> => {
  const response = await apiClient.get('/api/inventory/items/reports/total-value');
  return response.data;
};

// ===== SUPPLIER INVOICES API =====

export const getSupplierInvoices = async (
  page = 1,
  limit = 20
): Promise<SupplierInvoiceListResponse> => {
  // Note: This endpoint might need to be implemented in backend
  const params = {
    skip: (page - 1) * limit,
    limit,
  };

  try {
    const response = await apiClient.get('/api/inventory/invoices', { params });
    return response.data;
  } catch (error: any) {
    // If endpoint doesn't exist yet, return mock data
    if (error.response?.status === 404) {
      return {
        items: [],
        total: 0,
        page,
        page_size: limit,
      };
    }
    throw error;
  }
};

export const getSupplierInvoice = async (id: number): Promise<SupplierInvoice> => {
  const response = await apiClient.get(`/api/inventory/invoices/${id}`);
  return response.data;
};

export const createSupplierInvoice = async (
  data: SupplierInvoiceCreate
): Promise<SupplierInvoice> => {
  const response = await apiClient.post('/api/inventory/invoices', data);
  return response.data;
};

export const uploadInvoice = async (file: File): Promise<SupplierInvoice> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/api/inventory/invoices/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const finalizeInvoice = async (id: number): Promise<SupplierInvoice> => {
  // Note: This endpoint might need to be implemented in backend
  try {
    const response = await apiClient.post(`/api/inventory/invoices/${id}/finalize`);
    return response.data;
  } catch (error: any) {
    // If endpoint doesn't exist, just update status
    if (error.response?.status === 404) {
      const response = await apiClient.patch(`/api/inventory/invoices/${id}`, {
        status: 'VÉGLEGESÍTVE',
      });
      return response.data;
    }
    throw error;
  }
};

export const updateSupplierInvoice = async (
  id: number,
  data: Partial<SupplierInvoiceCreate>
): Promise<SupplierInvoice> => {
  const response = await apiClient.patch(`/api/inventory/invoices/${id}`, data);
  return response.data;
};

export const deleteSupplierInvoice = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/inventory/invoices/${id}`);
};

// ===== STOCK MOVEMENTS API =====

export const getStockMovements = async (
  page = 1,
  limit = 20,
  itemId?: number,
  reason?: string
): Promise<{
  items: StockMovement[];
  total: number;
  page: number;
  page_size: number;
}> => {
  // Note: This endpoint might need to be implemented in backend
  const params: Record<string, any> = {
    skip: (page - 1) * limit,
    limit,
  };

  if (itemId) params.item_id = itemId;
  if (reason) params.reason = reason;

  try {
    const response = await apiClient.get('/api/inventory/movements', { params });
    return response.data;
  } catch (error: any) {
    // If endpoint doesn't exist yet, return mock data
    if (error.response?.status === 404) {
      return {
        items: [],
        total: 0,
        page,
        page_size: limit,
      };
    }
    throw error;
  }
};

// ===== WASTE LOGS API =====

export const getWasteLogs = async (
  page = 1,
  limit = 20,
  itemId?: number
): Promise<{
  items: WasteLog[];
  total: number;
  page: number;
  page_size: number;
}> => {
  // Note: This endpoint might need to be implemented in backend
  const params: Record<string, any> = {
    skip: (page - 1) * limit,
    limit,
  };

  if (itemId) params.item_id = itemId;

  try {
    const response = await apiClient.get('/api/inventory/waste', { params });
    return response.data;
  } catch (error: any) {
    // If endpoint doesn't exist yet, return mock data
    if (error.response?.status === 404) {
      return {
        items: [],
        total: 0,
        page,
        page_size: limit,
      };
    }
    throw error;
  }
};

export const createWasteLog = async (
  data: WasteLogCreate
): Promise<WasteLog> => {
  const response = await apiClient.post('/api/inventory/waste', data);
  return response.data;
};

export const deleteWasteLog = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/inventory/waste/${id}`);
};
