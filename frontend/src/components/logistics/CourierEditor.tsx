/**
 * CourierEditor - Futár létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új futár létrehozása (POST /api/logistics/couriers)
 *   - Meglévő futár szerkesztése (PUT /api/logistics/couriers/{id})
 *   - Validáció (név, telefon kötelező)
 *   - Modal overlay (háttérre kattintva bezárás)
 */

import { useState } from 'react';
import { createCourier, updateCourier } from '@/services/logisticsService';
import type { Courier, CourierCreate, CourierUpdate, CourierStatus } from '@/types/logistics';
import './CourierEditor.css';

interface CourierEditorProps {
  courier: Courier | null; // null = új futár, Courier = szerkesztés
  onClose: (shouldRefresh: boolean) => void;
}

export const CourierEditor = ({ courier, onClose }: CourierEditorProps) => {
  const isEditing = !!courier; // true = szerkesztés, false = új létrehozás

  // Form állapot
  const [formData, setFormData] = useState({
    courier_name: courier?.courier_name || '',
    phone: courier?.phone || '',
    email: courier?.email || '',
    status: (courier?.status || 'available') as CourierStatus,
    is_active: courier?.is_active ?? true,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    // Checkbox kezelés
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    // String és select mezők
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Form submit (létrehozás / frissítés)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (!formData.courier_name.trim()) {
      alert('A futár neve kötelező!');
      return;
    }

    if (!formData.phone.trim()) {
      alert('A telefon kötelező!');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing && courier) {
        // Frissítés
        const updateData: CourierUpdate = {
          courier_name: formData.courier_name,
          phone: formData.phone,
          email: formData.email || undefined,
          status: formData.status,
          is_active: formData.is_active,
        };
        await updateCourier(courier.id, updateData);
        alert('Futár sikeresen frissítve!');
      } else {
        // Létrehozás
        const createData: CourierCreate = {
          courier_name: formData.courier_name,
          phone: formData.phone,
          email: formData.email || undefined,
          status: formData.status,
          is_active: formData.is_active,
        };
        await createCourier(createData);
        alert('Futár sikeresen létrehozva!');
      }

      onClose(true); // Bezárás + lista frissítése
    } catch (error: any) {
      console.error('Hiba a futár mentésekor:', error);
      const errorMessage =
        error?.response?.data?.detail || 'Nem sikerült menteni a futárt!';
      alert(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Modal bezárása (overlay kattintás)
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content courier-editor-modal">
        {/* Modal fejléc */}
        <header className="modal-header">
          <h2>{isEditing ? '✏️ Futár szerkesztése' : '➕ Új futár létrehozása'}</h2>
          <button onClick={() => onClose(false)} className="close-btn" title="Bezárás">
            ✖
          </button>
        </header>

        {/* Form */}
        <form onSubmit={handleSubmit} className="courier-editor-form">
          {/* Név */}
          <div className="form-group">
            <label htmlFor="courier_name">
              Név <span className="required">*</span>
            </label>
            <input
              type="text"
              id="courier_name"
              name="courier_name"
              value={formData.courier_name}
              onChange={handleChange}
              placeholder="pl. Kiss János"
              required
            />
          </div>

          {/* Telefon */}
          <div className="form-group">
            <label htmlFor="phone">
              Telefon <span className="required">*</span>
            </label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="pl. +36301234567"
              required
            />
          </div>

          {/* Email */}
          <div className="form-group">
            <label htmlFor="email">Email (opcionális)</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="pl. courier@example.com"
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
              <option value="available">Elérhető</option>
              <option value="on_delivery">Úton</option>
              <option value="break">Szünet</option>
              <option value="offline">Offline</option>
            </select>
          </div>

          {/* Aktív */}
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
              />
              Aktív futár
            </label>
          </div>

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
            <button type="submit" className="submit-btn" disabled={isSubmitting}>
              {isSubmitting
                ? 'Mentés...'
                : isEditing
                ? 'Módosítások mentése'
                : 'Futár létrehozása'}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
};
