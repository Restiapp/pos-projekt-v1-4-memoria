/**
 * TableMap - Főkomponens: Asztaltérkép megjelenítése
 * Fetch-eli az összes asztalt és grid layout-ban jeleníti meg
 */

import { useState, useEffect } from 'react';
import { getTables } from '@/services/tableService';
import { TableIcon } from './TableIcon';
import type { Table } from '@/types/table';
import { useAuthStore } from '@/stores/authStore';
import { notify } from '@/utils/notifications';
import './TableMap.css';

export const TableMap = () => {
  const { isAuthenticated } = useAuthStore();

  const [tables, setTables] = useState<Table[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Asztalok betöltése
  useEffect(() => {
    const fetchTables = async () => {
      try {
        console.log('[TableMap] Fetching tables...');
        setLoading(true);
        const data = await getTables();
        console.log('[TableMap] ✅ Tables loaded:', data.length, 'tables');
        setTables(data);
        setError(null);
      } catch (err: any) {
        console.error('[TableMap] ❌ Failed to fetch tables:', err);
        let errorMessage = 'Nem sikerült betölteni az asztalokat.';

        if (err.response?.status === 401) {
          errorMessage = '❌ Nincs bejelentkezve. Kérjük jelentkezzen be újra.';
        } else if (err.response?.status === 403) {
          errorMessage = '❌ Nincs jogosultsága az asztalok megtekintéséhez. Szükséges jogosultság: orders:manage';
        } else if (err.response?.data?.detail) {
          errorMessage = `❌ ${err.response.data.detail}`;
        } else if (err.message) {
          errorMessage = `❌ ${err.message}`;
        }

        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchTables();
    }
  }, [isAuthenticated]);

  // Asztal kattintás kezelése
  const handleTableClick = (table: Table) => {
    console.log('Asztal kiválasztva:', table);
    // TODO: Navigáció a rendelés oldalra vagy részletek megjelenítése
    notify.info(`Asztal: ${table.table_number} (ID: ${table.id})`);
  };

  if (loading) {
    return (
      <div className="table-map-loading">
        <p>Asztalok betöltése...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="table-map-error">
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Újrapróbálás</button>
      </div>
    );
  }

  if (tables.length === 0) {
    return (
      <div className="table-map-empty">
        <p>Nincs elérhető asztal.</p>
      </div>
    );
  }

  return (
    <div className="table-map-container">
      <div className="table-grid">
        {tables.map((table) => (
          <TableIcon
            key={table.id}
            table={table}
            occupiedSeats={0} // TODO: Rendelések alapján számítani
            onClick={handleTableClick}
          />
        ))}
      </div>
    </div>
  );
};
