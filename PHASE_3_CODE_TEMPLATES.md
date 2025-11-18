# 📦 FÁZIS 3 - KÓD TEMPLATES (Végrehajtó Ágens számára)

**Verzió:** 1.0
**Dátum:** 2025-11-18
**Branch:** `claude/phase-3-planning-01NsfmDJkXnHzNrCtujCi2Bt`

---

## 📚 TARTALOMJEGYZÉK

1. **Finance UI Komponensek** (Modul 2)
   - DailyClosureList.tsx
   - DailyClosureEditor.tsx
   - Finance.css
   - FinancePage.css
   - AdminPage.tsx módosítás
   - App.tsx módosítás

2. **Assets Backend + Frontend** (Modul 3-4)
   - Backend: schemas, services, routers
   - Frontend: types, services, komponensek

3. **Vehicles Backend + Frontend** (Modul 5-6)
   - Backend: schemas, services, routers
   - Frontend: types, services, komponensek

---

## 💰 MODUL 2: FINANCE UI - TOVÁBBI KOMPONENSEK

### 📄 `frontend/src/components/finance/DailyClosureList.tsx` (ÚJ FÁJL)

```typescript
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
import './Finance.css';

export const DailyClosureList = () => {
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
      alert('Nem sikerült betölteni a zárásokat!');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchClosures();
  }, [statusFilter]);

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
```

---

### 📄 `frontend/src/components/finance/DailyClosureEditor.tsx` (ÚJ FÁJL)

