/**
 * Auth Service - Autentikációs API hívások
 * Backend endpoints: /auth/login, /auth/me
 */

import apiClient from './api';
import type { LoginRequest, TokenResponse, User } from '@/types/auth';

export const authService = {
  /**
   * POST /auth/login - PIN-alapú bejelentkezés
   */
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(
      '/auth/login',
      credentials
    );
    return response.data;
  },

  /**
   * GET /auth/me - Aktuális felhasználó adatai
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },
};
