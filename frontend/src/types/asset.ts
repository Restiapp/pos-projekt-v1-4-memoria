/**
 * Asset (Tárgyi Eszköz) típusdefiníciók
 * Backend API sémáknak megfelelően
 * Backend: backend/service_admin/schemas/asset.py
 */

/**
 * AssetGroup (Eszközcsoport) - Backend API response
 */
export interface AssetGroup {
  id: number;
  name: string;
  description: string | null;
  depreciation_rate: number | null; // Százalék/év
  expected_lifetime_years: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Új eszközcsoport létrehozása (POST /api/assets/groups)
 * Backend: AssetGroupCreate schema
 */
export interface AssetGroupCreate {
  name: string;
  description?: string | null;
  depreciation_rate?: number | null;
  expected_lifetime_years?: number | null;
  is_active?: boolean;
}

/**
 * Eszközcsoport frissítése (PATCH /api/assets/groups/{id})
 * Backend: AssetGroupUpdate schema
 */
export interface AssetGroupUpdate {
  name?: string;
  description?: string | null;
  depreciation_rate?: number | null;
  expected_lifetime_years?: number | null;
  is_active?: boolean;
}

/**
 * Asset (Eszköz) - Backend API response
 */
export interface Asset {
  id: number;
  asset_group_id: number;
  name: string;
  inventory_number: string | null;
  manufacturer: string | null;
  model: string | null;
  serial_number: string | null;
  purchase_date: string | null; // ISO date string
  purchase_price: number | null;
  current_value: number | null;
  location: string | null;
  responsible_employee_id: number | null;
  status: string; // "ACTIVE" | "MAINTENANCE" | "RETIRED" | "SOLD" | "DAMAGED"
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Új eszköz létrehozása (POST /api/assets)
 * Backend: AssetCreate schema
 */
export interface AssetCreate {
  asset_group_id: number;
  name: string;
  inventory_number?: string | null;
  manufacturer?: string | null;
  model?: string | null;
  serial_number?: string | null;
  purchase_date?: string | null; // ISO date string
  purchase_price?: number | null;
  current_value?: number | null;
  location?: string | null;
  responsible_employee_id?: number | null;
  status?: string;
  notes?: string | null;
  is_active?: boolean;
}

/**
 * Eszköz frissítése (PATCH /api/assets/{id})
 * Backend: AssetUpdate schema
 */
export interface AssetUpdate {
  asset_group_id?: number;
  name?: string;
  inventory_number?: string | null;
  manufacturer?: string | null;
  model?: string | null;
  serial_number?: string | null;
  purchase_date?: string | null;
  purchase_price?: number | null;
  current_value?: number | null;
  location?: string | null;
  responsible_employee_id?: number | null;
  status?: string;
  notes?: string | null;
  is_active?: boolean;
}

/**
 * AssetService (Eszköz szerviz) - Backend API response
 */
export interface AssetService {
  id: number;
  asset_id: number;
  service_type: string; // "MAINTENANCE" | "REPAIR" | "INSPECTION" | "CALIBRATION" | "CLEANING"
  service_date: string; // ISO date string
  description: string;
  cost: number | null;
  service_provider: string | null;
  next_service_date: string | null; // ISO date string
  performed_by_employee_id: number | null;
  documents_url: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Új szerviz bejegyzés létrehozása (POST /api/assets/services)
 * Backend: AssetServiceCreate schema
 */
export interface AssetServiceCreate {
  asset_id: number;
  service_type: string;
  service_date: string;
  description: string;
  cost?: number | null;
  service_provider?: string | null;
  next_service_date?: string | null;
  performed_by_employee_id?: number | null;
  documents_url?: string | null;
}

/**
 * Szerviz bejegyzés frissítése (PATCH /api/assets/services/{id})
 * Backend: AssetServiceUpdate schema
 */
export interface AssetServiceUpdate {
  service_type?: string;
  service_date?: string;
  description?: string;
  cost?: number | null;
  service_provider?: string | null;
  next_service_date?: string | null;
  performed_by_employee_id?: number | null;
  documents_url?: string | null;
}
