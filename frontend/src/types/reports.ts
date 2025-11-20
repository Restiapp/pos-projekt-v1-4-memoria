/**
 * Reports Types - Analytics Dashboard
 * TypeScript típusok a riportok és analytics rendszerhez
 */

export interface DateRange {
  start_date: string; // ISO format: YYYY-MM-DD
  end_date: string;   // ISO format: YYYY-MM-DD
}

export interface SalesMetrics {
  total_revenue: number;
  total_orders: number;
  average_basket: number;
  cash_revenue: number;
  card_revenue: number;
  other_revenue: number;
}

export interface DailySales {
  date: string; // YYYY-MM-DD
  revenue_cash: number;
  revenue_card: number;
  revenue_total: number;
  order_count: number;
}

export interface TopProduct {
  product_id: number;
  product_name: string;
  quantity_sold: number;
  total_revenue: number;
  percentage: number;
}

export interface IngredientConsumption {
  ingredient_id: number;
  ingredient_name: string;
  unit: string;
  quantity_consumed: number;
  cost: number;
}

export interface ReportsResponse {
  metrics: SalesMetrics;
  daily_sales: DailySales[];
  top_products: TopProduct[];
  ingredient_consumption: IngredientConsumption[];
}

export type DateRangePreset = 'today' | 'week' | 'month' | 'custom';