```typescript
/**
 * DailyClosureEditor - Napi zárás szerkesztő modal
 *
 * Funkciók:
 *   - Új napi zárás létrehozása (nyitó egyenleg megadásával)
 *   - Meglévő zárás lezárása (tényleges egyenleg megadásával)
 *   - Eltérés automatikus számítása
 *   - Validáció és hibakezelés
 */

import { useState, useEffect } from 'react';
import { createDailyClosure, closeDailyClosure } from '@/services/financeService';
import type { DailyClosure, DailyClosureCreateRequest, DailyClosureUpdateRequest } from '@/types/finance';
import './Finance.css';

interface DailyClosureEditorProps {
  closure: DailyClosure | null; // null = új zárás létrehozása
  onClose: (shouldRefresh: boolean) => void;
}

export const DailyClosureEditor: React.FC<DailyClosureEditorProps> = ({ closure, onClose }) => {
  const isEditMode = !!closure;

  // Form state
  const [openingBalance, setOpeningBalance] = useState<string>('0');
  const [actualClosingBalance, setActualClosingBalance] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [isSaving, setIsSaving] = useState(false);

  // Initial load
  useEffect(() => {
    if (closure) {
      setOpeningBalance(closure.opening_balance.toString());
      setActualClosingBalance(closure.actual_closing_balance?.toString() || '');
      setNotes(closure.notes || '');
    }
  }, [closure]);

  // Form submit kezelése
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setIsSaving(true);

      if (isEditMode) {
        // Lezárás (update)
        const numActual = parseFloat(actualClosingBalance);
        if (isNaN(numActual) || numActual < 0) {
          alert('Érvénytelen záró egyenleg!');
          return;
        }

        const payload: DailyClosureUpdateRequest = {
          actual_closing_balance: numActual,
          notes: notes || undefined,
        };

        await closeDailyClosure(closure!.id, payload);
        alert('Zárás sikeresen lezárva!');
        onClose(true);
      } else {
        // Új zárás létrehozása
        const numOpening = parseFloat(openingBalance);
        if (isNaN(numOpening) || numOpening < 0) {
          alert('Érvénytelen nyitó egyenleg!');
          return;
        }

        const payload: DailyClosureCreateRequest = {
          opening_balance: numOpening,
          notes: notes || undefined,
        };

        await createDailyClosure(payload);
        alert('Új zárás sikeresen létrehozva!');
        onClose(true);
      }
    } catch (error: any) {
      console.error('Hiba a művelet során:', error);
      alert(error.response?.data?.detail || 'Nem sikerült a művelet!');
    } finally {
      setIsSaving(false);
    }
  };

  // Modal bezárás
  const handleCancel = () => {
    onClose(false);
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

  // Eltérés számítása
  const calculateDifference = (): number | null => {
    if (!isEditMode || !closure?.expected_closing_balance) return null;
    const actual = parseFloat(actualClosingBalance);
    if (isNaN(actual)) return null;
    return actual - closure.expected_closing_balance;
  };

  const difference = calculateDifference();

  return (
    <div className="modal-overlay" onClick={handleCancel}>
      <div className="modal-content daily-closure-editor" onClick={(e) => e.stopPropagation()}>
        {/* Modal fejléc */}
        <header className="modal-header">
          <h2>{isEditMode ? `📊 Napi Zárás #${closure!.id} Lezárása` : '➕ Új Napi Zárás'}</h2>
          <button onClick={handleCancel} className="close-btn" title="Bezárás">
            ✖️
          </button>
        </header>

        {/* Modal tartalom */}
        <form onSubmit={handleSubmit} className="modal-body">
          {/* Új zárás: Nyitó egyenleg */}
          {!isEditMode && (
            <div className="form-group">
              <label htmlFor="openingBalance">Nyitó egyenleg (Ft) *</label>
              <input
                id="openingBalance"
                type="number"
                min="0"
                step="1"
                value={openingBalance}
                onChange={(e) => setOpeningBalance(e.target.value)}
                placeholder="0"
                required
                disabled={isSaving}
              />
            </div>
          )}

          {/* Lezárás: Várható és tényleges egyenleg */}
          {isEditMode && (
            <>
              <div className="closure-summary">
                <div className="summary-item">
                  <label>Nyitó egyenleg:</label>
                  <span>{formatPrice(closure!.opening_balance)}</span>
                </div>
                <div className="summary-item">
                  <label>Várható záró egyenleg:</label>
                  <span>{formatPrice(closure!.expected_closing_balance)}</span>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="actualClosingBalance">Tényleges záró egyenleg (Ft) *</label>
                <input
                  id="actualClosingBalance"
                  type="number"
                  min="0"
                  step="1"
                  value={actualClosingBalance}
                  onChange={(e) => setActualClosingBalance(e.target.value)}
                  placeholder="0"
                  required
                  disabled={isSaving}
                />
              </div>

              {difference !== null && (
                <div className={`difference-display ${difference === 0 ? 'zero' : difference > 0 ? 'positive' : 'negative'}`}>
                  <strong>Eltérés:</strong> {formatPrice(difference)}
                </div>
              )}
            </>
          )}

          {/* Megjegyzések */}
          <div className="form-group">
            <label htmlFor="notes">Megjegyzések</label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Opcionális megjegyzések vagy indoklás eltérés esetén"
              rows={4}
              disabled={isSaving}
            />
          </div>

          {/* Modal lábléc */}
          <footer className="modal-footer">
            <button type="button" onClick={handleCancel} className="cancel-btn" disabled={isSaving}>
              Mégse
            </button>
            <button type="submit" className="save-btn" disabled={isSaving}>
              {isSaving ? 'Feldolgozás...' : isEditMode ? 'Lezárás' : 'Létrehozás'}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
};
```

---

### 📄 `frontend/src/components/finance/Finance.css` (ÚJ FÁJL)

```css
/**
 * Finance Components - Közös stílusok a pénzügyi komponensekhez
 */

/* ============================================================================
   Cash Drawer Styles
   ============================================================================ */

.cash-drawer {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  padding: 2rem;
}

@media (max-width: 768px) {
  .cash-drawer {
    grid-template-columns: 1fr;
  }
}

