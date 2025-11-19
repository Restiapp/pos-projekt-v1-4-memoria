/**
 * CouponEditor - Kupon létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új kupon létrehozása (POST /api/coupons)
 *   - Meglévő kupon szerkesztése (PUT /api/coupons/{id})
 *   - Validáció (kód, kedvezmény kötelező)
 *   - Modal overlay (háttérre kattintva bezárás)
 */

import { useState } from 'react';
import { createCoupon, updateCoupon } from '@/services/crmService';
import type { Coupon, CouponCreate, CouponUpdate } from '@/types/coupon';
import { DiscountTypeEnum } from '@/types/coupon';
import { notify } from '@/utils/notifications';
import './CouponEditor.css';

interface CouponEditorProps {
  coupon: Coupon | null; // null = új kupon, Coupon = szerkesztés
  onClose: (shouldRefresh: boolean) => void;
}

export const CouponEditor = ({ coupon, onClose }: CouponEditorProps) => {
  const isEditing = !!coupon; // true = szerkesztés, false = új létrehozás

  // Form állapot
  const [formData, setFormData] = useState({
    code: coupon?.code || '',
    description: coupon?.description || '',
    discount_type: coupon?.discount_type || DiscountTypeEnum.PERCENTAGE,
    discount_value: coupon?.discount_value || 0,
    min_purchase_amount: coupon?.min_purchase_amount || 0,
    max_uses: coupon?.max_uses || 0,
    valid_from: coupon?.valid_from
      ? coupon.valid_from.split('T')[0]
      : new Date().toISOString().split('T')[0],
    valid_until: coupon?.valid_until ? coupon.valid_until.split('T')[0] : '',
    is_active: coupon?.is_active ?? true,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    // Checkbox kezelés
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    // Szám mező kezelés
    if (
      name === 'discount_value' ||
      name === 'min_purchase_amount' ||
      name === 'max_uses'
    ) {
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
    if (!formData.code.trim()) {
      notify.warning('A kuponkód kötelező!');
      return;
    }

    if (formData.discount_value <= 0) {
      notify.warning('A kedvezmény értéke nagyobb kell legyen nullánál!');
      return;
    }

    if (
      formData.discount_type === DiscountTypeEnum.PERCENTAGE &&
      formData.discount_value > 100
    ) {
      notify.warning('A százalékos kedvezmény nem lehet nagyobb 100%-nál!');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing && coupon) {
        // Frissítés
        const updateData: CouponUpdate = {
          description: formData.description || undefined,
          discount_type: formData.discount_type,
          discount_value: formData.discount_value,
          min_purchase_amount: formData.min_purchase_amount || undefined,
          max_uses: formData.max_uses || undefined,
          valid_from: formData.valid_from,
          valid_until: formData.valid_until || undefined,
          is_active: formData.is_active,
        };
        await updateCoupon(coupon.id, updateData);
        notify.success('Kupon sikeresen frissítve!');
      } else {
        // Létrehozás
        const createData: CouponCreate = {
          code: formData.code,
          description: formData.description || undefined,
          discount_type: formData.discount_type,
          discount_value: formData.discount_value,
          min_purchase_amount: formData.min_purchase_amount || undefined,
          max_uses: formData.max_uses || undefined,
          valid_from: formData.valid_from,
          valid_until: formData.valid_until || undefined,
          is_active: formData.is_active,
        };
        await createCoupon(createData);
        notify.success('Kupon sikeresen létrehozva!');
      }

      onClose(true); // Bezárás + lista frissítése
    } catch (error: any) {
      console.error('Hiba a kupon mentésekor:', error);
      const errorMessage =
        error.response?.data?.detail || 'Nem sikerült menteni a kupont!';
      notify.error(errorMessage);
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
          <h2>{isEditing ? '✏️ Kupon szerkesztése' : '➕ Új kupon'}</h2>
          <button onClick={() => onClose(false)} className="close-btn">
            ✕
          </button>
        </header>

        <form onSubmit={handleSubmit} className="coupon-form">
          {/* Kuponkód */}
          <div className="form-group">
            <label htmlFor="code">
              Kuponkód <span className="required">*</span>
            </label>
            <input
              id="code"
              name="code"
              type="text"
              value={formData.code}
              onChange={handleChange}
              placeholder="pl. WELCOME10, SUMMER2024"
              required
              maxLength={50}
              disabled={isEditing} // Szerkesztésnél nem lehet változtatni
              className={isEditing ? 'readonly-input' : ''}
            />
          </div>

          {/* Leírás */}
          <div className="form-group">
            <label htmlFor="description">Leírás</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Kupon részletes leírása..."
              rows={2}
              maxLength={500}
            />
          </div>

          {/* Kedvezmény típusa */}
          <div className="form-group">
            <label htmlFor="discount_type">
              Kedvezmény típusa <span className="required">*</span>
            </label>
            <select
              id="discount_type"
              name="discount_type"
              value={formData.discount_type}
              onChange={handleChange}
              required
            >
              <option value={DiscountTypeEnum.PERCENTAGE}>Százalékos (%)</option>
              <option value={DiscountTypeEnum.FIXED_AMOUNT}>Fix összeg (HUF)</option>
            </select>
          </div>

          {/* Kedvezmény értéke */}
          <div className="form-group">
            <label htmlFor="discount_value">
              Kedvezmény értéke{' '}
              {formData.discount_type === DiscountTypeEnum.PERCENTAGE ? '(%)' : '(HUF)'}{' '}
              <span className="required">*</span>
            </label>
            <input
              id="discount_value"
              name="discount_value"
              type="number"
              value={formData.discount_value}
              onChange={handleChange}
              min={0}
              max={formData.discount_type === DiscountTypeEnum.PERCENTAGE ? 100 : undefined}
              step={formData.discount_type === DiscountTypeEnum.PERCENTAGE ? 1 : 10}
              required
            />
          </div>

          {/* Minimum vásárlási érték */}
          <div className="form-group">
            <label htmlFor="min_purchase_amount">Minimum vásárlási érték (HUF)</label>
            <input
              id="min_purchase_amount"
              name="min_purchase_amount"
              type="number"
              value={formData.min_purchase_amount}
              onChange={handleChange}
              min={0}
              step={100}
              placeholder="0 = nincs minimum"
            />
          </div>

          {/* Használati limit */}
          <div className="form-group">
            <label htmlFor="max_uses">Használati limit (max. felhasználások)</label>
            <input
              id="max_uses"
              name="max_uses"
              type="number"
              value={formData.max_uses}
              onChange={handleChange}
              min={0}
              step={1}
              placeholder="0 = korlátlan"
            />
          </div>

          {/* Érvényesség kezdete */}
          <div className="form-group">
            <label htmlFor="valid_from">
              Érvényesség kezdete <span className="required">*</span>
            </label>
            <input
              id="valid_from"
              name="valid_from"
              type="date"
              value={formData.valid_from}
              onChange={handleChange}
              required
            />
          </div>

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

          {/* Használati statisztika (csak szerkesztésnél) */}
          {isEditing && coupon && (
            <div className="stats-section">
              <h3>Statisztikák</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Használatok száma:</span>
                  <span className="stat-value">{coupon.usage_count}</span>
                </div>
                {coupon.max_uses && (
                  <div className="stat-item">
                    <span className="stat-label">Felhasználható még:</span>
                    <span className="stat-value">
                      {Math.max(0, coupon.max_uses - coupon.usage_count)}
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
