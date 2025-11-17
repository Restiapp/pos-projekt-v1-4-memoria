/**
 * App - Fő alkalmazás komponens (Routing)
 */

import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { LoginPage } from '@/pages/LoginPage';
import { TableMapPage } from '@/pages/TableMapPage';
import { KdsPage } from '@/pages/KdsPage';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

function App() {
  const { loadUserFromStorage } = useAuth();

  // Komponens mount-kor: storage-ból betöltjük a user-t (ha van)
  useEffect(() => {
    loadUserFromStorage();
  }, [loadUserFromStorage]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Route */}
        <Route path="/login" element={<LoginPage />} />

        {/* ÚJ ROUTE: Asztaltérkép */}
        <Route
          path="/tables"
          element={
            <ProtectedRoute>
              <TableMapPage />
            </ProtectedRoute>
          }
        />

        {/* ÚJ ROUTE: Konyhai Kijelző (KDS) */}
        <Route
          path="/kds"
          element={
            <ProtectedRoute>
              <KdsPage />
            </ProtectedRoute>
          }
        />

        {/* Default redirect: Asztaltérképre */}
        <Route path="/" element={<Navigate to="/tables" replace />} />

        {/* 404 - Not Found */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