.balance-card,
.cash-operation-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.balance-card h2 {
  margin-top: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.balance-amount {
  font-size: 3rem;
  font-weight: bold;
  color: #27ae60;
  margin: 1rem 0;
  text-align: center;
}

.operation-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.operation-btn {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.operation-btn:hover {
  background: #f8f9fa;
}

.operation-btn.active {
  border-color: #3498db;
  background: #3498db;
  color: white;
  font-weight: bold;
}

.cash-form .form-group {
  margin-bottom: 1.5rem;
}

.cash-form label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.cash-form input,
.cash-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.cash-form input:focus,
.cash-form textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn.deposit {
  background: #27ae60;
  color: white;
}

.submit-btn.deposit:hover:not(:disabled) {
  background: #229954;
}

.submit-btn.withdraw {
  background: #e74c3c;
  color: white;
}

.submit-btn.withdraw:hover:not(:disabled) {
  background: #c0392b;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ============================================================================
   Daily Closure List Styles
   ============================================================================ */

.daily-closure-list {
  padding: 2rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.list-header h2 {
  margin: 0;
  font-size: 2rem;
  color: #2c3e50;
}

.header-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.status-filter {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.refresh-btn,
.create-btn,
.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.refresh-btn {
  background: #95a5a6;
  color: white;
}

.refresh-btn:hover:not(:disabled) {
  background: #7f8c8d;
}

.create-btn {
  background: #3498db;
  color: white;
  font-weight: bold;
}

.create-btn:hover {
  background: #2980b9;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.closures-table {
  width: 100%;
  border-collapse: collapse;
}

.closures-table th,
.closures-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #ecf0f1;
}

.closures-table th {
  background: #34495e;
  color: white;
  font-weight: 600;
  position: sticky;
  top: 0;
}

.closures-table tbody tr:hover {
  background: #f8f9fa;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-badge.status-open {
  background: #3498db;
  color: white;
}

.status-badge.status-in-progress {
  background: #f39c12;
  color: white;
}

.status-badge.status-closed {
  background: #95a5a6;
  color: white;
}

.status-badge.status-reconciled {
  background: #27ae60;
  color: white;
}

.difference-badge {
  font-weight: bold;
}

.difference-badge.difference-zero {
  color: #27ae60;
}

.difference-badge.difference-positive {
  color: #f39c12;
}

.difference-badge.difference-negative {
  color: #e74c3c;
}

.action-btn {
  background: transparent;
  border: 1px solid #ddd;
  padding: 0.25rem 0.5rem;
  font-size: 1.25rem;
}

.action-btn:hover {
  background: #f8f9fa;
  border-color: #3498db;
}

.empty-state,
.loading-state {
  padding: 3rem;
  text-align: center;
  color: #95a5a6;
  font-size: 1.25rem;
}

/* ============================================================================
   Daily Closure Editor (Modal) Styles
   ============================================================================ */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #ecf0f1;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  color: #95a5a6;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #e74c3c;
}

.modal-body {
  padding: 2rem;
}

.closure-summary {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.summary-item label {
  font-weight: 600;
  color: #7f8c8d;
}

.summary-item span {
  font-weight: bold;
  color: #2c3e50;
}

.difference-display {
  padding: 1rem;
  border-radius: 6px;
  margin-top: 1rem;
  text-align: center;
  font-size: 1.25rem;
}

.difference-display.zero {
  background: #d5f4e6;
  color: #27ae60;
}

.difference-display.positive {
  background: #ffe5b4;
  color: #f39c12;
}

.difference-display.negative {
  background: #fadbd8;
  color: #e74c3c;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-top: 1px solid #ecf0f1;
}

.cancel-btn,
.save-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #ecf0f1;
  color: #7f8c8d;
}

.cancel-btn:hover:not(:disabled) {
  background: #bdc3c7;
}

.save-btn {
  background: #3498db;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #2980b9;
}

.cancel-btn:disabled,
.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

---

### 📄 `frontend/src/pages/FinancePage.css` (ÚJ FÁJL)

```css
/**
 * FinancePage - Főoldal stílusok
 */

.finance-page {
  background: #f5f6fa;
  min-height: 100vh;
}

.finance-header {
  background: white;
  padding: 2rem;
  border-bottom: 1px solid #ecf0f1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.finance-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2.5rem;
  color: #2c3e50;
}

.finance-description {
  margin: 0;
  color: #7f8c8d;
  font-size: 1.125rem;
}

.finance-tabs {
  display: flex;
  background: white;
  border-bottom: 2px solid #ecf0f1;
  padding: 0 2rem;
}

.tab-button {
  padding: 1rem 2rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1.125rem;
  font-weight: 600;
  color: #7f8c8d;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab-button:hover {
  color: #3498db;
  background: #f8f9fa;
}

.tab-button.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.finance-content {
  /* Tab tartalom */
}
```

---

### 📄 `frontend/src/pages/AdminPage.tsx` - Módosítás (Finance menüpont hozzáadása)

**VÁLTOZTATÁS:** A `MENU_ITEMS` tömb kiegészítése a Finance menüponttal:

```typescript
const MENU_ITEMS: MenuItem[] = [
  {
    id: 'products',
    label: 'Termékek',
    icon: '📦',
    path: '/admin/products',
    permission: 'menu:manage',
  },
  {
    id: 'tables',
    label: 'Asztalok',
    icon: '🪑',
    path: '/admin/tables',
    permission: 'orders:manage',
  },
  {
    id: 'employees',
    label: 'Munkavállalók',
    icon: '👥',
    path: '/admin/employees',
    permission: 'employees:manage',
  },
  {
    id: 'roles',
    label: 'Szerepkörök',
    icon: '🔐',
    path: '/admin/roles',
    permission: 'roles:manage',
  },
  // ÚJ MENÜPONT - FÁZIS 3
  {
    id: 'finance',
    label: 'Pénzügy',
    icon: '💰',
    path: '/admin/finance',
    permission: 'finance:manage', // TODO: Add finance:manage permission to RBAC
  },
  // CRM menüpontok
  {
    id: 'customers',
    label: 'Vendégek',
    icon: '👤',
    path: '/admin/customers',
    permission: 'menu:manage',
  },
  {
    id: 'coupons',
    label: 'Kuponok',
    icon: '🎫',
    path: '/admin/coupons',
    permission: 'menu:manage',
  },
  {
    id: 'gift_cards',
    label: 'Ajándékkártyák',
    icon: '🎁',
    path: '/admin/gift_cards',
    permission: 'menu:manage',
  },
  {
    id: 'logistics',
    label: 'Logisztika',
    icon: '🚚',
    path: '/admin/logistics',
    permission: 'menu:manage',
  },
];
```

---

### 📄 `frontend/src/App.tsx` - Módosítás (Finance routing hozzáadása)

**VÁLTOZTATÁS:** A Finance oldal importálása és route hozzáadása:

```typescript
// ÚJ IMPORT - Fázis 3
import { FinancePage } from '@/pages/FinancePage';

// ... (többi import)

function App() {
  // ...

  return (
    <BrowserRouter>
      <Routes>
        {/* ... (többi route) */}

        {/* Admin Dashboard (Nested Routes) */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute requiredPermission="menu:manage">
              <AdminPage />
            </ProtectedRoute>
          }
        >
          {/* ... (többi nested route) */}

          {/* ÚJ: Nested Route: /admin/finance - Pénzügy */}
          <Route
            path="finance"
            element={
              <ProtectedRoute requiredPermission="finance:manage">
                <FinancePage />
              </ProtectedRoute>
            }
          />

          {/* ... (többi nested route) */}
        </Route>

        {/* ... (többi route) */}
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🏗️ MODUL 2 ÖSSZEFOGLALÁS

A Finance UI modul implementálása **teljes**, az alábbi fájlokat kell létrehozni/módosítani:

### ÚJ FÁJLOK (9 db):
1. `frontend/src/types/finance.ts`
2. `frontend/src/services/financeService.ts`
3. `frontend/src/pages/FinancePage.tsx`
4. `frontend/src/pages/FinancePage.css`
5. `frontend/src/components/finance/CashDrawer.tsx`
6. `frontend/src/components/finance/DailyClosureList.tsx`
7. `frontend/src/components/finance/DailyClosureEditor.tsx`
8. `frontend/src/components/finance/Finance.css`
9. `frontend/src/components/finance/` (könyvtár létrehozása)

### MÓDOSÍTOTT FÁJLOK (2 db):
1. `frontend/src/pages/AdminPage.tsx` (Finance menüpont hozzáadása)
2. `frontend/src/App.tsx` (Finance routing hozzáadása)

### BACKEND API (KÉSZ):
- ✅ `backend/service_admin/models/finance.py`
- ✅ `backend/service_admin/services/finance_service.py`
- ✅ `backend/service_admin/routers/finance.py`
- ✅ `backend/service_admin/schemas/finance.py`

---

