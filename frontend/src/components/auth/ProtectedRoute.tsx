/**
 * ProtectedRoute - Védett útvonal komponens
 * Csak bejelentkezett felhasználók férhetnek hozzá
 *
 * Supports both permission-based and role-based access control:
 * - requiredPermission: Check if user has specific permission (e.g., "orders:manage")
 * - requiredRole: Check if user has specific role (e.g., "admin")
 * - allowedRoles: Check if user has any of the specified roles (e.g., ["admin", "waiter"])
 */

import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: string; // Opcionális jogosultság-ellenőrzés
  requiredRole?: string; // Opcionális szerepkör-ellenőrzés (pontosan ez a szerepkör kell)
  allowedRoles?: string[]; // Opcionális szerepkör-ellenőrzés (bármelyik szerepkör megfelelő)
}

export const ProtectedRoute = ({
  children,
  requiredPermission,
  requiredRole,
  allowedRoles,
}: ProtectedRouteProps) => {
  const { isAuthenticated, hasPermission, hasRole, isLoading } = useAuth();

  // DEBUG LOGGING
  console.log('[ProtectedRoute] Check:', {
    isAuthenticated,
    isLoading,
    requiredPermission,
    requiredRole,
    allowedRoles,
    path: window.location.pathname
  });

  // CRITICAL FIX: Várunk amíg az initial auth check befejeződik
  // Ez megelőzi a race condition-t amikor a loadUserFromStorage() még fut
  if (isLoading) {
    console.log('[ProtectedRoute] ⏳ Loading auth state...');
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Betöltés...</p>
        </div>
      </div>
    );
  }

  // Nincs bejelentkezve → redirect /login
  if (!isAuthenticated) {
    console.log('[ProtectedRoute] ❌ Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  // Van jogosultság követelmény és nincs meg → redirect /unauthorized
  if (requiredPermission && !hasPermission(requiredPermission)) {
    console.log('[ProtectedRoute] ❌ Missing permission:', requiredPermission);
    return <Navigate to="/unauthorized" replace />;
  }

  // Van szerepkör követelmény és nincs meg → redirect /unauthorized
  if (requiredRole && !hasRole(requiredRole)) {
    console.log('[ProtectedRoute] ❌ Missing required role:', requiredRole);
    return <Navigate to="/unauthorized" replace />;
  }

  // Van allowedRoles lista és egyik sincs meg → redirect /unauthorized
  if (allowedRoles && allowedRoles.length > 0) {
    const hasAnyRole = allowedRoles.some((role) => hasRole(role));
    if (!hasAnyRole) {
      console.log('[ProtectedRoute] ❌ Missing any of allowed roles:', allowedRoles);
      return <Navigate to="/unauthorized" replace />;
    }
  }

  console.log('[ProtectedRoute] ✅ Access granted');
  return <>{children}</>;
};
