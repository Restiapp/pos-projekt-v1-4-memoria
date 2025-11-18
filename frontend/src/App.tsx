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
            <ProtectedRoute requiredPermission="menu:manage">
              <AdminPage />
            </ProtectedRoute>
          }
        >
          {/* Nested Route: /admin/products */}
          <Route
            path="products"
            element={<ProductList />}
          />

          {/* HIGH PRIORITY FIX (H8.1): Add permission checks to nested routes */}
          {/* ÚJ: Nested Route: /admin/tables - requires orders:manage */}
          <Route
            path="tables"
            element={
              <ProtectedRoute requiredPermission="orders:manage">
                <TableList />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/employees - requires employees:manage */}
          <Route
            path="employees"
            element={
              <ProtectedRoute requiredPermission="employees:manage">
                <EmployeeList />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/roles - requires roles:manage */}
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

        {/* CRITICAL FIX (C6.1): Add /unauthorized route for permission denied */}
        <Route
          path="/unauthorized"
          element={
            <div style={{ padding: '2rem', textAlign: 'center' }}>
              <h1>403 - Hozzáférés megtagadva</h1>
              <p>Nincs jogosultságod ehhez az oldalhoz.</p>
              <a href="/tables">Vissza az asztaltérképre</a>
            </div>
          }
        />

        {/* CRITICAL FIX (C6.2): Fix 404 route to not logout authenticated users */}
        <Route
          path="*"
          element={
            <div style={{ padding: '2rem', textAlign: 'center' }}>
              <h1>404 - Az oldal nem található</h1>
              <p>A keresett oldal nem létezik.</p>
              <a href="/tables">Vissza az asztaltérképre</a>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
