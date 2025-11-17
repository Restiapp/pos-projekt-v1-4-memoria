/**
 * Menu típusok - Backend API sémákkal szinkronban
 * Backend: backend/service_menu/schemas/product.py
 * Backend: backend/service_menu/schemas/category.py
 */

// Product típusok

export interface ProductTranslation {
  name: string;
  description?: string;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  base_price: number; // HUF
  category_id?: number;
  sku?: string;
  is_active: boolean;
  translations?: Record<string, ProductTranslation>; // ISO lang code -> translation
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  description?: string;
  base_price: number;
  category_id?: number;
  sku?: string;
  is_active: boolean;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  base_price?: number;
  category_id?: number;
  sku?: string;
  is_active?: boolean;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
}

// Category típusok

export interface Category {
  id: number;
  name: string;
  description?: string;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoryListResponse {
  items: Category[];
  total: number;
  page: number;
  page_size: number;
}
