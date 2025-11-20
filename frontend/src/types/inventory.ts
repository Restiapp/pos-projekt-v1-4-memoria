/**
 * Inventory (Raktár) típusdefiníciók
 * Backend API sémáknak megfelelően
 * Backend: backend/service_inventory/schemas/
 */

/**
 * InventoryItem (Raktári tétel) - Backend API response
 */
export interface InventoryItem {
  id: number;
  name: string;
  sku?: string | null;
  category?: string | null;
  unit: string; // "kg" | "l" | "db" stb.
  current_stock: number;
  min_stock_level?: number | null;
  max_stock_level?: number | null;
  unit_price?: number | null;
  supplier?: string | null;
  storage_location?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Raktári tétel létrehozása (POST /inventory/items)
 */
export interface InventoryItemCreateRequest {
  name: string;
  sku?: string;
  category?: string;
  unit: string;
  current_stock: number;
  min_stock_level?: number;
  max_stock_level?: number;
  unit_price?: number;
  supplier?: string;
  storage_location?: string;
  notes?: string;
}

/**
 * Raktári tétel frissítése (PATCH /inventory/items/{id})
 */
export interface InventoryItemUpdateRequest {
  name?: string;
  sku?: string;
  category?: string;
  unit?: string;
  min_stock_level?: number;
  max_stock_level?: number;
  unit_price?: number;
  supplier?: string;
  storage_location?: string;
  notes?: string;
}

/**
 * Készlet módosítás (POST /inventory/items/{id}/stock)
 */
export interface StockUpdateRequest {
  quantity: number;
  operation: 'increase' | 'decrease';
  reason?: string;
}

/**
 * SupplierInvoice (Szállítói számla OCR) - Backend API response
 */
export interface SupplierInvoice {
  id: number;
  invoice_number?: string | null;
  supplier_name?: string | null;
  invoice_date?: string | null;
  total_amount?: number | null;
  currency?: string | null;
  file_path?: string | null;
  ocr_status: string; // "pending" | "processing" | "completed" | "failed"
  ocr_result?: any | null;
  finalized: boolean;
  finalized_at?: string | null;
  finalized_by_employee_id?: number | null;
  created_at: string;
  updated_at: string;
}

/**
 * Számla véglegesítése (POST /invoices/{id}/finalize)
 */
export interface FinalizeInvoiceRequest {
  employee_id?: number;
}

/**
 * DailyInventorySheet (Leltár sablon) - Backend API response
 */
export interface DailyInventorySheet {
  id: number;
  sheet_name: string;
  description?: string | null;
  item_ids: number[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * DailyInventoryCount (Leltár - Napi számlálás) - Backend API response
 */
export interface DailyInventoryCount {
  id: number;
  sheet_id: number;
  count_date: string;
  counted_by_employee_id?: number | null;
  counts: Record<string, number>; // { "item_id": counted_quantity }
  notes?: string | null;
  status: string; // "draft" | "finalized"
  finalized_at?: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Leltár számlálás létrehozása (POST /inventory/daily-counts)
 */
export interface DailyInventoryCountCreateRequest {
  sheet_id: number;
  count_date: string;
  counted_by_employee_id?: number;
  counts: Record<string, number>;
  notes?: string;
}

/**
 * Leltár számlálás frissítése (PUT /inventory/daily-counts/{id})
 */
export interface DailyInventoryCountUpdateRequest {
  counts?: Record<string, number>;
  notes?: string;
  status?: string;
}

/**
 * WasteLog (Selejt napló) - Backend API response
 */
export interface WasteLog {
  id: number;
  inventory_item_id: number;
  quantity: number;
  reason: string; // "expired" | "damaged" | "quality_issue" | "other"
  waste_date: string;
  noted_by?: string | null;
  notes?: string | null;
  created_at: string;
}

/**
 * Selejt rögzítése (POST /inventory/waste)
 */
export interface WasteLogCreateRequest {
  inventory_item_id: number;
  quantity: number;
  reason: string;
  waste_date: string;
  noted_by?: string;
  notes?: string;
}

/**
 * Alacsony készlet riport - Response
 */
export interface LowStockItem {
  id: number;
  name: string;
  current_stock: number;
  min_stock_level: number;
  unit: string;
}

/**
 * Készlet érték riport - Response
 */
export interface InventoryValueResponse {
  total_value: number;
  currency: string;
  item_count: number;
}

/**
 * Leltár eltérés (Variance) - frontend számított érték
 */
export interface StocktakingVariance {
  item_id: number;
  item_name: string;
  counted: number;
  theoretical: number;
  variance: number; // counted - theoretical
  unit: string;
}
