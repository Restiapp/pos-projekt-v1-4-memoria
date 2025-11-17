/**
 * Auth Service - Autentikációs API hívások
 *
 * Backend endpoints (service_admin:8008):
 *   - POST /api/v1/auth/login
 *   - GET /api/v1/auth/me
 *
 * Frontend hívások:
 *   - POST /api/auth/login → Vite proxy → http://localhost:8008/api/v1/auth/login
 *   - GET /api/auth/me → Vite proxy → http://localhost:8008/api/v1/auth/me
 */

import apiClient from './api';
import type { LoginRequest, TokenResponse, User } from '@/types/auth';

export const authService = {
  /**
   * POST /api/auth/login - PIN-alapú bejelentkezés
   * Proxy Target: http://localhost:8008/api/v1/auth/login
   */
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(
      '/api/auth/login',
      credentials
    );
    return response.data;
  },

  /**
   * GET /api/auth/me - Aktuális felhasználó adatai
   * Proxy Target: http://localhost:8008/api/v1/auth/me
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/auth/me');
    return response.data;
  },
};
