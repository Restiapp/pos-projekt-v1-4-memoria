import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/common/Toast';
import './AdminPage.css';

interface MenuItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  permission?: string;
}

const MENU_ITEMS: MenuItem[] = [
  { id: 'products', label: 'Termékek', icon: 'PRD', path: '/admin/products', permission: 'menu:manage' },
  { id: 'tables', label: 'Asztalok', icon: 'TBL', path: '/admin/tables', permission: 'orders:manage' },
  { id: 'floorplan', label: 'Alaprajz', icon: 'MAP', path: '/admin/floorplan', permission: 'orders:manage' },
  { id: 'employees', label: 'Munkavállalók', icon: 'EMP', path: '/admin/employees', permission: 'employees:manage' },
  { id: 'roles', label: 'Szerepkörök', icon: 'ROL', path: '/admin/roles', permission: 'roles:manage' },
  { id: 'finance', label: 'Pénzügy', icon: 'FIN', path: '/admin/finance', permission: 'finance:manage' },
  { id: 'assets', label: 'Tárgyi eszközök', icon: 'AST', path: '/admin/assets', permission: 'assets:manage' },
  { id: 'vehicles', label: 'Gépjárművek', icon: 'VEH', path: '/admin/vehicles', permission: 'vehicles:manage' },
  { id: 'reports', label: 'Riportok', icon: 'RPT', path: '/admin/reports', permission: 'reports:view' },
  { id: 'customers', label: 'Vendégek', icon: 'CUS', path: '/admin/customers', permission: 'menu:manage' },
  { id: 'coupons', label: 'Kuponok', icon: 'CPN', path: '/admin/coupons', permission: 'menu:manage' },
  { id: 'gift_cards', label: 'Ajándékkártyák', icon: 'GFT', path: '/admin/gift_cards', permission: 'menu:manage' },
  { id: 'logistics', label: 'Logisztika', icon: 'LOG', path: '/admin/logistics', permission: 'menu:manage' },
  { id: 'inventory', label: 'Raktárkezelés', icon: 'INV', path: '/admin/inventory', permission: 'menu:manage' },
];

export const AdminPage = () => {
  const { showToast } = useToast();
  const { user, logout, hasPermission } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleMenuClick = (item: MenuItem) => {
    if (item.permission && !hasPermission(item.permission)) {
      showToast('Nincs jogosultságod ehhez a funkcióhoz!', 'error');
      return;
    }
    navigate(item.path);
  };

  const isActiveMenuItem = (path: string): boolean => {
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  return (
    <div className="admin-page">
      <aside className="admin-sidebar">
        <div className="sidebar-header">
          <h2>Admin</h2>
          <div className="user-badge">
            <span className="user-name">{user?.name}</span>
            <span className="user-role">{user?.roles.map((role) => role.name).join(', ')}</span>
          </div>
        </div>

        <nav className="sidebar-menu">
          {MENU_ITEMS.filter((item) => !item.permission || hasPermission(item.permission)).map((item) => (
            <button
              key={item.id}
              onClick={() => handleMenuClick(item)}
              className={`menu-item ${isActiveMenuItem(item.path) ? 'active' : ''}`}
            >
              <span className="menu-icon">{item.icon}</span>
              <span className="menu-label">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button onClick={logout} className="logout-btn">
            Kilépés
          </button>
        </div>
      </aside>

      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  );
};
