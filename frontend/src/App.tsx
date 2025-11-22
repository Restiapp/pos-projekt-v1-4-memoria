/**
 * App - Fő alkalmazás komponens (Routing)
 *
 * AGENT #8 FIX: Cleaned up routing structure
 * - Removed unused DashboardPage import
 * - Optimized ProtectedRoute usage
 * - Added proper route organization
 */

import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

// === PUBLIC PAGES ===
import { LoginPage } from '@/pages/LoginPage';

// === MAIN PAGES ===
import { TableMapPage } from '@/pages/TableMapPage';
import { KdsPage } from '@/pages/KdsPage';
import { PaymentPage } from '@/pages/PaymentPage';
import { OperatorPage } from '@/pages/OperatorPage';

// === ADMIN PAGES ===
import { AdminPage } from '@/pages/AdminPage';
import { FinancePage } from '@/pages/FinancePage';
import { AssetsPage } from '@/pages/AssetsPage';
import { VehiclesPage } from '@/pages/VehiclesPage';
import { LogisticsPage } from '@/pages/LogisticsPage';

// === ADMIN COMPONENTS ===
import { ProductList } from '@/components/admin/ProductList';
import { TableList } from '@/components/admin/TableList';
import { EmployeeList } from '@/components/admin/EmployeeList';
import { RoleList } from '@/components/admin/RoleList';
import { CustomerList } from '@/components/admin/CustomerList';
import { CouponList } from '@/components/admin/CouponList';
import { GiftCardList } from '@/components/admin/GiftCardList';

// === AUTH ===
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
        {/* ===== PUBLIC ROUTES ===== */}
        <Route path="/login" element={<LoginPage />} />

        {/* ===== MAIN APPLICATION ROUTES ===== */}

        {/* Waiter Mode - Table Management */}
        <Route
          path="/tables"
          element={
            <ProtectedRoute>
              <TableMapPage />
            </ProtectedRoute>
          }
        />

        {/* Kitchen Display System (Bar/Kitchen) */}
        <Route
          path="/kds"
          element={
            <ProtectedRoute>
              <KdsPage />
            </ProtectedRoute>
          }
        />

        {/* Operator Mode - Phone Orders (Dispatcher) */}
        <Route
          path="/operator"
          element={
            <ProtectedRoute>
              <OperatorPage />
            </ProtectedRoute>
          }
        />

        {/* Payment Screen */}
        <Route
          path="/orders/:orderId/pay"
          element={
            <ProtectedRoute>
              <PaymentPage />
            </ProtectedRoute>
          }
        />

        {/* ===== ADMIN ROUTES ===== */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminPage />
            </ProtectedRoute>
          }
        >
          {/* Default Admin Route - Redirect to Products */}
          <Route index element={<Navigate to="/admin/products" replace />} />

          {/* Menu Management */}
          <Route
            path="products"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <ProductList />
              </ProtectedRoute>
            }
          />

          {/* Table Management */}
          <Route
            path="tables"
            element={
              <ProtectedRoute requiredPermission="orders:manage">
                <TableList />
              </ProtectedRoute>
            }
          />

          {/* Employee Management */}
          <Route
            path="employees"
            element={
              <ProtectedRoute requiredPermission="employees:manage">
                <EmployeeList />
              </ProtectedRoute>
            }
          />

          {/* Role Management */}
          <Route
            path="roles"
            element={
              <ProtectedRoute requiredPermission="roles:manage">
                <RoleList />
              </ProtectedRoute>
            }
          />

          {/* Finance Management */}
          <Route
            path="finance"
            element={
              <ProtectedRoute requiredPermission="finance:manage">
                <FinancePage />
              </ProtectedRoute>
            }
          />

          {/* Asset Management */}
          <Route
            path="assets"
            element={
              <ProtectedRoute requiredPermission="assets:manage">
                <AssetsPage />
              </ProtectedRoute>
            }
          />

          {/* Vehicle Management */}
          <Route
            path="vehicles"
            element={
              <ProtectedRoute requiredPermission="vehicles:manage">
                <VehiclesPage />
              </ProtectedRoute>
            }
          />

          {/* CRM - Customer Management */}
          <Route
            path="customers"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <CustomerList />
              </ProtectedRoute>
            }
          />

          {/* CRM - Coupon Management */}
          <Route
            path="coupons"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <CouponList />
              </ProtectedRoute>
            }
          />

          {/* CRM - Gift Card Management */}
          <Route
            path="gift_cards"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <GiftCardList />
              </ProtectedRoute>
            }
          />

          {/* Logistics Management */}
          <Route
            path="logistics"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <LogisticsPage />
              </ProtectedRoute>
            }
          />
        </Route>

        {/* ===== UTILITY ROUTES ===== */}

        {/* Default Redirect */}
        <Route path="/" element={<Navigate to="/tables" replace />} />

        {/* 403 - Unauthorized Access */}
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

        {/* 404 - Not Found */}
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
