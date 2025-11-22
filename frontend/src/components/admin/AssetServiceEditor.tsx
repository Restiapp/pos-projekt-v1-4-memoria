/**
 * AssetServiceEditor - Szerviz bejegyzés létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új szerviz bejegyzés létrehozása (POST /api/assets/services)
 *   - Meglévő szerviz bejegyzés szerkesztése (PATCH /api/assets/services/{id})
 *   - Validáció (eszköz, típus, dátum, leírás kötelező)
 *   - Modal overlay
 */

import { useState } from 'react';
import { createAssetService, updateAssetService } from '@/services/assetService';
import type { AssetService, Asset, AssetServiceCreate, AssetServiceUpdate } from '@/types/asset';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './AssetServiceEditor.css';

interface AssetServiceEditorProps {
  service: AssetService | null; // null = új, AssetService = szerkesztés
  assets: Asset[];
  onClose: (shouldRefresh: boolean) => void;
}

export const AssetServiceEditor = ({
  service,
  assets,
  onClose,
}: AssetServiceEditorProps) => {
  const isEditing = !!service;
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();

  // Form állapot
  const [formData, setFormData] = useState({
    asset_id: service?.asset_id?.toString() || '',
    service_type: service?.service_type || 'MAINTENANCE',
    service_date: service?.service_date || new Date().toISOString().split('T')[0],
    description: service?.description || '',
    cost: service?.cost?.toString() || '',
    service_provider: service?.service_provider || '',
    next_service_date: service?.next_service_date || '',
    performed_by_employee_id: service?.performed_by_employee_id?.toString() || '',
    documents_url: service?.documents_url || '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (!formData.asset_id) {
      showToast('Az eszköz választása kötelező!', 'error');
      return;
    }

    if (!formData.service_type) {
      showToast('A szerviz típusa kötelező!', 'error');
      return;
    }

    if (!formData.service_date) {
      showToast('A szerviz dátuma kötelező!', 'error');
      return;
    }

    if (!formData.description.trim()) {
      showToast('A leírás kötelező!', 'error');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing) {
        const updateData: AssetServiceUpdate = {
          service_type: formData.service_type,
          service_date: formData.service_date,
          description: formData.description.trim(),
          cost: formData.cost ? parseFloat(formData.cost) : null,
          service_provider: formData.service_provider.trim() || null,
          next_service_date: formData.next_service_date || null,
          performed_by_employee_id: formData.performed_by_employee_id
            ? parseInt(formData.performed_by_employee_id)
            : null,
          documents_url: formData.documents_url.trim() || null,
        };

        await updateAssetService(service!.id, updateData);
        showToast('Szerviz bejegyzés sikeresen frissítve!', 'success');
      } else {
        const createData: AssetServiceCreate = {
          asset_id: parseInt(formData.asset_id),
          service_type: formData.service_type,
          service_date: formData.service_date,
          description: formData.description.trim(),
          cost: formData.cost ? parseFloat(formData.cost) : null,
          service_provider: formData.service_provider.trim() || null,
          next_service_date: formData.next_service_date || null,
          performed_by_employee_id: formData.performed_by_employee_id
            ? parseInt(formData.performed_by_employee_id)
            : null,
          documents_url: formData.documents_url.trim() || null,
        };

        await createAssetService(createData);
        showToast('Szerviz bejegyzés sikeresen létrehozva!', 'success');
      }

      onClose(true);
    } catch (error: any) {
      console.error('Hiba a szerviz bejegyzés mentésekor:', error);
      const errorMsg = error?.response?.data?.detail || 'Ismeretlen hiba történt';
      showToast(`Hiba: ${errorMsg}`, 'error');
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
            {isEditing
              ? '✏️ Szerviz bejegyzés szerkesztése'
              : '➕ Új szerviz bejegyzés'}
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
          {/* Eszköz választás */}
          <div className="form-group">
            <label htmlFor="asset_id">
              Eszköz <span className="required">*</span>
            </label>
            <select
              id="asset_id"
              name="asset_id"
              value={formData.asset_id}
              onChange={handleChange}
              required
              disabled={isSubmitting || isEditing}
            >
              <option value="">-- Válassz eszközt --</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name} ({asset.inventory_number || 'Nincs leltári szám'})
                </option>
              ))}
            </select>
          </div>

          {/* Szerviz típus és dátum */}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="service_type">
                Szerviz típusa <span className="required">*</span>
              </label>
              <select
                id="service_type"
                name="service_type"
                value={formData.service_type}
                onChange={handleChange}
                required
                disabled={isSubmitting}
              >
                <option value="MAINTENANCE">Karbantartás</option>
                <option value="REPAIR">Javítás</option>
                <option value="INSPECTION">Felülvizsgálat</option>
                <option value="CALIBRATION">Kalibrálás</option>
                <option value="CLEANING">Tisztítás</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="service_date">
                Szerviz dátuma <span className="required">*</span>
              </label>
              <input
                id="service_date"
                name="service_date"
                type="date"
                value={formData.service_date}
                onChange={handleChange}
                required
                disabled={isSubmitting}
              />
            </div>
          </div>

          {/* Leírás */}
          <div className="form-group">
            <label htmlFor="description">
              Leírás <span className="required">*</span>
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Részletes leírás az elvégzett munkáról"
              rows={4}
              required
              disabled={isSubmitting}
            />
          </div>

          {/* Költség és szervizes */}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="cost">Költség (Ft)</label>
              <input
                id="cost"
                name="cost"
                type="number"
                step="0.01"
                min="0"
                value={formData.cost}
                onChange={handleChange}
                placeholder="pl. 15000"
                disabled={isSubmitting}
              />
            </div>

            <div className="form-group">
              <label htmlFor="service_provider">Szervizes cég/személy</label>
              <input
                id="service_provider"
                name="service_provider"
                type="text"
                value={formData.service_provider}
                onChange={handleChange}
                placeholder="pl. Szerviz Kft."
                disabled={isSubmitting}
              />
            </div>
          </div>

          {/* Következő szerviz és végző munkatárs */}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="next_service_date">Következő szerviz dátuma</label>
              <input
                id="next_service_date"
                name="next_service_date"
                type="date"
                value={formData.next_service_date}
                onChange={handleChange}
                disabled={isSubmitting}
              />
            </div>

            <div className="form-group">
              <label htmlFor="performed_by_employee_id">
                Végző munkatárs ID (belső)
              </label>
              <input
                id="performed_by_employee_id"
                name="performed_by_employee_id"
                type="number"
                value={formData.performed_by_employee_id}
                onChange={handleChange}
                placeholder="pl. 3"
                disabled={isSubmitting}
              />
            </div>
          </div>

          {/* Dokumentumok URL */}
          <div className="form-group">
            <label htmlFor="documents_url">Dokumentumok URL (számla, jegyzőkönyv)</label>
            <input
              id="documents_url"
              name="documents_url"
              type="url"
              value={formData.documents_url}
              onChange={handleChange}
              placeholder="https://example.com/invoice.pdf"
              disabled={isSubmitting}
            />
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
