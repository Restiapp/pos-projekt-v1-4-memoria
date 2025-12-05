/**
 * Menu V1 Types - Sprint D6
 * Synchronized with backend schemas
 * Backend: backend/service_menu/schemas/menu.py
 */

// Selection type for modifier groups
export enum SelectionType {
  REQUIRED_SINGLE = 'REQUIRED_SINGLE',
  OPTIONAL_SINGLE = 'OPTIONAL_SINGLE',
  OPTIONAL_MULTIPLE = 'OPTIONAL_MULTIPLE',
}

// ===========================
// MenuCategory Types
// ===========================

export interface MenuCategory {
  id: number;
  name: string;
  description?: string;
  parent_id?: number;
  position: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MenuCategoryCreate {
  name: string;
  description?: string;
  parent_id?: number;
  position?: number;
  is_active?: boolean;
}

export interface MenuCategoryUpdate {
  name?: string;
  description?: string;
  parent_id?: number;
  position?: number;
  is_active?: boolean;
}

// ===========================
// MenuItem Types
// ===========================

export interface MenuItem {
  id: number;
  category_id?: number;
  name: string;
  description?: string;
  base_price_gross: number;
  vat_rate_dine_in: number;
  vat_rate_takeaway: number;
  is_active: boolean;
  channel_flags?: Record<string, boolean>;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface MenuItemCreate {
  category_id?: number;
  name: string;
  description?: string;
  base_price_gross: number;
  vat_rate_dine_in?: number;
  vat_rate_takeaway?: number;
  is_active?: boolean;
  channel_flags?: Record<string, boolean>;
  metadata_json?: Record<string, any>;
}

export interface MenuItemUpdate {
  category_id?: number;
  name?: string;
  description?: string;
  base_price_gross?: number;
  vat_rate_dine_in?: number;
  vat_rate_takeaway?: number;
  is_active?: boolean;
  channel_flags?: Record<string, boolean>;
  metadata_json?: Record<string, any>;
}

// ===========================
// MenuItemVariant Types
// ===========================

export interface MenuItemVariant {
  id: number;
  item_id: number;
  name: string;
  price_delta: number;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MenuItemVariantCreate {
  item_id: number;
  name: string;
  price_delta?: number;
  is_default?: boolean;
  is_active?: boolean;
}

export interface MenuItemVariantUpdate {
  item_id?: number;
  name?: string;
  price_delta?: number;
  is_default?: boolean;
  is_active?: boolean;
}

// ===========================
// ModifierGroup Types
// ===========================

export interface ModifierGroup {
  id: number;
  name: string;
  description?: string;
  selection_type: SelectionType;
  min_select: number;
  max_select?: number;
  position: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ModifierGroupCreate {
  name: string;
  description?: string;
  selection_type?: SelectionType;
  min_select?: number;
  max_select?: number;
  position?: number;
  is_active?: boolean;
}

export interface ModifierGroupUpdate {
  name?: string;
  description?: string;
  selection_type?: SelectionType;
  min_select?: number;
  max_select?: number;
  position?: number;
  is_active?: boolean;
}

// ===========================
// ModifierOption Types
// ===========================

export interface ModifierOption {
  id: number;
  group_id: number;
  name: string;
  price_delta_gross: number;
  is_default: boolean;
  is_active: boolean;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ModifierOptionCreate {
  group_id: number;
  name: string;
  price_delta_gross?: number;
  is_default?: boolean;
  is_active?: boolean;
  metadata_json?: Record<string, any>;
}

export interface ModifierOptionUpdate {
  group_id?: number;
  name?: string;
  price_delta_gross?: number;
  is_default?: boolean;
  is_active?: boolean;
  metadata_json?: Record<string, any>;
}

// ===========================
// ModifierAssignment Types
// ===========================

export interface ModifierAssignment {
  id: number;
  group_id: number;
  item_id?: number;
  category_id?: number;
  applies_to_variants: boolean;
  is_required_override?: boolean;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface ModifierAssignmentCreate {
  group_id: number;
  item_id?: number;
  category_id?: number;
  applies_to_variants?: boolean;
  is_required_override?: boolean;
  position?: number;
}

export interface ModifierAssignmentUpdate {
  group_id?: number;
  item_id?: number;
  category_id?: number;
  applies_to_variants?: boolean;
  is_required_override?: boolean;
  position?: number;
}

// ===========================
// Tree/Aggregated Types
// ===========================

export interface ModifierOptionTree {
  id: number;
  name: string;
  price_delta_gross: number;
  is_default: boolean;
  is_active: boolean;
}

export interface ModifierGroupTree {
  id: number;
  name: string;
  description?: string;
  selection_type: SelectionType;
  min_select: number;
  max_select?: number;
  position: number;
  is_active: boolean;
  options: ModifierOptionTree[];
}

export interface MenuItemVariantTree {
  id: number;
  name: string;
  price_delta: number;
  is_default: boolean;
  is_active: boolean;
}

export interface MenuItemTree {
  id: number;
  name: string;
  description?: string;
  base_price_gross: number;
  vat_rate_dine_in: number;
  vat_rate_takeaway: number;
  is_active: boolean;
  channel_flags?: Record<string, boolean>;
  metadata_json?: Record<string, any>;
  variants: MenuItemVariantTree[];
  modifier_groups: ModifierGroupTree[];
}

export interface MenuCategoryTree {
  id: number;
  name: string;
  description?: string;
  parent_id?: number;
  position: number;
  is_active: boolean;
  items: MenuItemTree[];
  subcategories: MenuCategoryTree[];
}

// ===========================
// Channel Type
// ===========================

export type Channel = 'dine_in' | 'takeaway' | 'delivery';
