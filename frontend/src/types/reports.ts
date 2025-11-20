/**
 * Reports (Riportok/Analitika) típusdefiníciók
 * Dashboard Analytics API sémáknak megfelelően
 * Backend: backend/service_admin/schemas/reports.py
 */

/**
 * Napi értékesítési adatok (egy napra)
 * Backend: DailySalesData schema
 */
export interface DailySalesData {
  date: string; // ISO date string (YYYY-MM-DD)
  total_revenue: number;
  cash_revenue: number;
  card_revenue: number;
  order_count: number;
  average_order_value: number;
}

/**
 * Értékesítési riport válasz (GET /api/v1/reports/sales)
 * Backend: SalesReportResponse schema
 */
export interface SalesReportResponse {
  sales_data: DailySalesData[];
  total_revenue: number;
  total_orders: number;
  average_daily_revenue: number;
}

/**
 * Top termék adatok (egy termékre)
 * Backend: TopProductData schema
 */
export interface TopProductData {
  product_id: number;
  product_name: string;
  quantity_sold: number;
  total_revenue: number;
  average_price: number;
  category_name?: string | null;
}

/**
 * Top termékek riport válasz (GET /api/v1/reports/top-products)
 * Backend: TopProductsResponse schema
 */
export interface TopProductsResponse {
  products: TopProductData[];
  total_products_analyzed: number;
}

/**
 * Készletfogyási adatok (egy alapanyagra)
 * Backend: InventoryConsumptionData schema
 */
export interface InventoryConsumptionData {
  ingredient_id: number;
  ingredient_name: string;
  quantity_consumed: number;
  unit: string;
  estimated_cost?: number | null;
}

/**
 * Készletfogyási riport válasz (GET /api/v1/reports/consumption)
 * Backend: ConsumptionReportResponse schema
 */
export interface ConsumptionReportResponse {
  consumption_data: InventoryConsumptionData[];
  total_items: number;
  total_estimated_cost?: number | null;
}

/**
 * Riport lekérdezési paraméterek
 */
export interface ReportQueryParams {
  start_date?: string; // ISO date string (YYYY-MM-DD)
  end_date?: string; // ISO date string (YYYY-MM-DD)
  limit?: number; // Only for top-products
}
