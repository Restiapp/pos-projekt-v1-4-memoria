/**
 * Zustand Auth Store - Globális autentikációs state
 */

import { create } from 'zustand';
import { authService } from '@/services/authService';
import { storage } from '@/utils/storage';
import type { AuthState, LoginRequest, User } from '@/types/auth';

interface AuthActions {
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  loadUserFromStorage: () => void;
  fetchCurrentUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState & AuthActions>((set) => ({
  // State
  token: null,
  user: null,
  isAuthenticated: false,
  isLoading: false,

  // Actions
  login: async (credentials) => {
    set({ isLoading: true });
    try {
      // 1. Login API hívás
      const tokenResponse = await authService.login(credentials);

      // 2. Token mentése
      storage.setToken(tokenResponse.access_token);

      // 3. User adatok lekérése
      const user = await authService.getCurrentUser();

      // 4. User és token mentése storage-ba és state-be
      storage.setUser(user);
      set({
        token: tokenResponse.access_token,
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    storage.clear();
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  },

  loadUserFromStorage: () => {
    const token = storage.getToken();
    const user = storage.getUser();
    if (token && user) {
      set({
        token,
        user,
        isAuthenticated: true,
      });
    }
  },

  fetchCurrentUser: async () => {
    try {
      const user = await authService.getCurrentUser();
      storage.setUser(user);
      set({ user });
    } catch (error) {
      // Token érvénytelen, kijelentkezés
      storage.clear();
      set({
        token: null,
        user: null,
        isAuthenticated: false,
      });
    }
  },
}));
