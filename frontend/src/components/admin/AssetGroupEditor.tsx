/**
 * AssetGroupEditor - Eszközcsoport létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új eszközcsoport létrehozása (POST /api/assets/groups)
 *   - Meglévő eszközcsoport szerkesztése (PATCH /api/assets/groups/{id})
 *   - Validáció (név kötelező)
 *   - Modal overlay (háttérre kattintva bezárás)
 */

import { useState } from 'react';
import { createAssetGroup, updateAssetGroup } from '@/services/assetService';
import type { AssetGroup, AssetGroupCreate, AssetGroupUpdate } from '@/types/asset';
import './AssetGroupEditor.css';
import { notifications } from '@mantine/notifications';

interface AssetGroupEditorProps {
  assetGroup: AssetGroup | null; // null = új, AssetGroup = szerkesztés
  onClose: (shouldRefresh: boolean) => void;
}

export const AssetGroupEditor = ({
  assetGroup,
  onClose,
}: AssetGroupEditorProps) => {
  const isEditing = !!assetGroup;
    
  // Form állapot
  const [formData, setFormData] = useState({
    name: assetGroup?.name || '',
    description: assetGroup?.description || '',
    depreciation_rate: assetGroup?.depreciation_rate?.toString() || '',
    expected_lifetime_years: assetGroup?.expected_lifetime_years?.toString() || '',
    is_active: assetGroup?.is_active ?? true,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (!formData.name.trim()) {
      notifications.show({
        title: 'Figyelmeztetés',
        message: 'Az eszközcsoport neve kötelező!',
        color: 'yellow',
      });
      return;
    }

    setIsSubmitting(true);

    try {
      // API hívás
      if (isEditing) {
        const updateData: AssetGroupUpdate = {
          name: formData.name.trim(),
          description: formData.description.trim() || null,
          depreciation_rate: formData.depreciation_rate
            ? parseFloat(formData.depreciation_rate)
            : null,
          expected_lifetime_years: formData.expected_lifetime_years
            ? parseInt(formData.expected_lifetime_years, 10)
            : null,
          is_active: formData.is_active,
        };

        await updateAssetGroup(assetGroup!.id, updateData);
        notifications.show({
        title: 'Siker',
        message: 'Eszközcsoport sikeresen frissítve!',
        color: 'green',
      });
      } else {
        const createData: AssetGroupCreate = {
          name: formData.name.trim(),
          description: formData.description.trim() || null,
          depreciation_rate: formData.depreciation_rate
            ? parseFloat(formData.depreciation_rate)
            : null,
          expected_lifetime_years: formData.expected_lifetime_years
            ? parseInt(formData.expected_lifetime_years, 10)
            : null,
          is_active: formData.is_active,
        };

        await createAssetGroup(createData);
        notifications.show({
        title: 'Siker',
        message: 'Eszközcsoport sikeresen létrehozva!',
        color: 'green',
      });
      }

      onClose(true); // Bezárás + lista frissítése
    } catch (error: any) {
      console.error('Hiba az eszközcsoport mentésekor:', error);
      const errorMsg = error?.response?.data?.detail || 'Ismeretlen hiba történt';
      notify.error(`Hiba: ${errorMsg}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={() => onClose(false)}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Modal fejléc */}
        <div className="modal-header">
          <h2>
            {isEditing ? '✏️ Eszközcsoport szerkesztése' : '➕ Új eszközcsoport'}
          </h2>
          <button
            onClick={() => onClose(false)}
            className="btn-close"
            disabled={isSubmitting}
          >
            ✕
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="modal-body">
          {/* Név */}
          <div className="form-group">
            <label htmlFor="name">
              Név <span className="required">*</span>
            </label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="pl. Konyhai berendezések"
              required
              disabled={isSubmitting}
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
              placeholder="Opcionális leírás"
              rows={3}
              disabled={isSubmitting}
            />
          </div>

          {/* Amortizációs ráta */}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="depreciation_rate">Amortizáció (%/év)</label>
              <input
                id="depreciation_rate"
                name="depreciation_rate"
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={formData.depreciation_rate}
                onChange={handleChange}
                placeholder="pl. 10.00"
                disabled={isSubmitting}
              />
            </div>

            {/* Várható élettartam */}
            <div className="form-group">
              <label htmlFor="expected_lifetime_years">
                Várható élettartam (év)
              </label>
              <input
                id="expected_lifetime_years"
                name="expected_lifetime_years"
                type="number"
                min="1"
                value={formData.expected_lifetime_years}
                onChange={handleChange}
                placeholder="pl. 5"
                disabled={isSubmitting}
              />
            </div>
          </div>

          {/* Aktív státusz */}
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                disabled={isSubmitting}
              />
              <span>Aktív</span>
            </label>
          </div>

          {/* Gombok */}
          <div className="modal-footer">
            <button
              type="button"
              onClick={() => onClose(false)}
              className="btn-cancel"
              disabled={isSubmitting}
            >
              Mégse
            </button>
            <button type="submit" className="btn-save" disabled={isSubmitting}>
              {isSubmitting ? 'Mentés...' : 'Mentés'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
