/**
 * Vehicle Service - Gépjárművek API hívások
 *
 * Backend endpoints (service_admin:8008):
 *   Vehicles:
 *     - POST /api/v1/vehicles
 *     - GET /api/v1/vehicles
 *     - GET /api/v1/vehicles/{id}
 *     - PATCH /api/v1/vehicles/{id}
 *     - DELETE /api/v1/vehicles/{id}
 *   Refuelings:
 *     - POST /api/v1/vehicles/refuelings
 *     - GET /api/v1/vehicles/refuelings
 *     - GET /api/v1/vehicles/refuelings/{id}
 *     - PATCH /api/v1/vehicles/refuelings/{id}
 *     - DELETE /api/v1/vehicles/refuelings/{id}
 *   Maintenances:
 *     - POST /api/v1/vehicles/maintenances
 *     - GET /api/v1/vehicles/maintenances
 *     - GET /api/v1/vehicles/maintenances/{id}
 *     - PATCH /api/v1/vehicles/maintenances/{id}
 *     - DELETE /api/v1/vehicles/maintenances/{id}
 *
 * Frontend hívások:
 *   - POST /api/vehicles → Vite proxy → http://localhost:8008/api/v1/vehicles
 *   - stb.
 */

import apiClient from './api';
import type {
  Vehicle,
  VehicleCreate,
  VehicleUpdate,
  VehicleRefueling,
  VehicleRefuelingCreate,
  VehicleRefuelingUpdate,
  VehicleMaintenance,
  VehicleMaintenanceCreate,
  VehicleMaintenanceUpdate,
} from '@/types/vehicle';

// ============================================================================
// Vehicle Operations (Járművek)
// ============================================================================

/**
 * Járművek listázása
 * GET /api/vehicles
 * Proxy Target: http://localhost:8008/api/v1/vehicles
 */
