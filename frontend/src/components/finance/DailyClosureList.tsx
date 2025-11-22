/**
 * DailyClosureList - Napi pénztárzárások listázása
 *
 * Funkciók:
 *   - Napi zárások táblázatos megjelenítése
 *   - Szűrés státusz és dátum szerint
 *   - Új zárás létrehozása (modal nyitás)
 *   - Zárás lezárása (modal nyitás)
 *   - Részletek megtekintése
 */

import { useState, useEffect } from 'react';
import { getDailyClosures } from '@/services/financeService';
import { DailyClosureEditor } from './DailyClosureEditor';
import type { DailyClosure } from '@/types/finance';
<<<<<<< HEAD
import { useAuthStore } from '@/stores/authStore';
import { notify } from '@/utils/notifications';
import './Finance.css';

export const DailyClosureList = () => {
  const { isAuthenticated } = useAuthStore();

=======
import { useToast } from '@/components/common/Toast';
import './Finance.css';

export const DailyClosureList = () => {
  const { showToast } = useToast();
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
  const [closures, setClosures] = useState<DailyClosure[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');

  // Editor modal state
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingClosure, setEditingClosure] = useState<DailyClosure | null>(null);

  // Zárások betöltése
  const fetchClosures = async () => {
    try {
      setIsLoading(true);
      const data = await getDailyClosures({
        status: statusFilter || undefined,
        limit: 50,
      });
      setClosures(data);
    } catch (error) {
      console.error('Hiba a zárások betöltésekor:', error);
<<<<<<< HEAD
      notify.error('Nem sikerült betölteni a zárásokat!');
=======
      showToast('Nem sikerült betölteni a zárásokat!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchClosures();
    }
  }, [isAuthenticated, statusFilter]);

  // Új zárás létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingClosure(null);
    setIsEditorOpen(true);
  };

  // Zárás szerkesztése/lezárása (modal nyitás)
  const handleEdit = (closure: DailyClosure) => {
    setEditingClosure(closure);
    setIsEditorOpen(true);
  };

  // Editor bezárása és lista frissítése
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingClosure(null);
    if (shouldRefresh) {
      fetchClosures();
    }
  };

  // Ár formázás
  const formatPrice = (price?: number): string => {
    if (price === undefined || price === null) return '-';
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  // Dátum formázás
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleString('hu-HU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Státusz badge
  const getStatusBadge = (status: string): JSX.Element => {
    const statusMap: Record<string, { label: string; className: string }> = {
      OPEN: { label: 'Nyitott', className: 'status-open' },
      IN_PROGRESS: { label: 'Folyamatban', className: 'status-in-progress' },
      CLOSED: { label: 'Lezárt', className: 'status-closed' },
      RECONCILED: { label: 'Egyeztetve', className: 'status-reconciled' },
    };

    const { label, className } = statusMap[status] || { label: status, className: '' };

    return <span className={`status-badge ${className}`}>{label}</span>;
  };

  // Eltérés badge (színes, ha van eltérés)
  const getDifferenceBadge = (difference?: number): JSX.Element => {
    if (difference === undefined || difference === null) return <>-</>;

    const className =
      difference === 0 ? 'difference-zero' : difference > 0 ? 'difference-positive' : 'difference-negative';

    return <span className={`difference-badge ${className}`}>{formatPrice(difference)}</span>;
  };

  return (
    <div className="daily-closure-list">
      {/* Fejléc */}
      <header className="list-header">
        <h2>📊 Napi Zárások</h2>
        <div className="header-controls">
          <label htmlFor="statusFilter">Státusz szűrő:</label>
          <select
            id="statusFilter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="status-filter"
          >
            <option value="">Összes</option>
            <option value="OPEN">Nyitott</option>
            <option value="IN_PROGRESS">Folyamatban</option>
            <option value="CLOSED">Lezárt</option>
            <option value="RECONCILED">Egyeztetve</option>
          </select>
          <button onClick={fetchClosures} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="create-btn">
            ➕ Új Zárás
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && closures.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="closures-table">
              <thead>
                <tr>
                  <th>Azonosító</th>
                  <th>Zárás dátuma</th>
                  <th>Státusz</th>
                  <th>Nyitó egyenleg</th>
                  <th>Várható záró</th>
                  <th>Tényleges záró</th>
                  <th>Eltérés</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {closures.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="empty-state">
                      Nincsenek zárások
                    </td>
                  </tr>
                ) : (
                  closures.map((closure) => (
                    <tr key={closure.id}>
                      <td>#{closure.id}</td>
                      <td>{formatDate(closure.closure_date)}</td>
                      <td>{getStatusBadge(closure.status)}</td>
                      <td>{formatPrice(closure.opening_balance)}</td>
                      <td>{formatPrice(closure.expected_closing_balance)}</td>
                      <td>{formatPrice(closure.actual_closing_balance)}</td>
                      <td>{getDifferenceBadge(closure.difference)}</td>
                      <td>
                        <button onClick={() => handleEdit(closure)} className="action-btn edit-btn" title="Szerkesztés">
                          ✏️
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Editor Modal */}
      {isEditorOpen && (
        <DailyClosureEditor closure={editingClosure} onClose={handleEditorClose} />
      )}
    </div>
  );
};
