/**
 * TableMapPage - Asztaltérkép oldal (wrapper + header)
 * V3.0 Fázis 5: GlobalHeader integrálva
 */

import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { TableMap } from '@/components/table-map/TableMap';
import { useAuth } from '@/hooks/useAuth';
import { storage } from '@/utils/storage';
import './TableMapPage.css';

export const TableMapPage = () => {
  const { isAuthenticated, user, token } = useAuth();
  const storedToken = storage.getToken();

  // Debug info (csak development módban)
  const isDev = import.meta.env.DEV;

  return (
    <div className="table-map-page">
      {/* Globális navigációs header */}
      <GlobalHeader currentPage="tables" />

      {/* Debug panel (only in development) */}
      {isDev && (
        <div style={{
          position: 'fixed',
          bottom: 0,
          right: 0,
          background: 'rgba(0,0,0,0.9)',
          color: '#0f0',
          padding: '10px',
          fontSize: '11px',
          fontFamily: 'monospace',
          maxWidth: '400px',
          zIndex: 9999,
          borderTopLeftRadius: '8px'
        }}>
          <div><strong>🔐 AUTH DEBUG</strong></div>
          <div>Authenticated: {isAuthenticated ? '✅ YES' : '❌ NO'}</div>
          <div>User: {user?.username || '❌ null'}</div>
          <div>Token in Store: {token ? '✅ YES (' + token.substring(0, 15) + '...)' : '❌ null'}</div>
          <div>Token in Storage: {storedToken ? '✅ YES (' + storedToken.substring(0, 15) + '...)' : '❌ null'}</div>
          <div>Permissions: {user?.permissions?.join(', ') || '❌ none'}</div>
          <div>Has orders:manage: {user?.permissions?.includes('orders:manage') ? '✅ YES' : '❌ NO'}</div>
        </div>
      )}

      {/* Fő tartalom */}
      <main className="page-content">
        <TableMap />
      </main>
    </div>
  );
};
