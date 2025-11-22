/**
 * ProtectedRoute - Védett útvonal komponens
 * Csak bejelentkezett felhasználók férhetnek hozzá
 */

import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: string; // Opcionális jogosultság-ellenőrzés
}

export const ProtectedRoute = ({
  children,
  requiredPermission,
}: ProtectedRouteProps) => {
  const { isAuthenticated, hasPermission, isLoading } = useAuth();

  // DEBUG LOGGING
  console.log('[ProtectedRoute] Check:', {
    isAuthenticated,
    isLoading,
    requiredPermission,
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

  console.log('[ProtectedRoute] ✅ Access granted');
  return <>{children}</>;
};
