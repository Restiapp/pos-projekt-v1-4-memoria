/**
 * Role (Szerepkör) és Permission (Jogosultság) típusdefiníciók
 * Backend API sémáknak megfelelően
 * Backend: backend/service_admin/schemas/role.py, permission.py
 */

/**
 * Permission (Jogosultság) - Backend API response
 */
export interface Permission {
  id: number;
  name: string; // snake_case, pl. "view_orders"
  description: string; // Pl. "Rendelések megtekintése"
  resource: string; // Pl. "orders", "employees", "products"
  action: string; // Pl. "view", "create", "update", "delete", "manage"
  created_at: string;
  updated_at: string;
}

/**
 * Role (Szerepkör) - Backend API response (RoleResponse)
 */
export interface Role {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

/**
 * Role with Permissions (Részletes szerepkör adatok)
 * Backend: RoleWithPermissionsResponse
 */
export interface RoleWithPermissions extends Role {
  permissions: Permission[];
}

/**
 * Új szerepkör létrehozása (POST /api/roles)
 * Backend: RoleCreate schema
 */
export interface RoleCreate {
  name: string;
  description: string;
  permission_ids: number[]; // Hozzárendelt jogosultságok ID-i
}

/**
 * Szerepkör frissítése (PUT /api/roles/{id})
 * Backend: RoleUpdate schema
 */
export interface RoleUpdate {
  name?: string;
  description?: string;
  permission_ids?: number[]; // Felülírja a meglévő jogosultságokat
}

/**
 * Szerepkörök listázása - Response (GET /api/roles)
 * Backend: RoleListResponse schema
 */
export interface RoleListResponse {
  items: Role[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Jogosultságok listázása - Response (GET /api/permissions)
 * Backend: PermissionListResponse schema
 */
export interface PermissionListResponse {
  items: Permission[];
  total: number;
  page: number;
  page_size: number;
}
