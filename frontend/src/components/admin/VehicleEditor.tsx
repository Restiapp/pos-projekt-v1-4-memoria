/**
 * VehicleEditor - Jármű létrehozó/szerkesztő modal
 *
 * Funkciók:
 *   - Új jármű létrehozása
 *   - Meglévő jármű szerkesztése
 *   - Form validáció
 *   - Biztosítás és műszaki lejárat kezelése
 */

import { useState } from 'react';
import { createVehicle, updateVehicle } from '@/services/vehicleService';
import type { Vehicle, VehicleCreate, VehicleUpdate } from '@/types/vehicle';
import './VehicleEditor.css';
import { notifications } from '@mantine/notifications';

interface VehicleEditorProps {
  vehicle: Vehicle | null; // null = új jármű létrehozása
  onClose: (shouldRefresh: boolean) => void;
}

export const VehicleEditor = ({ vehicle, onClose }: VehicleEditorProps) => {
  const isEditMode = vehicle !== null;
    
  // Form állapotok
  const [formData, setFormData] = useState({
    license_plate: vehicle?.license_plate || '',
    brand: vehicle?.brand || '',
    model: vehicle?.model || '',
    year: vehicle?.year || null,
    vin: vehicle?.vin || '',
    fuel_type: vehicle?.fuel_type || 'PETROL_95',
    purchase_date: vehicle?.purchase_date || '',
    purchase_price: vehicle?.purchase_price || null,
    current_value: vehicle?.current_value || null,
    current_mileage: vehicle?.current_mileage || null,
    responsible_employee_id: vehicle?.responsible_employee_id || null,
    status: vehicle?.status || 'ACTIVE',
    insurance_expiry_date: vehicle?.insurance_expiry_date || '',
    mot_expiry_date: vehicle?.mot_expiry_date || '',
    notes: vehicle?.notes || '',
    is_active: vehicle?.is_active ?? true,
  });

  const [isSaving, setIsSaving] = useState(false);

  // Form input change handler
  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value, type } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]:
        type === 'checkbox'
          ? (e.target as HTMLInputElement).checked
          : type === 'number'
          ? value === ''
            ? null
            : parseFloat(value)
          : value,
    }));
  };

  // Form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (
      !formData.license_plate ||
      !formData.brand ||
      !formData.model ||
      !formData.fuel_type
    ) {
      notify.warning(
        'Kérlek, töltsd ki a kötelező mezőket: Rendszám, Márka, Modell, Üzemanyag!'
      );
      return;
    }

    setIsSaving(true);

    try {
      if (isEditMode) {
        // Frissítés
        const updateData: VehicleUpdate = {
          license_plate: formData.license_plate,
          brand: formData.brand,
          model: formData.model,
          year: formData.year,
          vin: formData.vin || null,
          fuel_type: formData.fuel_type,
          purchase_date: formData.purchase_date || null,
          purchase_price: formData.purchase_price,
          current_value: formData.current_value,
          current_mileage: formData.current_mileage,
          responsible_employee_id: formData.responsible_employee_id,
          status: formData.status,
          insurance_expiry_date: formData.insurance_expiry_date || null,
          mot_expiry_date: formData.mot_expiry_date || null,
          notes: formData.notes || null,
          is_active: formData.is_active,
        };

        await updateVehicle(vehicle!.id, updateData);
        notifications.show({
        title: 'Siker',
        message: 'Jármű sikeresen frissítve!',
        color: 'green',
      });
      } else {
        // Létrehozás
        const createData: VehicleCreate = {
          license_plate: formData.license_plate,
          brand: formData.brand,
          model: formData.model,
          year: formData.year,
          vin: formData.vin || null,
          fuel_type: formData.fuel_type,
          purchase_date: formData.purchase_date || null,
          purchase_price: formData.purchase_price,
          current_value: formData.current_value,
          current_mileage: formData.current_mileage,
          responsible_employee_id: formData.responsible_employee_id,
          status: formData.status,
          insurance_expiry_date: formData.insurance_expiry_date || null,
          mot_expiry_date: formData.mot_expiry_date || null,
          notes: formData.notes || null,
          is_active: formData.is_active,
        };

        await createVehicle(createData);
        notifications.show({
        title: 'Siker',
        message: 'Jármű sikeresen létrehozva!',
        color: 'green',
      });
      }

      onClose(true); // Frissítés szükséges
    } catch (error) {
      console.error('Hiba a jármű mentésekor:', error);
      notifications.show({
        title: 'Hiba',
        message: 'Nem sikerült menteni a járművet!',
        color: 'red',
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={() => onClose(false)}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditMode ? 'Jármű szerkesztése' : 'Új jármű létrehozása'}</h2>
          <button
            onClick={() => onClose(false)}
            className="btn-close"
            disabled={isSaving}
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="vehicle-form">
          <div className="form-section">
            <h3>Alapadatok</h3>

            <div className="form-row">
              <div className="form-field">
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

              <div className="form-field">
                <label htmlFor="vin">VIN (alvázszám)</label>
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
            </div>

            <div className="form-row">
              <div className="form-field">
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

              <div className="form-field">
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

              <div className="form-field">
                <label htmlFor="year">Évjárat</label>
                <input
                  type="number"
                  id="year"
                  name="year"
                  value={formData.year || ''}
                  onChange={handleChange}
                  placeholder="2020"
                  min={1900}
                  max={2100}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-field">
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
                  <option value="LPG">LPG</option>
                  <option value="CNG">CNG</option>
                </select>
              </div>

              <div className="form-field">
                <label htmlFor="status">Státusz</label>
                <select
                  id="status"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                >
                  <option value="ACTIVE">Aktív</option>
                  <option value="MAINTENANCE">Karbantartás alatt</option>
                  <option value="OUT_OF_SERVICE">Üzemen kívül</option>
                  <option value="SOLD">Eladva</option>
                  <option value="RETIRED">Kivonva</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Pénzügyi adatok</h3>

            <div className="form-row">
              <div className="form-field">
                <label htmlFor="purchase_date">Beszerzési dátum</label>
                <input
                  type="date"
                  id="purchase_date"
                  name="purchase_date"
                  value={formData.purchase_date}
                  onChange={handleChange}
                />
              </div>

              <div className="form-field">
                <label htmlFor="purchase_price">Beszerzési ár (Ft)</label>
                <input
                  type="number"
                  id="purchase_price"
                  name="purchase_price"
                  value={formData.purchase_price || ''}
                  onChange={handleChange}
                  placeholder="5000000"
                  min={0}
                  step={1}
                />
              </div>

              <div className="form-field">
                <label htmlFor="current_value">Jelenlegi érték (Ft)</label>
                <input
                  type="number"
                  id="current_value"
                  name="current_value"
                  value={formData.current_value || ''}
                  onChange={handleChange}
                  placeholder="4000000"
                  min={0}
                  step={1}
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Kilométeróra és vizsgák</h3>

            <div className="form-row">
              <div className="form-field">
                <label htmlFor="current_mileage">Kilométeróra állás (km)</label>
                <input
                  type="number"
                  id="current_mileage"
                  name="current_mileage"
                  value={formData.current_mileage || ''}
                  onChange={handleChange}
                  placeholder="50000"
                  min={0}
                  step={1}
                />
              </div>

              <div className="form-field">
                <label htmlFor="insurance_expiry_date">Biztosítás lejár</label>
                <input
                  type="date"
                  id="insurance_expiry_date"
                  name="insurance_expiry_date"
                  value={formData.insurance_expiry_date}
                  onChange={handleChange}
                />
              </div>

              <div className="form-field">
                <label htmlFor="mot_expiry_date">Műszaki vizsga lejár</label>
                <input
                  type="date"
                  id="mot_expiry_date"
                  name="mot_expiry_date"
                  value={formData.mot_expiry_date}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>További információk</h3>

            <div className="form-field">
              <label htmlFor="responsible_employee_id">
                Felelős munkatárs ID
              </label>
              <input
                type="number"
                id="responsible_employee_id"
                name="responsible_employee_id"
                value={formData.responsible_employee_id || ''}
                onChange={handleChange}
                placeholder="1"
                min={1}
                step={1}
              />
            </div>

            <div className="form-field">
              <label htmlFor="notes">Megjegyzések</label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                placeholder="További információk..."
                rows={3}
              />
            </div>

            <div className="form-field-checkbox">
              <label htmlFor="is_active">
                <input
                  type="checkbox"
                  id="is_active"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleChange}
                />
                <span>Aktív (logikai törlés)</span>
              </label>
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              onClick={() => onClose(false)}
              className="btn-cancel"
              disabled={isSaving}
            >
              Mégse
            </button>
            <button
              type="submit"
              className="btn-save"
              disabled={isSaving}
            >
              {isSaving ? 'Mentés...' : isEditMode ? 'Frissítés' : 'Létrehozás'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
