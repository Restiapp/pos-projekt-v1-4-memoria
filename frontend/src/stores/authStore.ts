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
  isLoading: true, // CRITICAL FIX: Initial loading state = true

  // Actions
  login: async (credentials) => {
    console.log('[Auth Store] Login started for user:', credentials.username);
    set({ isLoading: true });
    try {
      // 1. Login API hívás
      const tokenResponse = await authService.login(credentials);
      console.log('[Auth Store] ✅ Token received:', tokenResponse.access_token.substring(0, 20) + '...');

      // 2. Token mentése
      storage.setToken(tokenResponse.access_token);
      console.log('[Auth Store] ✅ Token saved to localStorage');

      // 3. User adatok lekérése
      const user = await authService.getCurrentUser();
      console.log('[Auth Store] ✅ User data fetched:', user.username, 'Permissions:', user.permissions);

      // 4. User és token mentése storage-ba és state-be
      storage.setUser(user);
      set({
        token: tokenResponse.access_token,
        user,
        isAuthenticated: true,
        isLoading: false,
      });
      console.log('[Auth Store] ✅ Login complete - isAuthenticated: true');
    } catch (error) {
      console.error('[Auth Store] ❌ Login failed:', error);
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    console.log('[Auth Store] Logout - Clearing auth data');
    storage.clear();
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  },

  loadUserFromStorage: () => {
    console.log('[Auth Store] Loading user from storage...');
    const token = storage.getToken();
    const user = storage.getUser();
    if (token && user) {
      console.log('[Auth Store] ✅ Found stored auth:', {
        user: user.username,
        tokenPreview: token.substring(0, 20) + '...',
        permissions: user.permissions
      });
      set({
        token,
        user,
        isAuthenticated: true,
        isLoading: false, // CRITICAL FIX: Loading finished
      });
      console.log('[Auth Store] ✅ Auth restored from storage - isAuthenticated: true');
    } else {
      console.log('[Auth Store] ℹ️ No stored auth found (token:', !!token, 'user:', !!user, ')');
      set({
        isLoading: false, // CRITICAL FIX: Loading finished, nincs stored auth
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
