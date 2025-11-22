/**
 * EmployeeList - Munkatársak listázása és kezelése
 *
 * Funkciók:
 *   - Munkatársak listázása táblázatban (lapozással)
 *   - Új munkatárs létrehozása (modal nyitás)
 *   - Munkatárs szerkesztése (modal nyitás)
 *   - Munkatárs törlése (megerősítéssel)
 *   - Frissítés gomb
 *   - Szűrés (aktív/inaktív munkatársak)
 *   - Keresés (név vagy username)
 */

import { useState, useEffect } from 'react';
import { getEmployees, deleteEmployee, getRoles } from '@/services/employeeService';
import { EmployeeEditor } from './EmployeeEditor';
import type { Employee, Role } from '@/types/employee';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './EmployeeList.css';

export const EmployeeList = () => {
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);

  // Szűrő állapot
  const [showOnlyActive, setShowOnlyActive] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Munkatársak betöltése
  const fetchEmployees = async () => {
    try {
      setIsLoading(true);
      const response = await getEmployees(
        page,
        pageSize,
        showOnlyActive ? true : undefined,
        searchQuery || undefined
      );
      setEmployees(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Hiba a munkatársak betöltésekor:', error);
      showToast('Nem sikerült betölteni a munkatársakat!', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Szerepkörök betöltése (editor dropdown-hoz)
  const fetchRoles = async () => {
    try {
      const data = await getRoles();
      setRoles(data);
    } catch (error) {
      console.error('Hiba a szerepkörök betöltésekor:', error);
    }
  };

  // Első betöltés
  useEffect(() => {
    fetchEmployees();
  }, [page, showOnlyActive, searchQuery]);

  useEffect(() => {
    fetchRoles();
  }, []);

  // Új munkatárs létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingEmployee(null);
    setIsEditorOpen(true);
  };

  // Munkatárs szerkesztése (modal nyitás)
  const handleEdit = (employee: Employee) => {
    setEditingEmployee(employee);
    setIsEditorOpen(true);
  };

  // Munkatárs törlése (megerősítéssel)
  const handleDelete = async (employee: Employee) => {
    const confirmed = await showConfirm(
      `Biztosan törölni szeretnéd ezt a munkatársat?\n\n${employee.full_name} (${employee.username})`
    );

    if (!confirmed) return;

    try {
      await deleteEmployee(employee.id);
      showToast('Munkatárs sikeresen törölve!', 'success');
      fetchEmployees(); // Lista frissítése
    } catch (error) {
      console.error('Hiba a munkatárs törlésekor:', error);
      showToast('Nem sikerült törölni a munkatársat!', 'error');
    }
  };

  // Editor bezárása és lista frissítése
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingEmployee(null);
    if (shouldRefresh) {
      fetchEmployees();
    }
  };

  // Szerepkör neve ID alapján
  const getRoleName = (roleId?: number | null): string => {
    if (!roleId) return '-';
    const role = roles.find((r) => r.id === roleId);
    return role?.name || '-';
  };

  // Dátum formázása
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('hu-HU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  // Keresés kezelés (debounce nélkül egyelőre)
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setPage(1); // Visszaállítjuk az első oldalra keresés esetén
  };

  return (
    <div className="employee-list">
      {/* Fejléc */}
      <header className="list-header">
        <h1>👥 Munkatársak</h1>
        <div className="header-controls">
          {/* Keresés */}
          <input
            type="text"
            placeholder="Keresés (név, username)..."
            value={searchQuery}
            onChange={handleSearchChange}
            className="search-input"
          />

          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={showOnlyActive}
              onChange={(e) => {
                setShowOnlyActive(e.target.checked);
                setPage(1);
              }}
            />
            Csak aktív munkatársak
          </label>
          <button onClick={fetchEmployees} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="create-btn">
            ➕ Új munkatárs
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && employees.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="employees-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Teljes név</th>
                  <th>Felhasználónév</th>
                  <th>Email</th>
                  <th>Szerepkör</th>
                  <th>Aktív</th>
                  <th>Létrehozva</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {employees.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="empty-state">
                      Nincsenek munkatársak
                    </td>
                  </tr>
                ) : (
                  employees.map((employee) => (
                    <tr key={employee.id}>
                      <td>{employee.id}</td>
                      <td>
                        <strong>{employee.full_name}</strong>
                      </td>
                      <td>{employee.username}</td>
                      <td>{employee.email}</td>
                      <td>{getRoleName(employee.role_id)}</td>
                      <td>
                        <span
                          className={`status-badge ${
                            employee.is_active ? 'active' : 'inactive'
                          }`}
                        >
                          {employee.is_active ? '✅ Aktív' : '❌ Inaktív'}
                        </span>
                      </td>
                      <td>{formatDate(employee.created_at)}</td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(employee)}
                            className="edit-btn"
                            title="Szerkesztés"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDelete(employee)}
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

          {/* Lapozás */}
          <footer className="list-footer">
            <div className="pagination-info">
              Összesen: {total} munkatárs | Oldal: {page}
            </div>
            <div className="pagination-controls">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="page-btn"
              >
                ◀ Előző
              </button>
              <span className="page-number">Oldal {page}</span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={employees.length < pageSize}
                className="page-btn"
              >
                Következő ▶
              </button>
            </div>
          </footer>
        </>
      )}

      {/* Editor Modal */}
      {isEditorOpen && (
        <EmployeeEditor
          employee={editingEmployee}
          roles={roles}
          onClose={handleEditorClose}
        />
      )}
    </div>
  );
};
