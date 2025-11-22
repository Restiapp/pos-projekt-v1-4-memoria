/**
 * CustomerEditor - Vendég létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új vendég létrehozása (POST /api/customers)
 *   - Meglévő vendég szerkesztése (PUT /api/customers/{id})
 *   - Validáció (név, email kötelező)
 *   - Modal overlay (háttérre kattintva bezárás)
 */

import { useState } from 'react';
import { createCustomer, updateCustomer } from '@/services/crmService';
import type { Customer, CustomerCreate, CustomerUpdate } from '@/types/customer';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './CustomerEditor.css';

interface CustomerEditorProps {
  customer: Customer | null; // null = új vendég, Customer = szerkesztés
  onClose: (shouldRefresh: boolean) => void;
}

export const CustomerEditor = ({ customer, onClose }: CustomerEditorProps) => {
  const isEditing = !!customer; // true = szerkesztés, false = új létrehozás
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();

  // Form állapot
  const [formData, setFormData] = useState({
    first_name: customer?.first_name || '',
    last_name: customer?.last_name || '',
    email: customer?.email || '',
    phone: customer?.phone || '',
    marketing_consent: customer?.marketing_consent ?? false,
    sms_consent: customer?.sms_consent ?? false,
    birth_date: customer?.birth_date ? customer.birth_date.split('T')[0] : '',
    notes: customer?.notes || '',
    is_active: customer?.is_active ?? true,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    // Checkbox kezelés
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    // String mezők
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Form submit (létrehozás / frissítés)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (!formData.first_name.trim()) {
      showToast('A keresztnév kötelező!', 'error');
      return;
    }

    if (!formData.last_name.trim()) {
      showToast('A vezetéknév kötelező!', 'error');
      return;
    }

    if (!formData.email.trim()) {
      showToast('Az email kötelező!', 'error');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing && customer) {
        // Frissítés
        const updateData: CustomerUpdate = {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          phone: formData.phone || undefined,
          marketing_consent: formData.marketing_consent,
          sms_consent: formData.sms_consent,
          birth_date: formData.birth_date || undefined,
          notes: formData.notes || undefined,
          is_active: formData.is_active,
        };
        await updateCustomer(customer.id, updateData);
        showToast('Vendég sikeresen frissítve!', 'success');
      } else {
        // Létrehozás
        const createData: CustomerCreate = {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          phone: formData.phone || undefined,
          marketing_consent: formData.marketing_consent,
          sms_consent: formData.sms_consent,
          birth_date: formData.birth_date || undefined,
          notes: formData.notes || undefined,
        };
        await createCustomer(createData);
        showToast('Vendég sikeresen létrehozva!', 'success');
      }

      onClose(true); // Bezárás + lista frissítése
    } catch (error: any) {
      console.error('Hiba a vendég mentésekor:', error);
      const errorMessage =
        error.response?.data?.detail || 'Nem sikerült menteni a vendéget!';
      showToast(errorMessage, 'error');
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

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <header className="modal-header">
          <h2>{isEditing ? '✏️ Vendég szerkesztése' : '➕ Új vendég'}</h2>
          <button onClick={() => onClose(false)} className="close-btn">
            ✕
          </button>
        </header>

        <form onSubmit={handleSubmit} className="customer-form">
          {/* Vendégszám (csak szerkesztésnél látszik, read-only) */}
          {isEditing && customer && (
            <div className="form-group">
              <label>Vendégszám</label>
              <input
                type="text"
                value={customer.customer_uid}
                disabled
                className="readonly-input"
              />
            </div>
          )}

          {/* Keresztnév */}
          <div className="form-group">
            <label htmlFor="first_name">
              Keresztnév <span className="required">*</span>
            </label>
            <input
              id="first_name"
              name="first_name"
              type="text"
              value={formData.first_name}
              onChange={handleChange}
              placeholder="pl. János"
              required
              maxLength={100}
            />
          </div>

          {/* Vezetéknév */}
          <div className="form-group">
            <label htmlFor="last_name">
              Vezetéknév <span className="required">*</span>
            </label>
            <input
              id="last_name"
              name="last_name"
              type="text"
              value={formData.last_name}
              onChange={handleChange}
              placeholder="pl. Kovács"
              required
              maxLength={100}
            />
          </div>

          {/* Email */}
          <div className="form-group">
            <label htmlFor="email">
              Email <span className="required">*</span>
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="pl. janos.kovacs@example.com"
              required
            />
          </div>

          {/* Telefon */}
          <div className="form-group">
            <label htmlFor="phone">Telefon</label>
            <input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              placeholder="pl. +36301234567"
              maxLength={20}
            />
          </div>

          {/* Születési dátum */}
          <div className="form-group">
            <label htmlFor="birth_date">Születési dátum</label>
            <input
              id="birth_date"
              name="birth_date"
              type="date"
              value={formData.birth_date}
              onChange={handleChange}
            />
          </div>

          {/* Marketing hozzájárulás */}
          <div className="form-group checkbox-group">
            <label>
              <input
                name="marketing_consent"
                type="checkbox"
                checked={formData.marketing_consent}
                onChange={handleChange}
              />
              Marketing email hozzájárulás
            </label>
          </div>

          {/* SMS hozzájárulás */}
          <div className="form-group checkbox-group">
            <label>
              <input
                name="sms_consent"
                type="checkbox"
                checked={formData.sms_consent}
                onChange={handleChange}
              />
              SMS marketing hozzájárulás
            </label>
          </div>

          {/* Jegyzetek */}
          <div className="form-group">
            <label htmlFor="notes">Jegyzetek</label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="További információk a vendégről..."
              rows={3}
            />
          </div>

          {/* Aktív (csak szerkesztésnél) */}
          {isEditing && (
            <div className="form-group checkbox-group">
              <label>
                <input
                  name="is_active"
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={handleChange}
                />
                Aktív vendég
              </label>
            </div>
          )}

          {/* Hűségpontok / Statisztikák (csak szerkesztésnél, read-only) */}
          {isEditing && customer && (
            <div className="stats-section">
              <h3>Statisztikák</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Hűségpontok:</span>
                  <span className="stat-value">{customer.loyalty_points} pt</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Össz. költés:</span>
                  <span className="stat-value">
                    {new Intl.NumberFormat('hu-HU', {
                      style: 'currency',
                      currency: 'HUF',
                      minimumFractionDigits: 0,
                    }).format(customer.total_spent)}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Rendelések:</span>
                  <span className="stat-value">{customer.total_orders} db</span>
                </div>
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
