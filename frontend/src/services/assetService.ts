/**
 * Asset Service - Tárgyi Eszközök API hívások
 *
 * Backend endpoints (service_admin:8008):
 *   Asset Groups:
 *     - POST /api/v1/assets/groups
 *     - GET /api/v1/assets/groups
 *     - GET /api/v1/assets/groups/{id}
 *     - PATCH /api/v1/assets/groups/{id}
 *     - DELETE /api/v1/assets/groups/{id}
 *   Assets:
 *     - POST /api/v1/assets
 *     - GET /api/v1/assets
 *     - GET /api/v1/assets/{id}
 *     - PATCH /api/v1/assets/{id}
 *     - DELETE /api/v1/assets/{id}
 *   Asset Services:
 *     - POST /api/v1/assets/services
 *     - GET /api/v1/assets/services
 *     - GET /api/v1/assets/services/{id}
 *     - PATCH /api/v1/assets/services/{id}
 *     - DELETE /api/v1/assets/services/{id}
 *
 * Frontend hívások:
 *   - POST /api/assets/groups → Vite proxy → http://localhost:8008/api/v1/assets/groups
 *   - stb.
 */

import apiClient from './api';
import type {
  AssetGroup,
  AssetGroupCreate,
  AssetGroupUpdate,
  Asset,
  AssetCreate,
  AssetUpdate,
  AssetService,
  AssetServiceCreate,
  AssetServiceUpdate,
} from '@/types/asset';

// ============================================================================
// Asset Group Operations (Eszközcsoportok)
// ============================================================================

/**
 * Eszközcsoportok listázása
 * GET /api/assets/groups
 * Proxy Target: http://localhost:8008/api/v1/assets/groups
 */