export const getVehicles = async (params?: {
  status?: string;
  fuel_type?: string;
  responsible_employee_id?: number;
  is_active?: boolean;
  limit?: number;
  offset?: number;
}): Promise<Vehicle[]> => {
  try {
    const response = await apiClient.get<Vehicle[]>('/api/vehicles', {
      params,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching vehicles:', error);
    throw error;
  }
};

/**
 * Jármű lekérése ID alapján
 * GET /api/vehicles/{id}
 * Proxy Target: http://localhost:8008/api/v1/vehicles/{id}
 */
export const getVehicleById = async (id: number): Promise<Vehicle> => {
  try {
    const response = await apiClient.get<Vehicle>(`/api/vehicles/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching vehicle ${id}:`, error);
    throw error;
  }
};

/**
 * Új jármű létrehozása
 * POST /api/vehicles
 * Proxy Target: http://localhost:8008/api/v1/vehicles
 */
export const createVehicle = async (
  vehicleData: VehicleCreate
): Promise<Vehicle> => {
  try {
    const response = await apiClient.post<Vehicle>('/api/vehicles', vehicleData);
    return response.data;
  } catch (error) {
    console.error('Error creating vehicle:', error);
    throw error;
  }
};

/**
 * Jármű frissítése
 * PATCH /api/vehicles/{id}
 * Proxy Target: http://localhost:8008/api/v1/vehicles/{id}
 */
export const updateVehicle = async (
  id: number,
  vehicleData: VehicleUpdate
): Promise<Vehicle> => {
  try {
    const response = await apiClient.patch<Vehicle>(
      `/api/vehicles/${id}`,
      vehicleData
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating vehicle ${id}:`, error);
    throw error;
  }
};

/**
 * Jármű törlése (soft delete)
 * DELETE /api/vehicles/{id}
 * Proxy Target: http://localhost:8008/api/v1/vehicles/{id}
 */
export const deleteVehicle = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/vehicles/${id}`);
  } catch (error) {
    console.error(`Error deleting vehicle ${id}:`, error);
    throw error;
  }
};

// ============================================================================
// Refueling Operations (Tankolások)
// ============================================================================

/**
 * Tankolások listázása
 * GET /api/vehicles/refuelings
 * Proxy Target: http://localhost:8008/api/v1/vehicles/refuelings
 */
export const getRefuelings = async (params?: {
  vehicle_id?: number;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}): Promise<VehicleRefueling[]> => {
  try {
    const response = await apiClient.get<VehicleRefueling[]>(
      '/api/vehicles/refuelings',
      {
        params,
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching refuelings:', error);
    throw error;
  }
};

/**
 * Tankolás lekérése ID alapján
 * GET /api/vehicles/refuelings/{id}
 * Proxy Target: http://localhost:8008/api/v1/vehicles/refuelings/{id}
 */
export const getRefuelingById = async (
  id: number
): Promise<VehicleRefueling> => {
  try {
    const response = await apiClient.get<VehicleRefueling>(
      `/api/vehicles/refuelings/${id}`
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching refueling ${id}:`, error);
    throw error;
  }
};

/**
 * Új tankolás létrehozása
 * POST /api/vehicles/refuelings
 * Proxy Target: http://localhost:8008/api/v1/vehicles/refuelings
 */
export const createRefueling = async (
  refuelingData: VehicleRefuelingCreate
): Promise<VehicleRefueling> => {
  try {
    const response = await apiClient.post<VehicleRefueling>(
      '/api/vehicles/refuelings',
      refuelingData
    );
    return response.data;
  } catch (error) {
    console.error('Error creating refueling:', error);
    throw error;
  }
};

/**
 * Tankolás frissítése
 * PATCH /api/vehicles/refuelings/{id}
 * Proxy Target: http://localhost:8008/api/v1/vehicles/refuelings/{id}
 */
export const updateRefueling = async (
  id: number,
  refuelingData: VehicleRefuelingUpdate
): Promise<VehicleRefueling> => {
  try {
    const response = await apiClient.patch<VehicleRefueling>(
      `/api/vehicles/refuelings/${id}`,
      refuelingData
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating refueling ${id}:`, error);
    throw error;
  }
};

/**
 * Tankolás törlése (hard delete)
 * DELETE /api/vehicles/refuelings/{id}
 * Proxy Target: http://localhost:8008/api/v1/vehicles/refuelings/{id}
 */
export const deleteRefueling = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/vehicles/refuelings/${id}`);
  } catch (error) {
    console.error(`Error deleting refueling ${id}:`, error);
    throw error;
  }
};

// ============================================================================
// Maintenance Operations (Karbantartások)
// ============================================================================

/**
 * Karbantartások listázása
 * GET /api/vehicles/maintenances
 * Proxy Target: http://localhost:8008/api/v1/vehicles/maintenances
 */
export const getMaintenances = async (params?: {
  vehicle_id?: number;
  maintenance_type?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}): Promise<VehicleMaintenance[]> => {
  try {
    const response = await apiClient.get<VehicleMaintenance[]>(
      '/api/vehicles/maintenances',
      {
        params,
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching maintenances:', error);
    throw error;
  }
};

/**
 * Karbantartás lekérése ID alapján
 * GET /api/vehicles/maintenances/{id}
 * Proxy Target: http://localhost:8008/api/v1/vehicles/maintenances/{id}
 */
export const getMaintenanceById = async (
  id: number
): Promise<VehicleMaintenance> => {
  try {
    const response = await apiClient.get<VehicleMaintenance>(
      `/api/vehicles/maintenances/${id}`
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching maintenance ${id}:`, error);
    throw error;
  }
};

/**
 * Új karbantartás létrehozása
 * POST /api/vehicles/maintenances
 * Proxy Target: http://localhost:8008/api/v1/vehicles/maintenances
 */
export const createMaintenance = async (
  maintenanceData: VehicleMaintenanceCreate
): Promise<VehicleMaintenance> => {
  try {
    const response = await apiClient.post<VehicleMaintenance>(
      '/api/vehicles/maintenances',
      maintenanceData
    );
    return response.data;
  } catch (error) {
    console.error('Error creating maintenance:', error);
    throw error;
  }
};

/**
 * Karbantartás frissítése
 * PATCH /api/vehicles/maintenances/{id}
 * Proxy Target: http://localhost:8008/api/v1/vehicles/maintenances/{id}
 */
export const updateMaintenance = async (
  id: number,
  maintenanceData: VehicleMaintenanceUpdate
): Promise<VehicleMaintenance> => {
  try {
    const response = await apiClient.patch<VehicleMaintenance>(
      `/api/vehicles/maintenances/${id}`,
      maintenanceData
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating maintenance ${id}:`, error);
    throw error;
  }
};

/**
 * Karbantartás törlése (hard delete)
 * DELETE /api/vehicles/maintenances/{id}
 * Proxy Target: http://localhost:8008/api/v1/vehicles/maintenances/{id}
 */
export const deleteMaintenance = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/vehicles/maintenances/${id}`);
  } catch (error) {
    console.error(`Error deleting maintenance ${id}:`, error);
    throw error;
  }
};
