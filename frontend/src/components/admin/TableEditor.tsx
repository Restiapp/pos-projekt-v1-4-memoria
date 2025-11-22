/**
 * TableEditor - Asztal létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új asztal létrehozása (POST /api/tables)
 *   - Meglévő asztal szerkesztése (PUT /api/tables/{id})
 *   - Validáció (table_number kötelező)
 *   - Modal overlay (háttérre kattintva bezárás)
 */

import { useState } from 'react';
import { createTable, updateTable } from '@/services/tableService';
import type { Table, TableCreate, TableUpdate } from '@/types/table';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './TableEditor.css';

interface TableEditorProps {
  table: Table | null; // null = új asztal, Table = szerkesztés
  onClose: (shouldRefresh: boolean) => void;
}

export const TableEditor = ({ table, onClose }: TableEditorProps) => {
  const isEditing = !!table; // true = szerkesztés, false = új létrehozás
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();

  // Form állapot
  const [formData, setFormData] = useState({
    table_number: table?.table_number || '',
    position_x: table?.position_x ?? '',
    position_y: table?.position_y ?? '',
    capacity: table?.capacity ?? '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    // Numerikus mezők kezelése (position_x, position_y, capacity)
    if (['position_x', 'position_y', 'capacity'].includes(name)) {
      setFormData((prev) => ({
        ...prev,
        [name]: value === '' ? '' : parseFloat(value),
      }));
      return;
    }

    // String mezők (table_number)
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Form submit (létrehozás / frissítés)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (!formData.table_number.trim()) {
      showToast('Az asztalszám kötelező!', 'error');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing && table) {
        // Frissítés
        const updateData: TableUpdate = {
          table_number: formData.table_number,
          position_x: formData.position_x === '' ? null : Number(formData.position_x),
          position_y: formData.position_y === '' ? null : Number(formData.position_y),
          capacity: formData.capacity === '' ? null : Number(formData.capacity),
        };
        await updateTable(table.id, updateData);
        showToast('Asztal sikeresen frissítve!', 'success');
      } else {
        // Létrehozás
        const createData: TableCreate = {
          table_number: formData.table_number,
          position_x: formData.position_x === '' ? null : Number(formData.position_x),
          position_y: formData.position_y === '' ? null : Number(formData.position_y),
          capacity: formData.capacity === '' ? null : Number(formData.capacity),
        };
        await createTable(createData);
        showToast('Asztal sikeresen létrehozva!', 'success');
      }

      onClose(true); // Bezárás + lista frissítése
    } catch (error: any) {
      console.error('Hiba az asztal mentésekor:', error);
      const errorMessage =
        error.response?.data?.detail || 'Nem sikerült menteni az asztalt!';
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
          <h2>{isEditing ? '✏️ Asztal szerkesztése' : '➕ Új asztal'}</h2>
          <button onClick={() => onClose(false)} className="close-btn">
            ✕
          </button>
        </header>

        <form onSubmit={handleSubmit} className="table-form">
          {/* Asztalszám */}
          <div className="form-group">
            <label htmlFor="table_number">
              Asztalszám <span className="required">*</span>
            </label>
            <input
              id="table_number"
              name="table_number"
              type="text"
              value={formData.table_number}
              onChange={handleChange}
              placeholder="pl. A1, B2, VIP-01"
              required
              maxLength={50}
            />
          </div>

          {/* Pozíció X */}
          <div className="form-group">
            <label htmlFor="position_x">Pozíció X (px)</label>
            <input
              id="position_x"
              name="position_x"
              type="number"
              value={formData.position_x}
              onChange={handleChange}
              placeholder="pl. 100"
              step={1}
            />
            <small className="field-hint">
              Asztaltérképen való elhelyezés X koordinátája (opcionális)
            </small>
          </div>

          {/* Pozíció Y */}
          <div className="form-group">
            <label htmlFor="position_y">Pozíció Y (px)</label>
            <input
              id="position_y"
              name="position_y"
              type="number"
              value={formData.position_y}
              onChange={handleChange}
              placeholder="pl. 200"
              step={1}
            />
            <small className="field-hint">
              Asztaltérképen való elhelyezés Y koordinátája (opcionális)
            </small>
          </div>

          {/* Kapacitás */}
          <div className="form-group">
            <label htmlFor="capacity">Kapacitás (fő)</label>
            <input
              id="capacity"
              name="capacity"
              type="number"
              value={formData.capacity}
              onChange={handleChange}
              placeholder="pl. 4"
              min={1}
              step={1}
            />
            <small className="field-hint">
              Hány vendég fér el az asztalnál (opcionális)
            </small>
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
