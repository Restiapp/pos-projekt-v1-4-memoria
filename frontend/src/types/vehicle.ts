/**
 * Vehicle (Gépjármű) típusdefiníciók
 * Backend API sémáknak megfelelően
 * Backend: backend/service_admin/schemas/vehicle.py
 */

/**
 * Vehicle (Jármű) - Backend API response
 */
export interface Vehicle {
  id: number;
  license_plate: string;
  brand: string;
  model: string;
  year: number | null;
  vin: string | null; // Vehicle Identification Number
  fuel_type: string; // "PETROL_95" | "PETROL_98" | "DIESEL" | "ELECTRIC" | "HYBRID" | "LPG" | "CNG"
  purchase_date: string | null; // ISO date string
  purchase_price: number | null;
  current_value: number | null;
  current_mileage: number | null;
  responsible_employee_id: number | null;
  status: string; // "ACTIVE" | "MAINTENANCE" | "OUT_OF_SERVICE" | "SOLD" | "RETIRED"
  insurance_expiry_date: string | null; // ISO date string
  mot_expiry_date: string | null; // Műszaki vizsga lejárata (MOT = Ministry of Transport test)
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Új jármű létrehozása (POST /api/vehicles)
 * Backend: VehicleCreate schema
 */
export interface VehicleCreate {
  license_plate: string;
  brand: string;
  model: string;
  year?: number | null;
  vin?: string | null;
  fuel_type: string;
  purchase_date?: string | null;
  purchase_price?: number | null;
  current_value?: number | null;
  current_mileage?: number | null;
  responsible_employee_id?: number | null;
  status?: string;
  insurance_expiry_date?: string | null;
  mot_expiry_date?: string | null;
  notes?: string | null;
  is_active?: boolean;
}

/**
 * Jármű frissítése (PATCH /api/vehicles/{id})
 * Backend: VehicleUpdate schema
 */
export interface VehicleUpdate {
  license_plate?: string;
  brand?: string;
  model?: string;
  year?: number | null;
  vin?: string | null;
  fuel_type?: string;
  purchase_date?: string | null;
  purchase_price?: number | null;
  current_value?: number | null;
  current_mileage?: number | null;
  responsible_employee_id?: number | null;
  status?: string;
  insurance_expiry_date?: string | null;
  mot_expiry_date?: string | null;
  notes?: string | null;
  is_active?: boolean;
}

/**
 * VehicleMaintenance (Jármű karbantartás) - Backend API response
 */
export interface VehicleMaintenance {
  id: number;
  vehicle_id: number;
  maintenance_type: string; // "REGULAR_SERVICE" | "REPAIR" | "TIRE_CHANGE" | "OIL_CHANGE" | "BRAKE_SERVICE" | "MOT" | "OTHER"
  maintenance_date: string; // ISO date string
  mileage: number | null;
  description: string;
  cost: number | null;
  service_provider: string | null;
  next_maintenance_date: string | null; // ISO date string
  next_maintenance_mileage: number | null;
  invoice_number: string | null;
  recorded_by_employee_id: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Új karbantartás létrehozása (POST /api/vehicles/maintenances)
 * Backend: VehicleMaintenanceCreate schema
 */
export interface VehicleMaintenanceCreate {
  vehicle_id: number;
  maintenance_type: string;
  maintenance_date: string;
  mileage?: number | null;
  description: string;
  cost?: number | null;
  service_provider?: string | null;
  next_maintenance_date?: string | null;
  next_maintenance_mileage?: number | null;
  invoice_number?: string | null;
  recorded_by_employee_id?: number | null;
  notes?: string | null;
}

/**
 * Karbantartás frissítése (PATCH /api/vehicles/maintenances/{id})
 * Backend: VehicleMaintenanceUpdate schema
 */
export interface VehicleMaintenanceUpdate {
  maintenance_type?: string;
  maintenance_date?: string;
  mileage?: number | null;
  description?: string;
  cost?: number | null;
  service_provider?: string | null;
  next_maintenance_date?: string | null;
  next_maintenance_mileage?: number | null;
  invoice_number?: string | null;
  recorded_by_employee_id?: number | null;
  notes?: string | null;
}

/**
 * VehicleRefueling (Tankolás) - Backend API response
 */
export interface VehicleRefueling {
  id: number;
  vehicle_id: number;
  refueling_date: string; // ISO date string
  mileage: number | null;
  fuel_type: string; // "PETROL_95" | "PETROL_98" | "DIESEL" | "ELECTRIC" | "LPG" | "CNG"
  quantity_liters: number;
  price_per_liter: number;
  total_cost: number;
  full_tank: boolean;
  location: string | null;
  invoice_number: string | null;
  recorded_by_employee_id: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Új tankolás létrehozása (POST /api/vehicles/refuelings)
 * Backend: VehicleRefuelingCreate schema
 */
export interface VehicleRefuelingCreate {
  vehicle_id: number;
  refueling_date: string;
  mileage?: number | null;
  fuel_type: string;
  quantity_liters: number;
  price_per_liter: number;
  total_cost: number;
  full_tank?: boolean;
  location?: string | null;
  invoice_number?: string | null;
  recorded_by_employee_id?: number | null;
  notes?: string | null;
}

/**
 * Tankolás frissítése (PATCH /api/vehicles/refuelings/{id})
 * Backend: VehicleRefuelingUpdate schema
 */
export interface VehicleRefuelingUpdate {
  refueling_date?: string;
  mileage?: number | null;
  fuel_type?: string;
  quantity_liters?: number;
  price_per_liter?: number;
  total_cost?: number;
  full_tank?: boolean;
  location?: string | null;
  invoice_number?: string | null;
  recorded_by_employee_id?: number | null;
  notes?: string | null;
}
