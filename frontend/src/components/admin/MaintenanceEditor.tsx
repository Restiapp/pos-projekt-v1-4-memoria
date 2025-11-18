/**
 * MaintenanceEditor - Karbantartás létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új karbantartás létrehozása (POST /api/vehicles/maintenances)
 *   - Meglévő karbantartás szerkesztése (PATCH /api/vehicles/maintenances/{id})
 *   - Validáció (jármű, típus, dátum, leírás kötelező)
 *   - Következő szerviz tervezése
 *   - Modal overlay
 */

import { useState } from 'react';
import { createMaintenance, updateMaintenance } from '@/services/vehicleService';
import type { VehicleMaintenance, VehicleMaintenanceCreate, VehicleMaintenanceUpdate, Vehicle } from '@/types/vehicle';
import './MaintenanceEditor.css';

interface MaintenanceEditorProps {
  maintenance: VehicleMaintenance | null; // null = új, VehicleMaintenance = szerkesztés
  vehicles: Vehicle[];
  onClose: (shouldRefresh: boolean) => void;
}

export const MaintenanceEditor = ({ maintenance, vehicles, onClose }: MaintenanceEditorProps) => {
  const isEditing = !!maintenance;

  // Form állapot
  const [formData, setFormData] = useState({
    vehicle_id: maintenance?.vehicle_id?.toString() || '',
    maintenance_type: maintenance?.maintenance_type || 'REGULAR_SERVICE',
    maintenance_date: maintenance?.maintenance_date || new Date().toISOString().split('T')[0],
    mileage: maintenance?.mileage?.toString() || '',
    description: maintenance?.description || '',
    cost: maintenance?.cost?.toString() || '',
    service_provider: maintenance?.service_provider || '',
    next_maintenance_date: maintenance?.next_maintenance_date || '',
    next_maintenance_mileage: maintenance?.next_maintenance_mileage?.toString() || '',
    invoice_number: maintenance?.invoice_number || '',
    recorded_by_employee_id: maintenance?.recorded_by_employee_id?.toString() || '',
    notes: maintenance?.notes || '',
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
    if (!formData.vehicle_id) {
      alert('A jármű választása kötelező!');
      return;
    }

    if (!formData.maintenance_type) {
      alert('A karbantartás típusa kötelező!');
      return;
    }

    if (!formData.maintenance_date) {
      alert('A karbantartás dátuma kötelező!');
      return;
    }

    if (!formData.description.trim()) {
      alert('A leírás kötelező!');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing) {
        const updateData: VehicleMaintenanceUpdate = {
          maintenance_type: formData.maintenance_type,
          maintenance_date: formData.maintenance_date,
          mileage: formData.mileage ? parseInt(formData.mileage) : null,
          description: formData.description.trim(),
          cost: formData.cost ? parseFloat(formData.cost) : null,
          service_provider: formData.service_provider.trim() || null,
          next_maintenance_date: formData.next_maintenance_date || null,
          next_maintenance_mileage: formData.next_maintenance_mileage
            ? parseInt(formData.next_maintenance_mileage)
            : null,
          invoice_number: formData.invoice_number.trim() || null,
          recorded_by_employee_id: formData.recorded_by_employee_id
            ? parseInt(formData.recorded_by_employee_id)
            : null,
          notes: formData.notes.trim() || null,
        };

        await updateMaintenance(maintenance.id, updateData);
        alert('Karbantartás sikeresen frissítve!');
      } else {
        const createData: VehicleMaintenanceCreate = {
          vehicle_id: parseInt(formData.vehicle_id),
          maintenance_type: formData.maintenance_type,
          maintenance_date: formData.maintenance_date,
          mileage: formData.mileage ? parseInt(formData.mileage) : null,
          description: formData.description.trim(),
          cost: formData.cost ? parseFloat(formData.cost) : null,
          service_provider: formData.service_provider.trim() || null,
          next_maintenance_date: formData.next_maintenance_date || null,
          next_maintenance_mileage: formData.next_maintenance_mileage
            ? parseInt(formData.next_maintenance_mileage)
            : null,
          invoice_number: formData.invoice_number.trim() || null,
          recorded_by_employee_id: formData.recorded_by_employee_id
            ? parseInt(formData.recorded_by_employee_id)
            : null,
          notes: formData.notes.trim() || null,
        };

        await createMaintenance(createData);
        alert('Karbantartás sikeresen rögzítve!');
      }

      onClose(true); // Frissítés szükséges
    } catch (error) {
      console.error('Hiba a karbantartás mentésekor:', error);
      alert('Hiba történt a mentés során!');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={() => onClose(false)}>
      <div className="modal-content maintenance-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditing ? 'Karbantartás szerkesztése' : 'Új karbantartás rögzítése'}</h2>
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

            {/* Karbantartás típusa */}
            <div className="form-group">
              <label htmlFor="maintenance_type">
                Karbantartás típusa <span className="required">*</span>
              </label>
              <select
                id="maintenance_type"
                name="maintenance_type"
                value={formData.maintenance_type}
                onChange={handleChange}
                required
              >
                <option value="REGULAR_SERVICE">Rendszeres szerviz</option>
                <option value="REPAIR">Javítás</option>
                <option value="TIRE_CHANGE">Gumicsere</option>
                <option value="OIL_CHANGE">Olajcsere</option>
                <option value="BRAKE_SERVICE">Fékszerviz</option>
                <option value="MOT">Műszaki vizsga</option>
                <option value="OTHER">Egyéb</option>
              </select>
            </div>

            {/* Karbantartás dátuma */}
            <div className="form-group">
              <label htmlFor="maintenance_date">
                Karbantartás dátuma <span className="required">*</span>
              </label>
              <input
                type="date"
                id="maintenance_date"
                name="maintenance_date"
                value={formData.maintenance_date}
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

            {/* Költség */}
            <div className="form-group">
              <label htmlFor="cost">Költség (Ft)</label>
              <input
                type="number"
                id="cost"
                name="cost"
                value={formData.cost}
                onChange={handleChange}
                placeholder="25000"
                min="0"
                step="0.01"
              />
            </div>

            {/* Szerviz / javítóműhely */}
            <div className="form-group">
              <label htmlFor="service_provider">Szerviz / javítóműhely</label>
              <input
                type="text"
                id="service_provider"
                name="service_provider"
                value={formData.service_provider}
                onChange={handleChange}
                placeholder="AutoSzerviz Kft."
              />
            </div>

            {/* Következő szerviz dátuma */}
            <div className="form-group">
              <label htmlFor="next_maintenance_date">
                Következő szerviz dátuma
              </label>
              <input
                type="date"
                id="next_maintenance_date"
                name="next_maintenance_date"
                value={formData.next_maintenance_date}
                onChange={handleChange}
              />
            </div>

            {/* Következő szerviz km állás */}
            <div className="form-group">
              <label htmlFor="next_maintenance_mileage">
                Következő szerviz km állás
              </label>
              <input
                type="number"
                id="next_maintenance_mileage"
                name="next_maintenance_mileage"
                value={formData.next_maintenance_mileage}
                onChange={handleChange}
                placeholder="60000"
                min="0"
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
                placeholder="SRV-2024-001"
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

          {/* Leírás */}
          <div className="form-group-full">
            <label htmlFor="description">
              Leírás / Munka részletei <span className="required">*</span>
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              placeholder="Olajcsere és szűrőcsere..."
              required
            />
          </div>

          {/* Megjegyzések */}
          <div className="form-group-full">
            <label htmlFor="notes">Megjegyzések</label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={2}
              placeholder="Következő szerviz 10,000 km múlva..."
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
