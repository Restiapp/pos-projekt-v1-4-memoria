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
  const { isAuthenticated, hasPermission } = useAuth();

  // Nincs bejelentkezve → redirect /login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Van jogosultság követelmény és nincs meg → redirect /unauthorized
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
