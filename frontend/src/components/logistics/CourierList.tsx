/**
 * CourierList - Futárok listázása és kezelése
 *
 * Funkciók:
 *   - Futárok listázása táblázatban (lapozással)
 *   - Új futár létrehozása (modal nyitás)
 *   - Futár szerkesztése (modal nyitás)
 *   - Futár törlése (megerősítéssel)
 *   - Státusz módosítása (gyors váltás)
 *   - Frissítés gomb
 *   - Szűrés (státusz szerint)
 */

import { useState, useEffect } from 'react';
import {
  getCouriers,
  deleteCourier,
  updateCourierStatus,
} from '@/services/logisticsService';
import { CourierEditor } from './CourierEditor';
import type { Courier, CourierStatus } from '@/types/logistics';
import './CourierList.css';

export const CourierList = () => {
  const [couriers, setCouriers] = useState<Courier[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingCourier, setEditingCourier] = useState<Courier | null>(null);

  // Szűrő állapot
  const [statusFilter, setStatusFilter] = useState<CourierStatus | 'all'>('all');
  const [showOnlyActive, setShowOnlyActive] = useState(true);

  // Futárok betöltése
  const fetchCouriers = async () => {
    try {
      setIsLoading(true);
      const response = await getCouriers(
        page,
        pageSize,
        statusFilter !== 'all' ? statusFilter : undefined,
        showOnlyActive ? true : undefined
      );
      setCouriers(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Hiba a futárok betöltésekor:', error);
      alert('Nem sikerült betölteni a futárokat!');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés és frissítés szűrő változásakor
  useEffect(() => {
    fetchCouriers();
  }, [page, statusFilter, showOnlyActive]);

  // Új futár létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingCourier(null);
    setIsEditorOpen(true);
  };

  // Futár szerkesztése (modal nyitás)
  const handleEdit = (courier: Courier) => {
    setEditingCourier(courier);
    setIsEditorOpen(true);
  };

  // Futár törlése (megerősítéssel)
  const handleDelete = async (courier: Courier) => {
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt a futárt?\n\n${courier.courier_name} (${courier.phone})`
    );

    if (!confirmed) return;

    try {
      await deleteCourier(courier.id);
      alert('Futár sikeresen törölve!');
      fetchCouriers(); // Lista frissítése
    } catch (error) {
      console.error('Hiba a futár törlésekor:', error);
      alert('Nem sikerült törölni a futárt!');
    }
  };

  // Státusz gyors módosítása
  const handleStatusChange = async (courier: Courier, newStatus: CourierStatus) => {
    try {
      await updateCourierStatus(courier.id, newStatus);
      alert(`Futár státusza módosítva: ${getStatusLabel(newStatus)}`);
      fetchCouriers(); // Lista frissítése
    } catch (error) {
      console.error('Hiba a státusz módosításakor:', error);
      alert('Nem sikerült módosítani a státuszt!');
    }
  };

  // Editor bezárása és lista frissítése
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingCourier(null);
    if (shouldRefresh) {
      fetchCouriers();
    }
  };

  // Státusz címke
  const getStatusLabel = (status: CourierStatus): string => {
    switch (status) {
      case 'available':
        return 'Elérhető';
      case 'on_delivery':
        return 'Úton';
      case 'offline':
        return 'Offline';
      case 'break':
        return 'Szünet';
      default:
        return status;
    }
  };

  // Státusz badge class
  const getStatusBadgeClass = (status: CourierStatus): string => {
    switch (status) {
      case 'available':
        return 'status-available';
      case 'on_delivery':
        return 'status-on-delivery';
      case 'offline':
        return 'status-offline';
      case 'break':
        return 'status-break';
      default:
        return '';
    }
  };

  // Dátum formázása
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleString('hu-HU');
  };

  return (
    <div className="courier-list">
      {/* Fejléc */}
      <header className="list-header">
        <h2>👷 Futárok</h2>
        <div className="header-controls">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as CourierStatus | 'all')}
            className="filter-select"
          >
            <option value="all">Minden státusz</option>
            <option value="available">Elérhető</option>
            <option value="on_delivery">Úton</option>
            <option value="break">Szünet</option>
            <option value="offline">Offline</option>
          </select>
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={showOnlyActive}
              onChange={(e) => setShowOnlyActive(e.target.checked)}
            />
            Csak aktív futárok
          </label>
          <button onClick={fetchCouriers} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="create-btn">
            ➕ Új futár
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && couriers.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="couriers-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Név</th>
                  <th>Telefon</th>
                  <th>Email</th>
                  <th>Státusz</th>
                  <th>Státusz váltás</th>
                  <th>Aktív</th>
                  <th>Létrehozva</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {couriers.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="empty-state">
                      Nincsenek futárok
                    </td>
                  </tr>
                ) : (
                  couriers.map((courier) => (
                    <tr key={courier.id}>
                      <td>
                        <span className="courier-id">#{courier.id}</span>
                      </td>
                      <td>
                        <strong>{courier.courier_name}</strong>
                      </td>
                      <td>{courier.phone}</td>
                      <td>{courier.email || '-'}</td>
                      <td>
                        <span
                          className={`status-badge ${getStatusBadgeClass(courier.status)}`}
                        >
                          {getStatusLabel(courier.status)}
                        </span>
                      </td>
                      <td>
                        <select
                          value={courier.status}
                          onChange={(e) =>
                            handleStatusChange(courier, e.target.value as CourierStatus)
                          }
                          className="status-select"
                          disabled={!courier.is_active}
                        >
                          <option value="available">Elérhető</option>
                          <option value="on_delivery">Úton</option>
                          <option value="break">Szünet</option>
                          <option value="offline">Offline</option>
                        </select>
                      </td>
                      <td>
                        <span
                          className={`active-badge ${
                            courier.is_active ? 'active' : 'inactive'
                          }`}
                        >
                          {courier.is_active ? '✅ Aktív' : '❌ Inaktív'}
                        </span>
                      </td>
                      <td>
                        <span className="date-text">{formatDate(courier.created_at)}</span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(courier)}
                            className="edit-btn"
                            title="Szerkesztés"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDelete(courier)}
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
              Összesen: {total} futár | Oldal: {page}
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
                disabled={couriers.length < pageSize}
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
        <CourierEditor courier={editingCourier} onClose={handleEditorClose} />
      )}
    </div>
  );
};
