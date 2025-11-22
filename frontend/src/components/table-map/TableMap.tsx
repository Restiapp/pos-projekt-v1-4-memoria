/**
 * TableMap - Főkomponens: Asztaltérkép megjelenítése
 * Fetch-eli az összes asztalt és grid layout-ban jeleníti meg
 */

import { useState, useEffect } from 'react';
import { getTables } from '@/services/tableService';
import { TableIcon } from './TableIcon';
import type { Table } from '@/types/table';
import { useToast } from '@/components/common/Toast';
import './TableMap.css';

export const TableMap = () => {
  const { showToast } = useToast();
  const [tables, setTables] = useState<Table[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Asztalok betöltése
  useEffect(() => {
    const fetchTables = async () => {
      try {
        setLoading(true);
        const data = await getTables();
        setTables(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch tables:', err);
        setError('Nem sikerült betölteni az asztalokat. Kérjük, próbálja újra.');
      } finally {
        setLoading(false);
      }
    };

    fetchTables();
  }, []);

  // Asztal kattintás kezelése
  const handleTableClick = (table: Table) => {
    console.log('Asztal kiválasztva:', table);
    // TODO: Navigáció a rendelés oldalra vagy részletek megjelenítése
    showToast(`Asztal: ${table.table_number} (ID: ${table.id})`, 'info');
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
