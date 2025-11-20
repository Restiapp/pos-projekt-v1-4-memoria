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
import { CustomerList } from '@/components/admin/CustomerList';
import { CouponList } from '@/components/admin/CouponList';
import { GiftCardList } from '@/components/admin/GiftCardList';

// ÚJ IMPORTOK - V3.0 Hullám 10
import { OperatorPage } from '@/pages/OperatorPage';
import { LogisticsPage } from '@/pages/LogisticsPage';

// ÚJ IMPORT - Fázis 3 (Finance)
import { FinancePage } from '@/pages/FinancePage';

// ÚJ IMPORT - Fázis 3.3 (Assets)
import { AssetsPage } from '@/pages/AssetsPage';

// ÚJ IMPORT - Fázis 3.5 (Vehicles)
import { VehiclesPage } from '@/pages/VehiclesPage';

// ÚJ IMPORT - Module 5 (Inventory)
import { InventoryPage } from '@/pages/InventoryPage';

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

        {/* ÚJ ROUTE: Operátori Felület (Telefonos Rendelésfelvétel) */}
        <Route
          path="/operator"
          element={
            <ProtectedRoute>
              <OperatorPage />
            </ProtectedRoute>
          }
        />

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
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <ProductList />
              </ProtectedRoute>
            }
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

          {/* ÚJ: Nested Route: /admin/finance - Pénzügy és Zárások - FÁZIS 3 */}
          <Route
            path="finance"
            element={
              <ProtectedRoute requiredPermission="finance:manage">
                <FinancePage />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/assets - Tárgyi Eszközök - FÁZIS 3.3 */}
          <Route
            path="assets"
            element={
              <ProtectedRoute requiredPermission="assets:manage">
                <AssetsPage />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/vehicles - Gépjárművek - FÁZIS 3.5 */}
          <Route
            path="vehicles"
            element={
              <ProtectedRoute requiredPermission="vehicles:manage">
                <VehiclesPage />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/customers - CRM Vendégek */}
          <Route
            path="customers"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <CustomerList />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/coupons - CRM Kuponok */}
          <Route
            path="coupons"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <CouponList />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/gift_cards - CRM Ajándékkártyák */}
          <Route
            path="gift_cards"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <GiftCardList />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/logistics - Logisztikai Adminisztráció */}
          <Route
            path="logistics"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <LogisticsPage />
              </ProtectedRoute>
            }
          />

          {/* ÚJ: Nested Route: /admin/inventory - Raktárkezelés - MODULE 5 */}
          <Route
            path="inventory"
            element={
              <ProtectedRoute requiredPermission="menu:manage">
                <InventoryPage />
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
