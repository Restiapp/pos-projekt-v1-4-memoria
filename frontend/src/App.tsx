/**
 * App - Fő alkalmazás komponens (Routing)
 */

import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { LoginPage } from '@/pages/LoginPage';
import { TableMapPage } from '@/pages/TableMapPage';
import { KdsPage } from '@/pages/KdsPage';
import { PaymentPage } from '@/pages/PaymentPage';
import { AdminPage } from '@/pages/AdminPage';
import { ProductList } from '@/components/admin/ProductList';
import { TableList } from '@/components/admin/TableList';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { EmployeeList } from '@/components/admin/EmployeeList';
import { RoleList } from '@/components/admin/RoleList';

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

        {/* ÚJ ROUTE: Fizetési Képernyő */}
        <Route
          path="/orders/:orderId/pay"
          element={
            <ProtectedRoute>
              <PaymentPage />
            </ProtectedRoute>
          }
        />

        {/* ÚJ ROUTE: Admin Dashboard (Nested Routes) */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminPage />
            </ProtectedRoute>
          }
        >
          {/* Nested Route: /admin/products - RBAC Protected */}
          <Route
            path="products"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <ProductList />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/tables - RBAC Protected */}
          <Route
            path="tables"
            element={
              <ProtectedRoute requiredPermission="tables:manage">
                <TableList />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/employees - RBAC Protected */}
          <Route
            path="employees"
            element={
              <ProtectedRoute requiredPermission="employees:manage">
                <EmployeeList />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/roles - RBAC Protected */}
          <Route
            path="roles"
            element={
              <ProtectedRoute requiredPermission="roles:manage">
                <RoleList />
              </ProtectedRoute>
            }
          />

          {/* TODO: További admin modulok (kategóriák, stb.) */}
          {/* <Route path="categories" element={<CategoryList />} /> */}
        </Route>

        {/* Default redirect: Asztaltérképre */}
        <Route path="/" element={<Navigate to="/tables" replace />} />

        {/* 404 - Not Found */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
