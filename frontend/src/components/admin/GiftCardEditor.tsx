/**
 * GiftCardEditor - Ajándékkártya létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új ajándékkártya létrehozása (POST /api/gift_cards)
 *   - Meglévő ajándékkártya szerkesztése (PUT /api/gift_cards/{id})
 *   - Validáció (kártyakód, kezdeti egyenleg kötelező)
 *   - Modal overlay (háttérre kattintva bezárás)
 */

import { useState } from 'react';
import { createGiftCard, updateGiftCard } from '@/services/crmService';
import type { GiftCard, GiftCardCreate, GiftCardUpdate } from '@/types/giftCard';
<<<<<<< HEAD
import { notify } from '@/utils/notifications';
=======
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
import './GiftCardEditor.css';

interface GiftCardEditorProps {
  giftCard: GiftCard | null; // null = új kártya, GiftCard = szerkesztés
  onClose: (shouldRefresh: boolean) => void;
}

export const GiftCardEditor = ({ giftCard, onClose }: GiftCardEditorProps) => {
  const isEditing = !!giftCard; // true = szerkesztés, false = új létrehozás
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();

  // Form állapot
  const [formData, setFormData] = useState({
    card_code: giftCard?.card_code || '',
    pin_code: giftCard?.pin_code || '',
    initial_balance: giftCard?.initial_balance || 0,
    valid_until: giftCard?.valid_until ? giftCard.valid_until.split('T')[0] : '',
    is_active: giftCard?.is_active ?? true,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;

    // Checkbox kezelés
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    // Szám mező kezelés
    if (name === 'initial_balance') {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }));
      return;
    }

    // String mezők
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Form submit (létrehozás / frissítés)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (!formData.card_code.trim()) {
<<<<<<< HEAD
      notify.warning('A kártyakód kötelező!');
=======
      showToast('A kártyakód kötelező!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      return;
    }

    // PIN kód validáció
    if (formData.pin_code.trim()) {
      // Ha PIN kódot adtak meg, ellenőrizzük a formátumot
      const pinRegex = /^[0-9]{4,10}$/; // 4-10 számjegy
      if (!pinRegex.test(formData.pin_code)) {
<<<<<<< HEAD
        notify.warning('A PIN kód 4-10 számjegyből kell álljon!');
=======
        showToast('A PIN kód 4-10 számjegyből kell álljon!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
        return;
      }
    }

    if (formData.initial_balance <= 0 && !isEditing) {
<<<<<<< HEAD
      notify.warning('A kezdeti egyenleg nagyobb kell legyen nullánál!');
=======
      showToast('A kezdeti egyenleg nagyobb kell legyen nullánál!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing && giftCard) {
        // Frissítés
        const updateData: GiftCardUpdate = {
          pin_code: formData.pin_code || undefined,
          valid_until: formData.valid_until || undefined,
          is_active: formData.is_active,
        };
        await updateGiftCard(giftCard.id, updateData);
<<<<<<< HEAD
        notify.success('Ajándékkártya sikeresen frissítve!');
=======
        showToast('Ajándékkártya sikeresen frissítve!', 'success');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      } else {
        // Létrehozás
        const createData: GiftCardCreate = {
          card_code: formData.card_code,
          pin_code: formData.pin_code || undefined,
          initial_balance: formData.initial_balance,
          valid_until: formData.valid_until || undefined,
          is_active: formData.is_active,
        };
        await createGiftCard(createData);
<<<<<<< HEAD
        notify.success('Ajándékkártya sikeresen létrehozva!');
=======
        showToast('Ajándékkártya sikeresen létrehozva!', 'success');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      }

      onClose(true); // Bezárás + lista frissítése
    } catch (error: any) {
      console.error('Hiba az ajándékkártya mentésekor:', error);
      const errorMessage =
        error.response?.data?.detail || 'Nem sikerült menteni az ajándékkártyát!';
<<<<<<< HEAD
      notify.error(errorMessage);
=======
      showToast(errorMessage, 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
    } finally {
      setIsSubmitting(false);
    }
  };

  // Modal overlay kattintás (háttérre kattintva bezárás)
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose(false);
    }
  };

  // Ár formázása
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <header className="modal-header">
          <h2>
            {isEditing ? '✏️ Ajándékkártya szerkesztése' : '➕ Új ajándékkártya'}
          </h2>
          <button onClick={() => onClose(false)} className="close-btn">
            ✕
          </button>
        </header>

        <form onSubmit={handleSubmit} className="gift-card-form">
          {/* Kártyakód */}
          <div className="form-group">
            <label htmlFor="card_code">
              Kártyakód <span className="required">*</span>
            </label>
            <input
              id="card_code"
              name="card_code"
              type="text"
              value={formData.card_code}
              onChange={handleChange}
              placeholder="pl. GIFT-2024-ABC123"
              required
              maxLength={50}
              disabled={isEditing} // Szerkesztésnél nem lehet változtatni
              className={isEditing ? 'readonly-input' : ''}
            />
          </div>

          {/* PIN kód */}
          <div className="form-group">
            <label htmlFor="pin_code">PIN kód (opcionális)</label>
            <input
              id="pin_code"
              name="pin_code"
              type="text"
              value={formData.pin_code}
              onChange={handleChange}
              placeholder="pl. 1234"
              maxLength={10}
            />
            <small>Opcionális biztonsági PIN kód a kártya használatához</small>
          </div>

          {/* Kezdeti egyenleg (csak létrehozásnál) */}
          {!isEditing && (
            <div className="form-group">
              <label htmlFor="initial_balance">
                Kezdeti egyenleg (HUF) <span className="required">*</span>
              </label>
              <input
                id="initial_balance"
                name="initial_balance"
                type="number"
                value={formData.initial_balance}
                onChange={handleChange}
                min={0}
                step={100}
                required
              />
            </div>
          )}

          {/* Érvényesség vége */}
          <div className="form-group">
            <label htmlFor="valid_until">Érvényesség vége</label>
            <input
              id="valid_until"
              name="valid_until"
              type="date"
              value={formData.valid_until}
              onChange={handleChange}
            />
            <small>Üresen hagyva: nincs lejárati dátum</small>
          </div>

          {/* Aktív */}
          <div className="form-group checkbox-group">
            <label>
              <input
                name="is_active"
                type="checkbox"
                checked={formData.is_active}
                onChange={handleChange}
              />
              Aktív (használható)
            </label>
          </div>

          {/* Statisztikák (csak szerkesztésnél) */}
          {isEditing && giftCard && (
            <div className="stats-section">
              <h3>Kártya állapota</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Kezdeti egyenleg:</span>
                  <span className="stat-value">
                    {formatPrice(giftCard.initial_balance)}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Jelenlegi egyenleg:</span>
                  <span className="stat-value">
                    {formatPrice(giftCard.current_balance)}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Felhasználás:</span>
                  <span className="stat-value">
                    {giftCard.usage_percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Érvényes:</span>
                  <span className={`stat-value ${giftCard.is_valid ? 'valid' : 'invalid'}`}>
                    {giftCard.is_valid ? '✅ Igen' : '❌ Nem'}
                  </span>
                </div>
                {giftCard.is_assigned && (
                  <div className="stat-item">
                    <span className="stat-label">Hozzárendelve:</span>
                    <span className="stat-value">
                      Vendég #{giftCard.customer_id}
                    </span>
                  </div>
                )}
                {giftCard.last_used_at && (
                  <div className="stat-item">
                    <span className="stat-label">Utoljára használva:</span>
                    <span className="stat-value">
                      {new Date(giftCard.last_used_at).toLocaleDateString('hu-HU')}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Gombok */}
          <footer className="modal-footer">
            <button
              type="button"
              onClick={() => onClose(false)}
              className="cancel-btn"
              disabled={isSubmitting}
            >
              Mégse
            </button>
            <button type="submit" className="save-btn" disabled={isSubmitting}>
              {isSubmitting
                ? 'Mentés...'
                : isEditing
                ? '💾 Mentés'
                : '➕ Létrehozás'}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
};
