/**
 * TableMapPage - Asztaltérkép oldal (wrapper + header)
 */

import { useAuth } from '@/hooks/useAuth';
import { TableMap } from '@/components/table-map/TableMap';
import './TableMapPage.css';

export const TableMapPage = () => {
  const { user, logout } = useAuth();

  return (
    <div className="table-map-page">
      <header className="page-header">
        <h1>🍽️ Asztaltérkép</h1>
        <div className="user-info">
          <span>👤 {user?.name}</span>
          <button onClick={logout} className="logout-btn">
            Kijelentkezés
          </button>
        </div>
      </header>

      <main className="page-content">
        <TableMap />
      </main>
    </div>
  );
};
