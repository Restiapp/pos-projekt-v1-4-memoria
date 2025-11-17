/**
 * Employee Service - Munkatársak API hívások
 *
 * Backend endpoints (service_admin:8008):
 *   - GET /api/v1/employees
 *   - POST /api/v1/employees
 *   - GET /api/v1/employees/{id}
 *   - PUT /api/v1/employees/{id}
 *   - DELETE /api/v1/employees/{id}
 *   - GET /api/v1/roles (szerepkörök lekérése)
 *
 * Frontend hívások:
 *   - GET /api/employees → Vite proxy → http://localhost:8008/api/v1/employees
 *   - POST /api/employees → Vite proxy → http://localhost:8008/api/v1/employees
 *   - stb.
 */

import apiClient from './api';
import type {
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
  EmployeeListResponse,
  Role,
} from '@/types/employee';

/**
 * Munkatársak listázása (lapozással, szűréssel)
 * Proxy Target: http://localhost:8008/api/v1/employees
 *
 * @param page - Oldalszám (1-től kezdődik)
 * @param pageSize - Elemek száma oldalanként
 * @param isActive - Szűrés aktív státuszra (undefined = összes)
 * @param search - Keresési kifejezés (név vagy username)
 */
export const getEmployees = async (
  page: number = 1,
  pageSize: number = 20,
  isActive?: boolean,
  search?: string
): Promise<EmployeeListResponse> => {
  try {
    const params: any = {
      page,
      page_size: pageSize,
    };

    if (isActive !== undefined) {
      params.is_active = isActive;
    }

    if (search) {
      params.search = search;
    }

    const response = await apiClient.get<EmployeeListResponse>('/api/employees', {
      params,
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching employees:', error);
    throw error;
  }
};

/**
 * Munkatárs lekérése ID alapján
 * Proxy Target: http://localhost:8008/api/v1/employees/{id}
 */
export const getEmployeeById = async (id: number): Promise<Employee> => {
  try {
    const response = await apiClient.get<Employee>(`/api/employees/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching employee ${id}:`, error);
    throw error;
  }
};

/**
 * Új munkatárs létrehozása
 * POST /api/employees
 * Proxy Target: http://localhost:8008/api/v1/employees
 */
export const createEmployee = async (
  employeeData: EmployeeCreate
): Promise<Employee> => {
  try {
    const response = await apiClient.post<Employee>('/api/employees', employeeData);
    return response.data;
  } catch (error) {
    console.error('Error creating employee:', error);
    throw error;
  }
};

/**
 * Munkatárs frissítése
 * PUT /api/employees/{id}
 * Proxy Target: http://localhost:8008/api/v1/employees/{id}
 */
export const updateEmployee = async (
  id: number,
  employeeData: EmployeeUpdate
): Promise<Employee> => {
  try {
    const response = await apiClient.put<Employee>(
      `/api/employees/${id}`,
      employeeData
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating employee ${id}:`, error);
    throw error;
  }
};

/**
 * Munkatárs törlése
 * DELETE /api/employees/{id}
 * Proxy Target: http://localhost:8008/api/v1/employees/{id}
 */
export const deleteEmployee = async (id: number): Promise<void> => {
  try {
    await apiClient.delete(`/api/employees/${id}`);
  } catch (error) {
    console.error(`Error deleting employee ${id}:`, error);
    throw error;
  }
};

// =====================================================
// ROLE (Szerepkör) API hívások
// =====================================================

/**
 * Összes szerepkör lekérése (admin dropdown-hoz)
 * GET /api/roles
 * Proxy Target: http://localhost:8008/api/v1/roles
 */
export const getRoles = async (): Promise<Role[]> => {
  try {
    const response = await apiClient.get<{ items: Role[] }>('/api/roles', {
      params: {
        page: 1,
        page_size: 100, // Összes szerepkör egy kérésben
      },
    });
    return response.data.items;
  } catch (error) {
    console.error('Error fetching roles:', error);
    throw error;
  }
};
