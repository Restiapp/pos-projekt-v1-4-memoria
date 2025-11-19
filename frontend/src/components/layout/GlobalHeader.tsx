/**
 * GlobalHeader - Globális Navigációs Header
 *
 * V3.0 Fázis 5: Tiszta belépési pontok a 4 főfunkcióhoz
 *
 * Funkciók:
 *   - Asztaltérkép (Pincér módusz)
 *   - Konyhai Kijelző (KDS)
 *   - Operátori Felület (Telefonos rendelés)
 *   - Admin Dashboard
 *
 * Használat:
 *   <GlobalHeader currentPage="tables" />
 */

import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import './GlobalHeader.css';

interface GlobalHeaderProps {
  /** Jelenlegi oldal azonosítója (highlighting) */
  currentPage?: 'tables' | 'kds' | 'operator' | 'admin' | 'orders';
}

interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  description: string;
}

const NAV_ITEMS: NavItem[] = [
  {
    id: 'tables',
    label: 'Asztaltérkép',
    icon: '🍽️',
    path: '/tables',
    description: 'Pincér módusz - Asztalok kezelése',
  },
  {
    id: 'orders',
    label: 'Rendelés',
    icon: '📝',
    path: '/orders/new',
    description: 'Új rendelés felvétele',
  },
  {
    id: 'kds',
    label: 'Konyhai Kijelző',
    icon: '👨‍🍳',
    path: '/kds',
    description: 'Valós idejű rendelés megjelenítés',
  },
  {
    id: 'operator',
    label: 'Operátor',
    icon: '📞',
    path: '/operator',
    description: 'Telefonos rendelésfelvétel',
  },
  {
    id: 'admin',
    label: 'Admin',
    icon: '⚙️',
    path: '/admin/products',
    description: 'Adminisztráció és beállítások',
  },
];

export const GlobalHeader = ({ currentPage }: GlobalHeaderProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  // Aktív oldal meghatározása (auto-detect, ha nincs currentPage prop)
  const getActivePage = (): string | undefined => {
    if (currentPage) return currentPage;

    const path = location.pathname;
    if (path.startsWith('/tables')) return 'tables';
    if (path.startsWith('/orders')) return 'orders';
    if (path.startsWith('/kds')) return 'kds';
    if (path.startsWith('/operator')) return 'operator';
    if (path.startsWith('/admin')) return 'admin';

    return undefined;
  };

  const activePage = getActivePage();

  return (
    <header className="global-header">
      <div className="global-header-content">
        {/* BAL OLDAL: Logo / Alkalmazás név */}
        <div className="global-header-brand">
          <h1 className="brand-title">🍕 POS System V3.0</h1>
        </div>

        {/* KÖZÉPSŐ RÉSZ: Navigációs Linkek */}
        <nav className="global-header-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => navigate(item.path)}
              className={`nav-item ${activePage === item.id ? 'active' : ''}`}
              title={item.description}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* JOBB OLDAL: Felhasználó info + Kijelentkezés */}
        <div className="global-header-user">
          <span className="user-name">👤 {user?.name}</span>
          <button onClick={logout} className="logout-btn" title="Kijelentkezés">
            🚪 Kilépés
          </button>
        </div>
      </div>
    </header>
  );
};