export const getAssetGroups = async (params?: {
  is_active?: boolean;
  limit?: number;
  offset?: number;
}): Promise<AssetGroup[]> => {
  try {
    const response = await apiClient.get<AssetGroup[]>('/api/assets/groups', {
      params,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching asset groups:', error);
    throw error;
  }
};

/**
 * Eszközcsoport lekérése ID alapján
 * GET /api/assets/groups/{id}
 * Proxy Target: http://localhost:8008/api/v1/assets/groups/{id}
 */
export const getAssetGroupById = async (id: number): Promise<AssetGroup> => {
  try {
    const response = await apiClient.get<AssetGroup>(`/api/assets/groups/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching asset group ${id}:`, error);
    throw error;
  }
};

/**
 * Új eszközcsoport létrehozása
 * POST /api/assets/groups
 * Proxy Target: http://localhost:8008/api/v1/assets/groups
 */
export const createAssetGroup = async (
  groupData: AssetGroupCreate
): Promise<AssetGroup> => {
  try {
    const response = await apiClient.post<AssetGroup>(
      '/api/assets/groups',
      groupData
    );
    return response.data;
  } catch (error) {
    console.error('Error creating asset group:', error);
    throw error;
  }
};

/**
 * Eszközcsoport frissítése
 * PATCH /api/assets/groups/{id}
 * Proxy Target: http://localhost:8008/api/v1/assets/groups/{id}
 */
export const updateAssetGroup = async (
  id: number,
  groupData: AssetGroupUpdate
): Promise<AssetGroup> => {
  try {
    const response = await apiClient.patch<AssetGroup>(
      `/api/assets/groups/${id}`,
      groupData
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating asset group ${id}:`, error);
    throw error;
  }
};

/**
 * Eszközcsoport törlése (soft delete)
 * DELETE /api/assets/groups/{id}
 * Proxy Target: http://localhost:8008/api/v1/assets/groups/{id}
 */
export const deleteAssetGroup = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/assets/groups/${id}`);
  } catch (error) {
    console.error(`Error deleting asset group ${id}:`, error);
    throw error;
  }
};

// ============================================================================
// Asset Operations (Eszközök)
// ============================================================================

/**
 * Eszközök listázása
 * GET /api/assets
 * Proxy Target: http://localhost:8008/api/v1/assets
 */
export const getAssets = async (params?: {
  asset_group_id?: number;
  status?: string;
  responsible_employee_id?: number;
  is_active?: boolean;
  limit?: number;
  offset?: number;
}): Promise<Asset[]> => {
  try {
    const response = await apiClient.get<Asset[]>('/api/assets', {
      params,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching assets:', error);
    throw error;
  }
};

/**
 * Eszköz lekérése ID alapján
 * GET /api/assets/{id}
 * Proxy Target: http://localhost:8008/api/v1/assets/{id}
 */
export const getAssetById = async (id: number): Promise<Asset> => {
  try {
    const response = await apiClient.get<Asset>(`/api/assets/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching asset ${id}:`, error);
    throw error;
  }
};

/**
 * Új eszköz létrehozása
 * POST /api/assets
 * Proxy Target: http://localhost:8008/api/v1/assets
 */
export const createAsset = async (assetData: AssetCreate): Promise<Asset> => {
  try {
    const response = await apiClient.post<Asset>('/api/assets', assetData);
    return response.data;
  } catch (error) {
    console.error('Error creating asset:', error);
    throw error;
  }
};

/**
 * Eszköz frissítése
 * PATCH /api/assets/{id}
 * Proxy Target: http://localhost:8008/api/v1/assets/{id}
 */
export const updateAsset = async (
  id: number,
  assetData: AssetUpdate
): Promise<Asset> => {
  try {
    const response = await apiClient.patch<Asset>(`/api/assets/${id}`, assetData);
    return response.data;
  } catch (error) {
    console.error(`Error updating asset ${id}:`, error);
    throw error;
  }
};

/**
 * Eszköz törlése (soft delete)
 * DELETE /api/assets/{id}
 * Proxy Target: http://localhost:8008/api/v1/assets/{id}
 */
export const deleteAsset = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/assets/${id}`);
  } catch (error) {
    console.error(`Error deleting asset ${id}:`, error);
    throw error;
  }
};

// ============================================================================
// Asset Service Operations (Szerviz bejegyzések)
// ============================================================================

/**
 * Szerviz bejegyzések listázása
 * GET /api/assets/services
 * Proxy Target: http://localhost:8008/api/v1/assets/services
 */
export const getAssetServices = async (params?: {
  asset_id?: number;
  service_type?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}): Promise<AssetService[]> => {
  try {
    const response = await apiClient.get<AssetService[]>('/api/assets/services', {
      params,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching asset services:', error);
    throw error;
  }
};

/**
 * Szerviz bejegyzés lekérése ID alapján
 * GET /api/assets/services/{id}
 * Proxy Target: http://localhost:8008/api/v1/assets/services/{id}
 */
export const getAssetServiceById = async (id: number): Promise<AssetService> => {
  try {
    const response = await apiClient.get<AssetService>(`/api/assets/services/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching asset service ${id}:`, error);
    throw error;
  }
};

/**
 * Új szerviz bejegyzés létrehozása
 * POST /api/assets/services
 * Proxy Target: http://localhost:8008/api/v1/assets/services
 */
export const createAssetService = async (
  serviceData: AssetServiceCreate
): Promise<AssetService> => {
  try {
    const response = await apiClient.post<AssetService>(
      '/api/assets/services',
      serviceData
    );
    return response.data;
  } catch (error) {
    console.error('Error creating asset service:', error);
    throw error;
  }
};

/**
 * Szerviz bejegyzés frissítése
 * PATCH /api/assets/services/{id}
 * Proxy Target: http://localhost:8008/api/v1/assets/services/{id}
 */
export const updateAssetService = async (
  id: number,
  serviceData: AssetServiceUpdate
): Promise<AssetService> => {
  try {
    const response = await apiClient.patch<AssetService>(
      `/api/assets/services/${id}`,
      serviceData
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating asset service ${id}:`, error);
    throw error;
  }
};

/**
 * Szerviz bejegyzés törlése (hard delete)
 * DELETE /api/assets/services/{id}
 * Proxy Target: http://localhost:8008/api/v1/assets/services/{id}
 */
export const deleteAssetService = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/assets/services/${id}`);
  } catch (error) {
    console.error(`Error deleting asset service ${id}:`, error);
    throw error;
  }
};
