/**
 * Employee (Munkatárs) és Role (Szerepkör) típusdefiníciók
 * Backend API sémáknak megfelelően
 * Backend: backend/service_admin/schemas/employee.py
 */

/**
 * Role (Szerepkör) - Backend API response
 */
export interface Role {
  id: number;
  name: string;
  description: string;
  created_at: string | null;
}

/**
 * Employee (Munkatárs) - Backend API response (EmployeeResponse)
 */
export interface Employee {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  role_id: number | null;
  created_at: string;
  updated_at: string;
}

/**
 * Új munkatárs létrehozása (POST /api/employees)
 * Backend: EmployeeCreate schema
 */
export interface EmployeeCreate {
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  role_id?: number | null;
  password: string; // PIN kód (backend "password" mezőbe kerül, majd hashelve tárolódik)
}

/**
 * Munkatárs frissítése (PUT /api/employees/{id})
 * Backend: EmployeeUpdate schema
 */
export interface EmployeeUpdate {
  username?: string;
  email?: string;
  full_name?: string;
  is_active?: boolean;
  role_id?: number | null;
  password?: string; // Új PIN kód (opcionális)
}

/**
 * Munkatársak listázása - Response (GET /api/employees)
 * Backend: EmployeeListResponse schema
 */
export interface EmployeeListResponse {
  items: Employee[];
  total: number;
  page: number;
  page_size: number;
}
