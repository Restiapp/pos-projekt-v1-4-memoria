/**
 * Role Service - Szerepkörök API hívások
 *
 * Backend endpoints (service_admin:8008):
 *   - GET /api/v1/roles
 *   - POST /api/v1/roles
 *   - GET /api/v1/roles/{id}
 *   - PUT /api/v1/roles/{id}
 *   - DELETE /api/v1/roles/{id}
 *   - GET /api/v1/permissions
 *
 * Frontend hívások:
 *   - GET /api/roles → Vite proxy → http://localhost:8008/api/v1/roles
 *   - POST /api/roles → Vite proxy → http://localhost:8008/api/v1/roles
 *   - stb.
 */

import apiClient from './api';
import type {
  Role,
  RoleWithPermissions,
  RoleCreate,
  RoleUpdate,
  RoleListResponse,
  Permission,
  PermissionListResponse,
} from '@/types/role';

/**
 * Szerepkörök listázása (lapozással)
 * Proxy Target: http://localhost:8008/api/v1/roles
 *
 * @param page - Oldalszám (1-től kezdődik)
 * @param pageSize - Elemek száma oldalanként
 */
export const getRoles = async (
  page: number = 1,
  pageSize: number = 20
): Promise<RoleListResponse> => {
  try {
    const response = await apiClient.get<RoleListResponse>('/api/roles', {
      params: {
        page,
        page_size: pageSize,
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching roles:', error);
    throw error;
  }
};

/**
 * Szerepkör lekérése ID alapján (részletes adatokkal, jogosultságokkal)
 * Proxy Target: http://localhost:8008/api/v1/roles/{id}
 */
export const getRoleById = async (id: number): Promise<RoleWithPermissions> => {
  try {
    const response = await apiClient.get<RoleWithPermissions>(`/api/roles/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching role ${id}:`, error);
    throw error;
  }
};

/**
 * Új szerepkör létrehozása
 * POST /api/roles
 * Proxy Target: http://localhost:8008/api/v1/roles
 */
export const createRole = async (roleData: RoleCreate): Promise<Role> => {
  try {
    const response = await apiClient.post<Role>('/api/roles', roleData);
    return response.data;
  } catch (error) {
    console.error('Error creating role:', error);
    throw error;
  }
};

/**
 * Szerepkör frissítése
 * PUT /api/roles/{id}
 * Proxy Target: http://localhost:8008/api/v1/roles/{id}
 */
export const updateRole = async (
  id: number,
  roleData: RoleUpdate
): Promise<Role> => {
  try {
    const response = await apiClient.put<Role>(`/api/roles/${id}`, roleData);
    return response.data;
  } catch (error) {
    console.error(`Error updating role ${id}:`, error);
    throw error;
  }
};

/**
 * Szerepkör törlése
 * DELETE /api/roles/{id}
 * Proxy Target: http://localhost:8008/api/v1/roles/{id}
 */
export const deleteRole = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/roles/${id}`);
  } catch (error) {
    console.error(`Error deleting role ${id}:`, error);
    throw error;
  }
};

// =====================================================
// PERMISSION (Jogosultság) API hívások
// =====================================================

/**
 * Összes jogosultság lekérése (szerepkör szerkesztőhöz)
 * GET /api/permissions
 * Proxy Target: http://localhost:8008/api/v1/permissions
 */
export const getPermissions = async (): Promise<Permission[]> => {
  try {
    const response = await apiClient.get<PermissionListResponse>('/api/permissions', {
      params: {
        page: 1,
        page_size: 1000, // Összes jogosultság egy kérésben
      },
    });
    return response.data.items;
  } catch (error) {
    console.error('Error fetching permissions:', error);
    throw error;
  }
};
