/**
 * AssetEditor - Eszköz létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új eszköz létrehozása (POST /api/assets)
 *   - Meglévő eszköz szerkesztése (PATCH /api/assets/{id})
 *   - Validáció (név, eszközcsoport kötelező)
 *   - Dátum picker, ár mezők, státusz választó
 *   - Modal overlay
 */

import { useState } from 'react';
import { createAsset, updateAsset } from '@/services/assetService';
import type { Asset, AssetGroup, AssetCreate, AssetUpdate } from '@/types/asset';
import './AssetEditor.css';

interface AssetEditorProps {
  asset: Asset | null; // null = új, Asset = szerkesztés
  assetGroups: AssetGroup[];
  onClose: (shouldRefresh: boolean) => void;
}

export const AssetEditor = ({
  asset,
  assetGroups,
  onClose,
}: AssetEditorProps) => {
  const isEditing = !!asset;

  // Form állapot
  const [formData, setFormData] = useState({
    asset_group_id: asset?.asset_group_id?.toString() || '',
    name: asset?.name || '',
    inventory_number: asset?.inventory_number || '',
    manufacturer: asset?.manufacturer || '',
    model: asset?.model || '',
    serial_number: asset?.serial_number || '',
    purchase_date: asset?.purchase_date || '',
    purchase_price: asset?.purchase_price?.toString() || '',
    current_value: asset?.current_value?.toString() || '',
    location: asset?.location || '',
    responsible_employee_id: asset?.responsible_employee_id?.toString() || '',
    status: asset?.status || 'ACTIVE',
    notes: asset?.notes || '',
    is_active: asset?.is_active ?? true,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
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
      alert('Az eszköz neve kötelező!');
      return;
    }

    if (!formData.asset_group_id) {
      alert('Az eszközcsoport választása kötelező!');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing) {
        const updateData: AssetUpdate = {
          asset_group_id: parseInt(formData.asset_group_id),
          name: formData.name.trim(),
          inventory_number: formData.inventory_number.trim() || null,
          manufacturer: formData.manufacturer.trim() || null,
          model: formData.model.trim() || null,
          serial_number: formData.serial_number.trim() || null,
          purchase_date: formData.purchase_date || null,
          purchase_price: formData.purchase_price
            ? parseFloat(formData.purchase_price)
            : null,
          current_value: formData.current_value
            ? parseFloat(formData.current_value)
            : null,
          location: formData.location.trim() || null,
          responsible_employee_id: formData.responsible_employee_id
            ? parseInt(formData.responsible_employee_id)
            : null,
          status: formData.status,
          notes: formData.notes.trim() || null,
          is_active: formData.is_active,
        };

        await updateAsset(asset!.id, updateData);
        alert('Eszköz sikeresen frissítve!');
      } else {
        const createData: AssetCreate = {
          asset_group_id: parseInt(formData.asset_group_id),
          name: formData.name.trim(),
          inventory_number: formData.inventory_number.trim() || null,
          manufacturer: formData.manufacturer.trim() || null,
          model: formData.model.trim() || null,
          serial_number: formData.serial_number.trim() || null,
          purchase_date: formData.purchase_date || null,
          purchase_price: formData.purchase_price
            ? parseFloat(formData.purchase_price)
            : null,
          current_value: formData.current_value
            ? parseFloat(formData.current_value)
            : null,
          location: formData.location.trim() || null,
          responsible_employee_id: formData.responsible_employee_id
            ? parseInt(formData.responsible_employee_id)
            : null,
          status: formData.status,
          notes: formData.notes.trim() || null,
          is_active: formData.is_active,
        };

        await createAsset(createData);
        alert('Eszköz sikeresen létrehozva!');
      }

      onClose(true);
    } catch (error: any) {
      console.error('Hiba az eszköz mentésekor:', error);
      const errorMsg = error?.response?.data?.detail || 'Ismeretlen hiba történt';
      alert(`Hiba: ${errorMsg}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={() => onClose(false)}>
      <div
        className="modal-content modal-large"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal fejléc */}
        <div className="modal-header">
          <h2>{isEditing ? '✏️ Eszköz szerkesztése' : '➕ Új eszköz'}</h2>
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
          {/* Alapadatok */}
          <fieldset>
            <legend>Alapadatok</legend>

            <div className="form-row">
              {/* Eszközcsoport */}
              <div className="form-group">
                <label htmlFor="asset_group_id">
                  Eszközcsoport <span className="required">*</span>
                </label>
                <select
                  id="asset_group_id"
                  name="asset_group_id"
                  value={formData.asset_group_id}
                  onChange={handleChange}
                  required
                  disabled={isSubmitting}
                >
                  <option value="">-- Válassz eszközcsoportot --</option>
                  {assetGroups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Név */}
              <div className="form-group">
                <label htmlFor="name">
                  Eszköz neve <span className="required">*</span>
                </label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="pl. Dell XPS 15 laptop"
                  required
                  disabled={isSubmitting}
                />
              </div>
            </div>

            <div className="form-row">
              {/* Leltári szám */}
              <div className="form-group">
                <label htmlFor="inventory_number">Leltári szám</label>
                <input
                  id="inventory_number"
                  name="inventory_number"
                  type="text"
                  value={formData.inventory_number}
                  onChange={handleChange}
                  placeholder="pl. INV-2024-001"
                  disabled={isSubmitting}
                />
              </div>

              {/* Helyszín */}
              <div className="form-group">
                <label htmlFor="location">Helyszín</label>
                <input
                  id="location"
                  name="location"
                  type="text"
                  value={formData.location}
                  onChange={handleChange}
                  placeholder="pl. Konyha, Iroda"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            <div className="form-row">
              {/* Gyártó */}
              <div className="form-group">
                <label htmlFor="manufacturer">Gyártó</label>
                <input
                  id="manufacturer"
                  name="manufacturer"
                  type="text"
                  value={formData.manufacturer}
                  onChange={handleChange}
                  placeholder="pl. Dell, Samsung"
                  disabled={isSubmitting}
                />
              </div>

              {/* Modell */}
              <div className="form-group">
                <label htmlFor="model">Modell</label>
                <input
                  id="model"
                  name="model"
                  type="text"
                  value={formData.model}
                  onChange={handleChange}
                  placeholder="pl. XPS 15 9520"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            {/* Sorozatszám */}
            <div className="form-group">
              <label htmlFor="serial_number">Sorozatszám</label>
              <input
                id="serial_number"
                name="serial_number"
                type="text"
                value={formData.serial_number}
                onChange={handleChange}
                placeholder="pl. SN123456789"
                disabled={isSubmitting}
              />
            </div>
          </fieldset>

          {/* Pénzügyi adatok */}
          <fieldset>
            <legend>Pénzügyi adatok</legend>

            <div className="form-row">
              {/* Beszerzési dátum */}
              <div className="form-group">
                <label htmlFor="purchase_date">Beszerzési dátum</label>
                <input
                  id="purchase_date"
                  name="purchase_date"
                  type="date"
                  value={formData.purchase_date}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
              </div>

              {/* Beszerzési ár */}
              <div className="form-group">
                <label htmlFor="purchase_price">Beszerzési ár (Ft)</label>
                <input
                  id="purchase_price"
                  name="purchase_price"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.purchase_price}
                  onChange={handleChange}
                  placeholder="pl. 500000"
                  disabled={isSubmitting}
                />
              </div>

              {/* Jelenlegi érték */}
              <div className="form-group">
                <label htmlFor="current_value">Jelenlegi érték (Ft)</label>
                <input
                  id="current_value"
                  name="current_value"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.current_value}
                  onChange={handleChange}
                  placeholder="pl. 300000"
                  disabled={isSubmitting}
                />
              </div>
            </div>
          </fieldset>

          {/* Státusz és megjegyzések */}
          <fieldset>
            <legend>Státusz és megjegyzések</legend>

            <div className="form-row">
              {/* Státusz */}
              <div className="form-group">
                <label htmlFor="status">Státusz</label>
                <select
                  id="status"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  disabled={isSubmitting}
                >
                  <option value="ACTIVE">Aktív</option>
                  <option value="MAINTENANCE">Karbantartás</option>
                  <option value="RETIRED">Kivonva</option>
                  <option value="SOLD">Eladva</option>
                  <option value="DAMAGED">Sérült</option>
                </select>
              </div>

              {/* Felelős munkatárs ID (opcionális) */}
              <div className="form-group">
                <label htmlFor="responsible_employee_id">
                  Felelős munkatárs ID
                </label>
                <input
                  id="responsible_employee_id"
                  name="responsible_employee_id"
                  type="number"
                  value={formData.responsible_employee_id}
                  onChange={handleChange}
                  placeholder="pl. 5"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            {/* Megjegyzések */}
            <div className="form-group">
              <label htmlFor="notes">Megjegyzések</label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                placeholder="Garancia, szervizelési információk, stb."
                rows={4}
                disabled={isSubmitting}
              />
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
                <span>Aktív (nyilvántartásban)</span>
              </label>
            </div>
          </fieldset>

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
