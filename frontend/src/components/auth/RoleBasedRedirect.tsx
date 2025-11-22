/**
 * RoleBasedRedirect - Redirects user to their default route based on role
 *
 * Usage: <Route path="/" element={<RoleBasedRedirect />} />
 */

import { Navigate } from 'react-router-dom';
import { useUserRole } from '@/hooks/useUserRole';
import { useAuth } from '@/hooks/useAuth';

export const RoleBasedRedirect = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const { getDefaultRoute } = useUserRole();

  // Wait for auth to load
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Betöltés...</p>
        </div>
      </div>
    );
  }

  // Not authenticated -> login
  if (!isAuthenticated) {
    console.log('[RoleBasedRedirect] Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  // Get default route for user's role
  const defaultRoute = getDefaultRoute();
  console.log('[RoleBasedRedirect] Redirecting to default route:', defaultRoute);
  return <Navigate to={defaultRoute} replace />;
};
