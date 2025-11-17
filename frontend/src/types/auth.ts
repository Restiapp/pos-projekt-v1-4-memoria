/**
 * Auth típusok - Backend API sémákkal szinkronban
 * Backend: backend/service_admin/schemas/auth.py
 */

// POST /auth/login Request
export interface LoginRequest {
  username: string;
  password: string; // PIN kód (backend "password" mezőbe kerül)
}

// POST /auth/login Response
export interface TokenResponse {
  access_token: string;
  token_type: string; // "bearer"
  expires_in: number; // másodpercben
  issued_at: string;  // ISO datetime string
}

// GET /auth/me Response
export interface User {
  id: number;
  username: string;
  name: string;
  email: string;
  phone: string;
  is_active: boolean;
  roles: Role[];
  permissions: string[]; // pl. ["orders:view", "orders:create"]
  created_at: string | null;
  updated_at: string | null;
}

export interface Role {
  id: number;
  name: string;
  description: string;
}

// Auth Store State
export interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
