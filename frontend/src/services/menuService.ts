/**
 * Menu Service - Menu API hívások (Products, Categories)
 *
 * Backend endpoints (service_menu:8001):
 *   - GET /api/v1/products
 *   - POST /api/v1/products
 *   - PUT /api/v1/products/{id}
 *   - DELETE /api/v1/products/{id}
 *   - GET /api/v1/categories
 *
 * Frontend hívások:
 *   - GET /api/products → Vite proxy → http://localhost:8001/api/v1/products
 *   - POST /api/products → Vite proxy → http://localhost:8001/api/v1/products
 */

import apiClient from './api';
import type {
  Product,
  ProductCreate,
  ProductUpdate,
  ProductListResponse,
  Category,
  CategoryListResponse,
} from '@/types/menu';
import type {
  ModifierGroupWithModifiers,
} from '@/types/modifier';

// =====================================================
// PRODUCTS
// =====================================================

/**
 * GET /api/products - Termékek listája (lapozással)
 * Proxy Target: http://localhost:8001/api/v1/products
 */
export const getProducts = async (
  page: number = 1,
  page_size: number = 20,
  is_active?: boolean,
  search?: string
): Promise<ProductListResponse> => {
  const params: Record<string, any> = { page, page_size };
  if (is_active !== undefined) {
    params.is_active = is_active;
  }
  if (search) {
    params.search = search;
  }

  const response = await apiClient.get<ProductListResponse>('/api/products', {
    params,
  });
  return response.data;
};

/**
 * GET /api/products/{id} - Termék részletei
 * Proxy Target: http://localhost:8001/api/v1/products/{id}
 */
export const getProductById = async (id: number): Promise<Product> => {
  const response = await apiClient.get<Product>(`/api/products/${id}`);
  return response.data;
};

/**
 * POST /api/products - Új termék létrehozása
 * Proxy Target: http://localhost:8001/api/v1/products
 *
 * FONTOS: A backend automatikusan lefordítja a terméket AI-val (háttérfolyamat).
 */
export const createProduct = async (
  productData: ProductCreate
): Promise<Product> => {
  const response = await apiClient.post<Product>('/api/products', productData);
  return response.data;
};

/**
 * PUT /api/products/{id} - Termék frissítése
 * Proxy Target: http://localhost:8001/api/v1/products/{id}
 *
 * FONTOS: A backend automatikusan lefordítja a terméket AI-val (háttérfolyamat).
 */
export const updateProduct = async (
  id: number,
  productData: ProductUpdate
): Promise<Product> => {
  const response = await apiClient.put<Product>(
    `/api/products/${id}`,
    productData
  );
  return response.data;
};

/**
 * DELETE /api/products/{id} - Termék törlése
 * Proxy Target: http://localhost:8001/api/v1/products/{id}
 */
export const deleteProduct = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/products/${id}`);
};

// =====================================================
// CATEGORIES
// =====================================================

/**
 * GET /api/categories - Kategóriák listája (lapozással)
 * Proxy Target: http://localhost:8001/api/v1/categories
 */
export const getCategories = async (
  page: number = 1,
  page_size: number = 100, // Kategóriák általában kevesebbek, ezért nagyobb page_size
  is_active?: boolean
): Promise<CategoryListResponse> => {
  const params: Record<string, any> = { page, page_size };
  if (is_active !== undefined) {
    params.is_active = is_active;
  }

  const response = await apiClient.get<CategoryListResponse>(
    '/api/categories',
    { params }
  );
  return response.data;
};

/**
 * GET /api/categories/{id} - Kategória részletei
 * Proxy Target: http://localhost:8001/api/v1/categories/{id}
 */
export const getCategoryById = async (id: number): Promise<Category> => {
  const response = await apiClient.get<Category>(`/api/categories/${id}`);
  return response.data;
};

// =====================================================
// MODIFIER GROUPS
// =====================================================

/**
 * GET /api/modifier-groups/products/{product_id}/modifier-groups
 * Get all modifier groups for a specific product
 * Proxy Target: http://localhost:8001/api/v1/modifier-groups/products/{product_id}/modifier-groups
 */
export const getModifierGroupsByProduct = async (
  productId: number,
  includeModifiers: boolean = true
): Promise<ModifierGroupWithModifiers[]> => {
  const response = await apiClient.get<ModifierGroupWithModifiers[]>(
    `/api/modifier-groups/products/${productId}/modifier-groups`,
    {
      params: { include_modifiers: includeModifiers },
    }
  );
  return response.data;
};
