/**
 * Modifier Types - Backend API schemas
 * Backend: backend/service_menu/schemas/modifier.py
 */

export enum SelectionType {
  SINGLE_CHOICE_REQUIRED = 'SINGLE_CHOICE_REQUIRED',
  SINGLE_CHOICE_OPTIONAL = 'SINGLE_CHOICE_OPTIONAL',
  MULTIPLE_CHOICE_OPTIONAL = 'MULTIPLE_CHOICE_OPTIONAL',
  MULTIPLE_CHOICE_REQUIRED = 'MULTIPLE_CHOICE_REQUIRED',
}

export interface Modifier {
  id: number;
  group_id: number;
  name: string;
  price_modifier: number; // Can be positive or negative
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface ModifierGroup {
  id: number;
  name: string;
  selection_type: SelectionType;
  min_selection: number;
  max_selection: number;
  created_at: string;
  updated_at: string;
}

export interface ModifierGroupWithModifiers extends ModifierGroup {
  modifiers: Modifier[];
}

export interface SelectedModifier {
  group_name: string;
  modifier_name: string;
  price: number;
}

// For creating order items
export interface OrderItemModifier {
  group_id: number;
  group_name: string;
  modifier_id: number;
  modifier_name: string;
  price_modifier: number;
}
