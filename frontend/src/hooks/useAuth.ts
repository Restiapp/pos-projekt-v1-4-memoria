/**
 * useAuth Hook - Auth state és metódusok egyszerű elérése
 */

import { useAuthStore } from '@/stores/authStore';

export const useAuth = () => {
  const {
    token,
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    loadUserFromStorage,
    fetchCurrentUser,
  } = useAuthStore();

  // Jogosultság ellenőrző helper
  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    return user.permissions.includes(permission);
  };

  // Szerepkör ellenőrző helper
  const hasRole = (roleName: string): boolean => {
    if (!user) return false;
    return user.roles.some((role) => role.name === roleName);
  };

  return {
    token,
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    loadUserFromStorage,
    fetchCurrentUser,
    hasPermission,
    hasRole,
  };
};
