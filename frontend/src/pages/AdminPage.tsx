/**
 * AdminPage - Adminisztrációs Dashboard
 *
 * Layout:
 *   - Bal oldal: Sidebar (navigációs menü)
 *   - Jobb oldal: Tartalom (gyermek komponens renderelése)
 *
 * Jogosultság: menu:manage (ProtectedRoute-ban ellenőrzött)
 */

import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import './AdminPage.css';

interface MenuItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  permission?: string; // Opcionális jogosultság-ellenőrzés
}

const MENU_ITEMS: MenuItem[] = [
  {
    id: 'products',
    label: 'Termékek',
    icon: '📦',
    path: '/admin/products',
    permission: 'menu:manage',
  },
  // CRITICAL FIX (C8.1): Comment out Categories link until CategoryList component is created
  // {
  //   id: 'categories',
  //   label: 'Kategóriák',
  //   icon: '📁',
  //   path: '/admin/categories',
  //   permission: 'menu:manage',
  // },
  {
    id: 'tables',
    label: 'Asztalok',
    icon: '🪑',
    path: '/admin/tables',
    permission: 'orders:manage',
  },
  {
    id: 'employees',
    label: 'Munkavállalók',
    icon: '👥',
    path: '/admin/employees',
    permission: 'employees:manage',
  },
  {
    id: 'roles',
    label: 'Szerepkörök',
    icon: '🔐',
    path: '/admin/roles',
    permission: 'roles:manage',
  },
  // ÚJ MENÜPONT - FÁZIS 3 (Finance)
  {
    id: 'finance',
    label: 'Pénzügy',
    icon: '💰',
    path: '/admin/finance',
    permission: 'finance:manage', // TODO: Add finance:manage permission to RBAC
  },
  // ÚJ MENÜPONT - FÁZIS 3.3 (Assets)
  {
    id: 'assets',
    label: 'Tárgyi Eszközök',
    icon: '🏭',
    path: '/admin/assets',
    permission: 'assets:manage', // TODO: Add assets:manage permission to RBAC
  },
  // ÚJ MENÜPONT - FÁZIS 3.5 (Vehicles)
  {
    id: 'vehicles',
    label: 'Gépjárművek',
    icon: '🚗',
    path: '/admin/vehicles',
    permission: 'vehicles:manage', // TODO: Add vehicles:manage permission to RBAC
  },
  // CRM menüpontok
  {
    id: 'customers',
    label: 'Vendégek',
    icon: '👤',
    path: '/admin/customers',
    permission: 'menu:manage', // TODO: Add crm:manage permission
  },
  {
    id: 'coupons',
    label: 'Kuponok',
    icon: '🎫',
    path: '/admin/coupons',
    permission: 'menu:manage', // TODO: Add crm:manage permission
  },
  {
    id: 'gift_cards',
    label: 'Ajándékkártyák',
    icon: '🎁',
    path: '/admin/gift_cards',
    permission: 'menu:manage', // TODO: Add crm:manage permission
  },
  // ÚJ MENÜPONT - V3.0 Hullám 10
  {
    id: 'logistics',
    label: 'Logisztika',
    icon: '🚚',
    path: '/admin/logistics',
    permission: 'menu:manage', // TODO: Add logistics:manage permission
  },
  // ÚJ MENÜPONT - Analytics Dashboard (FE-REP)
  {
    id: 'reports',
    label: 'Riportok',
    icon: '📊',
    path: '/admin/reports',
    permission: 'menu:manage', // TODO: Add reports:view permission
  },
];

export const AdminPage = () => {
  const { user, logout, hasPermission } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Menüpont kattintás
  const handleMenuClick = (item: MenuItem) => {
    // Jogosultság ellenőrzés (opcionális, a route is védett)
    if (item.permission && !hasPermission(item.permission)) {
      alert('Nincs jogosultságod ehhez a funkcióhoz!');
      return;
    }
    navigate(item.path);
  };

  // Aktív menüpont meghatározása (jelenlegi URL alapján)
  const isActiveMenuItem = (path: string): boolean => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <div className="admin-page">
      {/* Oldalsáv (Sidebar) */}
      <aside className="admin-sidebar">
        <div className="sidebar-header">
          <h2>⚙️ Admin</h2>
          <div className="user-badge">
            <span className="user-name">{user?.name}</span>
            <span className="user-role">
              {user?.roles.map((r) => r.name).join(', ')}
            </span>
          </div>
        </div>

        {/* Navigációs menü */}
        <nav className="sidebar-menu">
          {MENU_ITEMS.map((item) => {
            // Rejtett menüpont, ha nincs jogosultság
            if (item.permission && !hasPermission(item.permission)) {
              return null;
            }

            return (
              <button
                key={item.id}
                onClick={() => handleMenuClick(item)}
                className={`menu-item ${
                  isActiveMenuItem(item.path) ? 'active' : ''
                }`}
              >
                <span className="menu-icon">{item.icon}</span>
                <span className="menu-label">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Kijelentkezés gomb */}
        <div className="sidebar-footer">
          <button onClick={logout} className="logout-btn">
            🚪 Kijelentkezés
          </button>
        </div>
      </aside>

      {/* Főtartalom (Route-ok renderelése) */}
      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  );
};
