/**
 * VehicleEditor - Jármű létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új jármű létrehozása (POST /api/vehicles)
 *   - Meglévő jármű szerkesztése (PATCH /api/vehicles/{id})
 *   - Validáció (rendszám, márka, modell, üzemanyag kötelező)
 *   - Dátum picker, ár mezők, státusz választó
 *   - Biztosítási és műszaki dátumok
 *   - Modal overlay
 */

import { useState } from 'react';
import { createVehicle, updateVehicle } from '@/services/vehicleService';
import type { Vehicle, VehicleCreate, VehicleUpdate } from '@/types/vehicle';
import './VehicleEditor.css';

interface VehicleEditorProps {
  vehicle: Vehicle | null; // null = új, Vehicle = szerkesztés
  onClose: (shouldRefresh: boolean) => void;
}

export const VehicleEditor = ({ vehicle, onClose }: VehicleEditorProps) => {
  const isEditing = !!vehicle;

  // Form állapot
  const [formData, setFormData] = useState({
    license_plate: vehicle?.license_plate || '',
    brand: vehicle?.brand || '',
    model: vehicle?.model || '',
    year: vehicle?.year?.toString() || '',
    vin: vehicle?.vin || '',
    fuel_type: vehicle?.fuel_type || 'PETROL_95',
    purchase_date: vehicle?.purchase_date || '',
    purchase_price: vehicle?.purchase_price?.toString() || '',
    current_value: vehicle?.current_value?.toString() || '',
    current_mileage: vehicle?.current_mileage?.toString() || '',
    responsible_employee_id: vehicle?.responsible_employee_id?.toString() || '',
    status: vehicle?.status || 'ACTIVE',
    insurance_expiry_date: vehicle?.insurance_expiry_date || '',
    mot_expiry_date: vehicle?.mot_expiry_date || '',
    notes: vehicle?.notes || '',
    is_active: vehicle?.is_active ?? true,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
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
    if (!formData.license_plate.trim()) {
      alert('A rendszám kötelező!');
      return;
    }

    if (!formData.brand.trim()) {
      alert('A márka kötelező!');
      return;
    }

    if (!formData.model.trim()) {
      alert('A modell kötelező!');
      return;
    }

    if (!formData.fuel_type) {
      alert('Az üzemanyag típusa kötelező!');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing) {
        const updateData: VehicleUpdate = {
          license_plate: formData.license_plate.trim(),
          brand: formData.brand.trim(),
          model: formData.model.trim(),
          year: formData.year ? parseInt(formData.year) : null,
          vin: formData.vin.trim() || null,
          fuel_type: formData.fuel_type,
          purchase_date: formData.purchase_date || null,
          purchase_price: formData.purchase_price
            ? parseFloat(formData.purchase_price)
            : null,
          current_value: formData.current_value
            ? parseFloat(formData.current_value)
            : null,
          current_mileage: formData.current_mileage
            ? parseInt(formData.current_mileage)
            : null,
          responsible_employee_id: formData.responsible_employee_id
            ? parseInt(formData.responsible_employee_id)
            : null,
          status: formData.status,
          insurance_expiry_date: formData.insurance_expiry_date || null,
          mot_expiry_date: formData.mot_expiry_date || null,
          notes: formData.notes.trim() || null,
          is_active: formData.is_active,
        };

        await updateVehicle(vehicle.id, updateData);
        alert('Jármű sikeresen frissítve!');
      } else {
        const createData: VehicleCreate = {
          license_plate: formData.license_plate.trim(),
          brand: formData.brand.trim(),
          model: formData.model.trim(),
          year: formData.year ? parseInt(formData.year) : null,
          vin: formData.vin.trim() || null,
          fuel_type: formData.fuel_type,
          purchase_date: formData.purchase_date || null,
          purchase_price: formData.purchase_price
            ? parseFloat(formData.purchase_price)
            : null,
          current_value: formData.current_value
            ? parseFloat(formData.current_value)
            : null,
          current_mileage: formData.current_mileage
            ? parseInt(formData.current_mileage)
            : null,
          responsible_employee_id: formData.responsible_employee_id
            ? parseInt(formData.responsible_employee_id)
            : null,
          status: formData.status,
          insurance_expiry_date: formData.insurance_expiry_date || null,
          mot_expiry_date: formData.mot_expiry_date || null,
          notes: formData.notes.trim() || null,
          is_active: formData.is_active,
        };

        await createVehicle(createData);
        alert('Jármű sikeresen létrehozva!');
      }

      onClose(true); // Frissítés szükséges
    } catch (error) {
      console.error('Hiba a jármű mentésekor:', error);
      alert('Hiba történt a mentés során!');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={() => onClose(false)}>
      <div className="modal-content vehicle-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditing ? 'Jármű szerkesztése' : 'Új jármű létrehozása'}</h2>
          <button
            onClick={() => onClose(false)}
            className="modal-close"
            aria-label="Bezárás"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-grid">
            {/* Rendszám */}
            <div className="form-group">
              <label htmlFor="license_plate">
                Rendszám <span className="required">*</span>
              </label>
              <input
                type="text"
                id="license_plate"
                name="license_plate"
                value={formData.license_plate}
                onChange={handleChange}
                placeholder="ABC-123"
                required
              />
            </div>

            {/* Márka */}
            <div className="form-group">
              <label htmlFor="brand">
                Márka <span className="required">*</span>
              </label>
              <input
                type="text"
                id="brand"
                name="brand"
                value={formData.brand}
                onChange={handleChange}
                placeholder="Toyota"
                required
              />
            </div>

            {/* Modell */}
            <div className="form-group">
              <label htmlFor="model">
                Modell <span className="required">*</span>
              </label>
              <input
                type="text"
                id="model"
                name="model"
                value={formData.model}
                onChange={handleChange}
                placeholder="Corolla"
                required
              />
            </div>

            {/* Gyártási év */}
            <div className="form-group">
              <label htmlFor="year">Gyártási év</label>
              <input
                type="number"
                id="year"
                name="year"
                value={formData.year}
                onChange={handleChange}
                placeholder="2024"
                min="1900"
                max="2100"
              />
            </div>

            {/* VIN */}
            <div className="form-group">
              <label htmlFor="vin">VIN</label>
              <input
                type="text"
                id="vin"
                name="vin"
                value={formData.vin}
                onChange={handleChange}
                placeholder="1HGBH41JXMN109186"
                maxLength={17}
              />
            </div>

            {/* Üzemanyag típus */}
            <div className="form-group">
              <label htmlFor="fuel_type">
                Üzemanyag típusa <span className="required">*</span>
              </label>
              <select
                id="fuel_type"
                name="fuel_type"
                value={formData.fuel_type}
                onChange={handleChange}
                required
              >
                <option value="PETROL_95">95-ös benzin</option>
                <option value="PETROL_98">98-as benzin</option>
                <option value="DIESEL">Dízel</option>
                <option value="ELECTRIC">Elektromos</option>
                <option value="HYBRID">Hibrid</option>
                <option value="LPG">Gázolaj (LPG)</option>
              </select>
            </div>

            {/* Beszerzési dátum */}
            <div className="form-group">
              <label htmlFor="purchase_date">Beszerzési dátum</label>
              <input
                type="date"
                id="purchase_date"
                name="purchase_date"
                value={formData.purchase_date}
                onChange={handleChange}
              />
            </div>

            {/* Beszerzési ár */}
            <div className="form-group">
              <label htmlFor="purchase_price">Beszerzési ár (Ft)</label>
              <input
                type="number"
                id="purchase_price"
                name="purchase_price"
                value={formData.purchase_price}
                onChange={handleChange}
                placeholder="5000000"
                min="0"
                step="0.01"
              />
            </div>

            {/* Jelenlegi érték */}
            <div className="form-group">
              <label htmlFor="current_value">Jelenlegi érték (Ft)</label>
              <input
                type="number"
                id="current_value"
                name="current_value"
                value={formData.current_value}
                onChange={handleChange}
                placeholder="4000000"
                min="0"
                step="0.01"
              />
            </div>

            {/* Kilométeróra állás */}
            <div className="form-group">
              <label htmlFor="current_mileage">Km állás</label>
              <input
                type="number"
                id="current_mileage"
                name="current_mileage"
                value={formData.current_mileage}
                onChange={handleChange}
                placeholder="50000"
                min="0"
              />
            </div>

            {/* Felelős munkatárs */}
            <div className="form-group">
              <label htmlFor="responsible_employee_id">
                Felelős munkatárs ID
              </label>
              <input
                type="number"
                id="responsible_employee_id"
                name="responsible_employee_id"
                value={formData.responsible_employee_id}
                onChange={handleChange}
                placeholder="1"
                min="1"
              />
            </div>

            {/* Státusz */}
            <div className="form-group">
              <label htmlFor="status">Státusz</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
              >
                <option value="ACTIVE">Használatban</option>
                <option value="MAINTENANCE">Karbantartás alatt</option>
                <option value="OUT_OF_SERVICE">Nem üzemképes</option>
                <option value="SOLD">Eladva</option>
                <option value="RETIRED">Kivonva</option>
              </select>
            </div>

            {/* Biztosítás lejárata */}
            <div className="form-group">
              <label htmlFor="insurance_expiry_date">
                Biztosítás lejárata
              </label>
              <input
                type="date"
                id="insurance_expiry_date"
                name="insurance_expiry_date"
                value={formData.insurance_expiry_date}
                onChange={handleChange}
              />
            </div>

            {/* Műszaki vizsga lejárata */}
            <div className="form-group">
              <label htmlFor="mot_expiry_date">Műszaki vizsga lejárata</label>
              <input
                type="date"
                id="mot_expiry_date"
                name="mot_expiry_date"
                value={formData.mot_expiry_date}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* Megjegyzések */}
          <div className="form-group-full">
            <label htmlFor="notes">Megjegyzések</label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              placeholder="Cégautó, céges használatra..."
            />
          </div>

          {/* Aktív státusz */}
          <div className="form-group-full">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
              />
              Aktív
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
            <button
              type="submit"
              className="btn-save"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Mentés...' : isEditing ? 'Frissítés' : 'Létrehozás'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
