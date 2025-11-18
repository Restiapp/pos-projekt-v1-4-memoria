/**
 * RefuelingEditor - Tankolás létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új tankolás létrehozása (POST /api/vehicles/refuelings)
 *   - Meglévő tankolás szerkesztése (PATCH /api/vehicles/refuelings/{id})
 *   - Validáció (jármű, dátum, üzemanyag, mennyiség, ár kötelező)
 *   - Automatikus összkölts számítás
 *   - Modal overlay
 */

import { useState, useEffect } from 'react';
import { createRefueling, updateRefueling } from '@/services/vehicleService';
import type { VehicleRefueling, VehicleRefuelingCreate, VehicleRefuelingUpdate, Vehicle } from '@/types/vehicle';
import './RefuelingEditor.css';

interface RefuelingEditorProps {
  refueling: VehicleRefueling | null; // null = új, VehicleRefueling = szerkesztés
  vehicles: Vehicle[];
  onClose: (shouldRefresh: boolean) => void;
}

export const RefuelingEditor = ({ refueling, vehicles, onClose }: RefuelingEditorProps) => {
  const isEditing = !!refueling;

  // Form állapot
  const [formData, setFormData] = useState({
    vehicle_id: refueling?.vehicle_id?.toString() || '',
    refueling_date: refueling?.refueling_date || new Date().toISOString().split('T')[0],
    mileage: refueling?.mileage?.toString() || '',
    fuel_type: refueling?.fuel_type || 'PETROL_95',
    quantity_liters: refueling?.quantity_liters?.toString() || '',
    price_per_liter: refueling?.price_per_liter?.toString() || '',
    total_cost: refueling?.total_cost?.toString() || '',
    full_tank: refueling?.full_tank ?? true,
    location: refueling?.location || '',
    invoice_number: refueling?.invoice_number || '',
    recorded_by_employee_id: refueling?.recorded_by_employee_id?.toString() || '',
    notes: refueling?.notes || '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Automatikus összkölts számítás
  useEffect(() => {
    if (formData.quantity_liters && formData.price_per_liter) {
      const quantity = parseFloat(formData.quantity_liters);
      const price = parseFloat(formData.price_per_liter);
      if (!isNaN(quantity) && !isNaN(price)) {
        const total = quantity * price;
        setFormData(prev => ({ ...prev, total_cost: total.toFixed(2) }));
      }
    }
  }, [formData.quantity_liters, formData.price_per_liter]);

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
    if (!formData.vehicle_id) {
      alert('A jármű választása kötelező!');
      return;
    }

    if (!formData.refueling_date) {
      alert('A tankolás dátuma kötelező!');
      return;
    }

    if (!formData.fuel_type) {
      alert('Az üzemanyag típusa kötelező!');
      return;
    }

    if (!formData.quantity_liters || parseFloat(formData.quantity_liters) <= 0) {
      alert('A mennyiség kötelező és nagyobb kell legyen nullánál!');
      return;
    }

    if (!formData.price_per_liter || parseFloat(formData.price_per_liter) <= 0) {
      alert('Az egységár kötelező és nagyobb kell legyen nullánál!');
      return;
    }

    if (!formData.total_cost || parseFloat(formData.total_cost) <= 0) {
      alert('A teljes költség kötelező és nagyobb kell legyen nullánál!');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing) {
        const updateData: VehicleRefuelingUpdate = {
          refueling_date: formData.refueling_date,
          mileage: formData.mileage ? parseInt(formData.mileage) : null,
          fuel_type: formData.fuel_type,
          quantity_liters: parseFloat(formData.quantity_liters),
          price_per_liter: parseFloat(formData.price_per_liter),
          total_cost: parseFloat(formData.total_cost),
          full_tank: formData.full_tank,
          location: formData.location.trim() || null,
          invoice_number: formData.invoice_number.trim() || null,
          recorded_by_employee_id: formData.recorded_by_employee_id
            ? parseInt(formData.recorded_by_employee_id)
            : null,
          notes: formData.notes.trim() || null,
        };

        await updateRefueling(refueling.id, updateData);
        alert('Tankolás sikeresen frissítve!');
      } else {
        const createData: VehicleRefuelingCreate = {
          vehicle_id: parseInt(formData.vehicle_id),
          refueling_date: formData.refueling_date,
          mileage: formData.mileage ? parseInt(formData.mileage) : null,
          fuel_type: formData.fuel_type,
          quantity_liters: parseFloat(formData.quantity_liters),
          price_per_liter: parseFloat(formData.price_per_liter),
          total_cost: parseFloat(formData.total_cost),
          full_tank: formData.full_tank,
          location: formData.location.trim() || null,
          invoice_number: formData.invoice_number.trim() || null,
          recorded_by_employee_id: formData.recorded_by_employee_id
            ? parseInt(formData.recorded_by_employee_id)
            : null,
          notes: formData.notes.trim() || null,
        };

        await createRefueling(createData);
        alert('Tankolás sikeresen rögzítve!');
      }

      onClose(true); // Frissítés szükséges
    } catch (error) {
      console.error('Hiba a tankolás mentésekor:', error);
      alert('Hiba történt a mentés során!');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={() => onClose(false)}>
      <div className="modal-content refueling-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditing ? 'Tankolás szerkesztése' : 'Új tankolás rögzítése'}</h2>
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
            {/* Jármű */}
            <div className="form-group">
              <label htmlFor="vehicle_id">
                Jármű <span className="required">*</span>
              </label>
              <select
                id="vehicle_id"
                name="vehicle_id"
                value={formData.vehicle_id}
                onChange={handleChange}
                required
                disabled={isEditing}
              >
                <option value="">Válassz járművet...</option>
                {vehicles.map((vehicle) => (
                  <option key={vehicle.id} value={vehicle.id}>
                    {vehicle.brand} {vehicle.model} ({vehicle.license_plate})
                  </option>
                ))}
              </select>
            </div>

            {/* Tankolás dátuma */}
            <div className="form-group">
              <label htmlFor="refueling_date">
                Tankolás dátuma <span className="required">*</span>
              </label>
              <input
                type="date"
                id="refueling_date"
                name="refueling_date"
                value={formData.refueling_date}
                onChange={handleChange}
                required
              />
            </div>

            {/* Kilométeróra állás */}
            <div className="form-group">
              <label htmlFor="mileage">Km állás</label>
              <input
                type="number"
                id="mileage"
                name="mileage"
                value={formData.mileage}
                onChange={handleChange}
                placeholder="50000"
                min="0"
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

            {/* Mennyiség (liter) */}
            <div className="form-group">
              <label htmlFor="quantity_liters">
                Mennyiség (liter) <span className="required">*</span>
              </label>
              <input
                type="number"
                id="quantity_liters"
                name="quantity_liters"
                value={formData.quantity_liters}
                onChange={handleChange}
                placeholder="50.00"
                min="0"
                step="0.01"
                required
              />
            </div>

            {/* Egységár (Ft/liter) */}
            <div className="form-group">
              <label htmlFor="price_per_liter">
                Egységár (Ft/liter) <span className="required">*</span>
              </label>
              <input
                type="number"
                id="price_per_liter"
                name="price_per_liter"
                value={formData.price_per_liter}
                onChange={handleChange}
                placeholder="600.00"
                min="0"
                step="0.01"
                required
              />
            </div>

            {/* Teljes költség */}
            <div className="form-group">
              <label htmlFor="total_cost">
                Teljes költség (Ft) <span className="required">*</span>
              </label>
              <input
                type="number"
                id="total_cost"
                name="total_cost"
                value={formData.total_cost}
                onChange={handleChange}
                placeholder="30000.00"
                min="0"
                step="0.01"
                required
              />
            </div>

            {/* Helyszín */}
            <div className="form-group">
              <label htmlFor="location">Helyszín (benzinkút)</label>
              <input
                type="text"
                id="location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="MOL Kútnál"
              />
            </div>

            {/* Számla szám */}
            <div className="form-group">
              <label htmlFor="invoice_number">Számla szám</label>
              <input
                type="text"
                id="invoice_number"
                name="invoice_number"
                value={formData.invoice_number}
                onChange={handleChange}
                placeholder="INV-2024-001"
              />
            </div>

            {/* Rögzítő munkatárs */}
            <div className="form-group">
              <label htmlFor="recorded_by_employee_id">
                Rögzítő munkatárs ID
              </label>
              <input
                type="number"
                id="recorded_by_employee_id"
                name="recorded_by_employee_id"
                value={formData.recorded_by_employee_id}
                onChange={handleChange}
                placeholder="1"
                min="1"
              />
            </div>
          </div>

          {/* Tele tank */}
          <div className="form-group-full">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="full_tank"
                checked={formData.full_tank}
                onChange={handleChange}
              />
              Teletankolás
            </label>
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
              placeholder="Autópályán tankoltam..."
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
            <button
              type="submit"
              className="btn-save"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Mentés...' : isEditing ? 'Frissítés' : 'Rögzítés'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
