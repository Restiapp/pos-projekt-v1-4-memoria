/**
 * Menu V1 Service - Sprint D6
 * API service for Menu V1 endpoints
 */

import api from './api';
import type {
  MenuCategory,
  MenuCategoryCreate,
  MenuCategoryUpdate,
  MenuItem,
  MenuItemCreate,
  MenuItemUpdate,
  MenuItemVariant,
  MenuItemVariantCreate,
  MenuItemVariantUpdate,
  ModifierGroup,
  ModifierGroupCreate,
  ModifierGroupUpdate,
  ModifierOption,
  ModifierOptionCreate,
  ModifierOptionUpdate,
  ModifierAssignment,
  ModifierAssignmentCreate,
  ModifierAssignmentUpdate,
  MenuCategoryTree,
  Channel,
} from '../types/menuV1';

const BASE_URL = '/api/v1/menu';

// ===========================
// MenuCategory API
// ===========================

export const menuV1Service = {
  // Categories
  async getCategories(params?: { skip?: number; limit?: number; active_only?: boolean }): Promise<MenuCategory[]> {
    const response = await api.get(`${BASE_URL}/categories`, { params });
    return response.data;
  },

  async getCategory(id: number): Promise<MenuCategory> {
    const response = await api.get(`${BASE_URL}/categories/${id}`);
    return response.data;
  },

  async createCategory(data: MenuCategoryCreate): Promise<MenuCategory> {
    const response = await api.post(`${BASE_URL}/categories`, data);
    return response.data;
  },

  async updateCategory(id: number, data: MenuCategoryUpdate): Promise<MenuCategory> {
    const response = await api.put(`${BASE_URL}/categories/${id}`, data);
    return response.data;
  },

  async deleteCategory(id: number): Promise<void> {
    await api.delete(`${BASE_URL}/categories/${id}`);
  },

  // Items
  async getItems(params?: {
    skip?: number;
    limit?: number;
    category_id?: number;
    active_only?: boolean;
  }): Promise<MenuItem[]> {
    const response = await api.get(`${BASE_URL}/items`, { params });
    return response.data;
  },

  async getItem(id: number): Promise<MenuItem> {
    const response = await api.get(`${BASE_URL}/items/${id}`);
    return response.data;
  },

  async createItem(data: MenuItemCreate): Promise<MenuItem> {
    const response = await api.post(`${BASE_URL}/items`, data);
    return response.data;
  },

  async updateItem(id: number, data: MenuItemUpdate): Promise<MenuItem> {
    const response = await api.put(`${BASE_URL}/items/${id}`, data);
    return response.data;
  },

  async deleteItem(id: number): Promise<void> {
    await api.delete(`${BASE_URL}/items/${id}`);
  },

  // Variants
  async getVariantsByItem(itemId: number): Promise<MenuItemVariant[]> {
    const response = await api.get(`${BASE_URL}/items/${itemId}/variants`);
    return response.data;
  },

  async createVariant(data: MenuItemVariantCreate): Promise<MenuItemVariant> {
    const response = await api.post(`${BASE_URL}/variants`, data);
    return response.data;
  },

  async updateVariant(id: number, data: MenuItemVariantUpdate): Promise<MenuItemVariant> {
    const response = await api.put(`${BASE_URL}/variants/${id}`, data);
    return response.data;
  },

  async deleteVariant(id: number): Promise<void> {
    await api.delete(`${BASE_URL}/variants/${id}`);
  },

  // Modifier Groups
  async getModifierGroups(params?: { skip?: number; limit?: number; active_only?: boolean }): Promise<ModifierGroup[]> {
    const response = await api.get(`${BASE_URL}/modifier-groups`, { params });
    return response.data;
  },

  async getModifierGroup(id: number): Promise<ModifierGroup> {
    const response = await api.get(`${BASE_URL}/modifier-groups/${id}`);
    return response.data;
  },

  async createModifierGroup(data: ModifierGroupCreate): Promise<ModifierGroup> {
    const response = await api.post(`${BASE_URL}/modifier-groups`, data);
    return response.data;
  },

  async updateModifierGroup(id: number, data: ModifierGroupUpdate): Promise<ModifierGroup> {
    const response = await api.put(`${BASE_URL}/modifier-groups/${id}`, data);
    return response.data;
  },

  async deleteModifierGroup(id: number): Promise<void> {
    await api.delete(`${BASE_URL}/modifier-groups/${id}`);
  },

  // Modifier Options
  async getModifierOptionsByGroup(groupId: number): Promise<ModifierOption[]> {
    const response = await api.get(`${BASE_URL}/modifier-groups/${groupId}/options`);
    return response.data;
  },

  async createModifierOption(data: ModifierOptionCreate): Promise<ModifierOption> {
    const response = await api.post(`${BASE_URL}/modifier-options`, data);
    return response.data;
  },

  async updateModifierOption(id: number, data: ModifierOptionUpdate): Promise<ModifierOption> {
    const response = await api.put(`${BASE_URL}/modifier-options/${id}`, data);
    return response.data;
  },

  async deleteModifierOption(id: number): Promise<void> {
    await api.delete(`${BASE_URL}/modifier-options/${id}`);
  },

  // Modifier Assignments
  async getModifierAssignmentsByItem(itemId: number): Promise<ModifierAssignment[]> {
    const response = await api.get(`${BASE_URL}/items/${itemId}/modifier-assignments`);
    return response.data;
  },

  async getModifierAssignmentsByCategory(categoryId: number): Promise<ModifierAssignment[]> {
    const response = await api.get(`${BASE_URL}/categories/${categoryId}/modifier-assignments`);
    return response.data;
  },

  async createModifierAssignment(data: ModifierAssignmentCreate): Promise<ModifierAssignment> {
    const response = await api.post(`${BASE_URL}/modifier-assignments`, data);
    return response.data;
  },

  async updateModifierAssignment(id: number, data: ModifierAssignmentUpdate): Promise<ModifierAssignment> {
    const response = await api.put(`${BASE_URL}/modifier-assignments/${id}`, data);
    return response.data;
  },

  async deleteModifierAssignment(id: number): Promise<void> {
    await api.delete(`${BASE_URL}/modifier-assignments/${id}`);
  },

  // Menu Tree
  async getMenuTree(channel: Channel = 'dine_in'): Promise<MenuCategoryTree[]> {
    const response = await api.get(`${BASE_URL}/tree`, {
      params: { channel },
    });
    return response.data;
  },
};

export default menuV1Service;
