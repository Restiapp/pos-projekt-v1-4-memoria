/**
 * RoleList - Szerepkörök listázása és kezelése
 *
 * Funkciók:
 *   - Szerepkörök listázása táblázatban (lapozással)
 *   - Új szerepkör létrehozása (modal nyitás)
 *   - Szerepkör szerkesztése (modal nyitás)
 *   - Szerepkör törlése (megerősítéssel)
 *   - Frissítés gomb
 */

import { useState, useEffect } from 'react';
import { getRoles, deleteRole, getPermissions, getRoleById } from '@/services/roleService';
import { RoleEditor } from './RoleEditor';
import type { Role, Permission, RoleWithPermissions } from '@/types/role';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './RoleList.css';

export const RoleList = () => {
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<RoleWithPermissions | null>(null);

  // Szerepkörök betöltése
  const fetchRoles = async () => {
    try {
      setIsLoading(true);
      const response = await getRoles(page, pageSize);
      setRoles(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Hiba a szerepkörök betöltésekor:', error);
      showToast('Nem sikerült betölteni a szerepköröket!', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Jogosultságok betöltése (editor dropdown-hoz)
  const fetchPermissions = async () => {
    try {
      const data = await getPermissions();
      setPermissions(data);
    } catch (error) {
      console.error('Hiba a jogosultságok betöltésekor:', error);
    }
  };

  // Első betöltés
  useEffect(() => {
    fetchRoles();
  }, [page]);

  useEffect(() => {
    fetchPermissions();
  }, []);

  // Új szerepkör létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingRole(null);
    setIsEditorOpen(true);
  };

  // Szerepkör szerkesztése (modal nyitás, részletes adatok betöltése)
  const handleEdit = async (role: Role) => {
    try {
      // Részletes adatok betöltése (jogosultságokkal együtt)
      const detailedRole = await getRoleById(role.id);
      setEditingRole(detailedRole);
      setIsEditorOpen(true);
    } catch (error) {
      console.error('Hiba a szerepkör betöltésekor:', error);
      showToast('Nem sikerült betölteni a szerepkör részleteit!', 'error');
    }
  };

  // Szerepkör törlése (megerősítéssel)
  const handleDelete = async (role: Role) => {
    const confirmed = await showConfirm(
      `Biztosan törölni szeretnéd ezt a szerepkört?\n\n${role.name} - ${role.description}\n\nFigyelem: A szerepkörhöz rendelt munkatársak jogosultságai megszűnnek!`
    );

    if (!confirmed) return;

    try {
      await deleteRole(role.id);
      showToast('Szerepkör sikeresen törölve!', 'success');
      fetchRoles(); // Lista frissítése
    } catch (error) {
      console.error('Hiba a szerepkör törlésekor:', error);
      showToast('Nem sikerült törölni a szerepkört!', 'error');
    }
  };

  // Editor bezárása és lista frissítése
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingRole(null);
    if (shouldRefresh) {
      fetchRoles();
    }
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

  return (
    <div className="role-list">
      {/* Fejléc */}
      <header className="list-header">
        <h1>🔐 Szerepkörök</h1>
        <div className="header-controls">
          <button onClick={fetchRoles} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="create-btn">
            ➕ Új szerepkör
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && roles.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="roles-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Név</th>
                  <th>Leírás</th>
                  <th>Létrehozva</th>
                  <th>Frissítve</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {roles.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="empty-state">
                      Nincsenek szerepkörök
                    </td>
                  </tr>
                ) : (
                  roles.map((role) => (
                    <tr key={role.id}>
                      <td>{role.id}</td>
                      <td>
                        <strong>{role.name}</strong>
                      </td>
                      <td>{role.description}</td>
                      <td>{formatDate(role.created_at)}</td>
                      <td>{formatDate(role.updated_at)}</td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(role)}
                            className="edit-btn"
                            title="Szerkesztés"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDelete(role)}
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
              Összesen: {total} szerepkör | Oldal: {page}
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
                disabled={roles.length < pageSize}
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
        <RoleEditor
          role={editingRole}
          permissions={permissions}
          onClose={handleEditorClose}
        />
      )}
    </div>
  );
};
