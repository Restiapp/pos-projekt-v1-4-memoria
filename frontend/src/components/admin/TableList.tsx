/**
 * TableList - Asztalok listázása és kezelése
 *
 * Funkciók:
 *   - Asztalok listázása táblázatban
 *   - Új asztal létrehozása (modal nyitás)
 *   - Asztal szerkesztése (modal nyitás)
 *   - Asztal törlése (megerősítéssel)
 *   - Frissítés gomb
 */

import { useState, useEffect } from 'react';
import { getTables, deleteTable } from '@/services/tableService';
import { TableEditor } from './TableEditor';
import type { Table } from '@/types/table';
import './TableList.css';

export const TableList = () => {
  const [tables, setTables] = useState<Table[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingTable, setEditingTable] = useState<Table | null>(null);

  // Asztalok betöltése
  const fetchTables = async () => {
    try {
      setIsLoading(true);
      const data = await getTables();
      setTables(data);
    } catch (error) {
      console.error('Hiba az asztalok betöltésekor:', error);
      alert('Nem sikerült betölteni az asztalokat!');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    fetchTables();
  }, []);

  // Új asztal létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingTable(null);
    setIsEditorOpen(true);
  };

  // Asztal szerkesztése (modal nyitás)
  const handleEdit = (table: Table) => {
    setEditingTable(table);
    setIsEditorOpen(true);
  };

  // Asztal törlése (megerősítéssel)
  const handleDelete = async (table: Table) => {
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt az asztalt?\n\nAsztal: ${table.table_number}`
    );

    if (!confirmed) return;

    try {
      await deleteTable(table.id);
      alert('Asztal sikeresen törölve!');
      fetchTables(); // Lista frissítése
    } catch (error) {
      console.error('Hiba az asztal törlésekor:', error);
      alert('Nem sikerült törölni az asztalt!');
    }
  };

  // Editor bezárása és lista frissítése
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingTable(null);
    if (shouldRefresh) {
      fetchTables();
    }
  };

  return (
    <div className="table-list">
      {/* Fejléc */}
      <header className="list-header">
        <h1>🪑 Asztalok Kezelése</h1>
        <div className="header-controls">
          <button onClick={fetchTables} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="create-btn">
            ➕ Új asztal
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && tables.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="tables-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Asztalszám</th>
                  <th>Pozíció X</th>
                  <th>Pozíció Y</th>
                  <th>Kapacitás</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {tables.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="empty-state">
                      Nincsenek asztalok. Hozz létre egyet!
                    </td>
                  </tr>
                ) : (
                  tables.map((table) => (
                    <tr key={table.id}>
                      <td>{table.id}</td>
                      <td>
                        <strong>{table.table_number}</strong>
                      </td>
                      <td>{table.position_x ?? '-'}</td>
                      <td>{table.position_y ?? '-'}</td>
                      <td>{table.capacity ?? '-'}</td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(table)}
                            className="edit-btn"
                            title="Szerkesztés"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDelete(table)}
                            className="delete-btn"
                            title="Törlés"
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Összesítő */}
          <footer className="list-footer">
            <div className="summary-info">
              Összesen: <strong>{tables.length}</strong> asztal
            </div>
          </footer>
        </>
      )}

      {/* Editor Modal */}
      {isEditorOpen && (
        <TableEditor table={editingTable} onClose={handleEditorClose} />
      )}
    </div>
  );
};
