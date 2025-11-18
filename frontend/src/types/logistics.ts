/**
 * Logistics típusok - Backend API sémákkal szinkronban
 * Backend: backend/service_logistics/schemas/
 */

// =====================================================
// COURIER TYPES
// =====================================================

export type CourierStatus = 'available' | 'on_delivery' | 'offline' | 'break';

export interface Courier {
  id: number;
  courier_name: string;
  phone: string;
  email?: string;
  status: CourierStatus;
  is_active: boolean;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface CourierCreate {
  courier_name: string;
  phone: string;
  email?: string;
  status?: CourierStatus;
  is_active?: boolean;
}

export interface CourierUpdate {
  courier_name?: string;
  phone?: string;
  email?: string;
  status?: CourierStatus;
  is_active?: boolean;
}

export interface CourierListResponse {
  items: Courier[];
  total: number;
  page: number;
  page_size: number;
}

// =====================================================
// DELIVERY ZONE TYPES
// =====================================================

export interface DeliveryZone {
  id: number;
  zone_name: string;
  description?: string;
  delivery_fee: number; // HUF
  min_order_value: number; // HUF
  estimated_delivery_time_minutes: number;
  zip_codes?: string[]; // Irányítószámok listája
  is_active: boolean;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface DeliveryZoneCreate {
  zone_name: string;
  description?: string;
  delivery_fee?: number;
  min_order_value?: number;
  estimated_delivery_time_minutes?: number;
  zip_codes?: string[];
  is_active?: boolean;
}

export interface DeliveryZoneUpdate {
  zone_name?: string;
  description?: string;
  delivery_fee?: number;
  min_order_value?: number;
  estimated_delivery_time_minutes?: number;
  zip_codes?: string[];
  is_active?: boolean;
}

export interface DeliveryZoneListResponse {
  items: DeliveryZone[];
  total: number;
  page: number;
  page_size: number;
}

// =====================================================
// ZONE LOOKUP TYPES
// =====================================================

export interface GetByZipCodeRequest {
  zip_code: string;
}

export interface GetByZipCodeResponse {
  zone: DeliveryZone | null;
  message: string;
}

export interface GetByAddressRequest {
  address: string;
}

export interface GetByAddressResponse {
  zone: DeliveryZone | null;
  message: string;
  mock_mode: boolean;
}
