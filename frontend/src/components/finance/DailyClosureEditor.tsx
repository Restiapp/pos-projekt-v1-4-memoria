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
import { notify } from '@/utils/notifications';
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
          notify.error('Érvénytelen záró egyenleg!');
          return;
        }

        const payload: DailyClosureUpdateRequest = {
          actual_closing_balance: numActual,
          notes: notes || undefined,
        };

        await closeDailyClosure(closure!.id, payload);
        notify.success('Zárás sikeresen lezárva!');
        onClose(true);
      } else {
        // Új zárás létrehozása
        const numOpening = parseFloat(openingBalance);
        if (isNaN(numOpening) || numOpening < 0) {
          notify.error('Érvénytelen nyitó egyenleg!');
          return;
        }

        const payload: DailyClosureCreateRequest = {
          opening_balance: numOpening,
          notes: notes || undefined,
        };

        await createDailyClosure(payload);
        notify.success('Új zárás sikeresen létrehozva!');
        onClose(true);
      }
    } catch (error: any) {
      console.error('Hiba a művelet során:', error);
      notify.error(error.response?.data?.detail || 'Nem sikerült a művelet!');
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
