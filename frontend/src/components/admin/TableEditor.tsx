/**
 * TableEditor - Asztal létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új asztal létrehozása (POST /api/tables)
 *   - Meglévő asztal szerkesztése (PUT /api/tables/{id})
 *   - Validáció (table_number kötelező)
 *   - Modal overlay (háttérre kattintva bezárás)
 *   - Asztal ikon / típus választó
 */

import { useState } from 'react';
import { createTable, updateTable } from '@/services/tableService';
import type { Table, TableCreate, TableUpdate } from '@/types/table';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import { TableCircle, TableSquare, TableFourSeat, TableSixSeat } from '@/components/tables/icons';
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
    shape: (table?.shape || 'rect') as 'rect' | 'round',
    width: table?.width ?? 60,
    height: table?.height ?? 60,
    rotation: table?.rotation ?? 0,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tableType, setTableType] = useState<'circle' | 'square' | 'four-seat' | 'six-seat'>(
    table?.shape === 'round' ? 'circle' : 'square'
  );

  // Form mező változás
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    // Numerikus mezők kezelése (position_x, position_y, capacity, width, height, rotation)
    if (['position_x', 'position_y', 'capacity', 'width', 'height', 'rotation'].includes(name)) {
      setFormData((prev) => ({
        ...prev,
        [name]: value === '' ? '' : parseFloat(value),
      }));
      return;
    }

    // String mezők (table_number)
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Asztal típus kiválasztása
  const handleTableTypeSelect = (type: 'circle' | 'square' | 'four-seat' | 'six-seat') => {
    setTableType(type);

    // Automatically set shape and default dimensions based on type
    const updates: Partial<typeof formData> = {};

    if (type === 'circle') {
      updates.shape = 'round';
      updates.width = 60;
      updates.height = 60;
    } else if (type === 'square') {
      updates.shape = 'rect';
      updates.width = 60;
      updates.height = 60;
    } else if (type === 'four-seat') {
      updates.shape = 'rect';
      updates.width = 80;
      updates.height = 80;
      updates.capacity = 4;
    } else if (type === 'six-seat') {
      updates.shape = 'rect';
      updates.width = 90;
      updates.height = 68;
      updates.capacity = 6;
    }

    setFormData((prev) => ({ ...prev, ...updates }));
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
          shape: formData.shape,
          width: Number(formData.width),
          height: Number(formData.height),
          rotation: Number(formData.rotation),
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
          shape: formData.shape,
          width: Number(formData.width),
          height: Number(formData.height),
          rotation: Number(formData.rotation),
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

          {/* Asztal típus választó */}
          <div className="form-group">
            <label>Asztal típusa</label>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '8px' }}>
              <div
                onClick={() => handleTableTypeSelect('circle')}
                style={{
                  cursor: 'pointer',
                  padding: '10px',
                  border: tableType === 'circle' ? '3px solid #fd7e14' : '2px solid #dee2e6',
                  borderRadius: '8px',
                  backgroundColor: tableType === 'circle' ? '#fff3e0' : '#f8f9fa',
                  transition: 'all 0.2s',
                }}
              >
                <TableCircle selected={tableType === 'circle'} size={50} />
                <div style={{ textAlign: 'center', marginTop: '5px', fontSize: '12px' }}>Kerek</div>
              </div>

              <div
                onClick={() => handleTableTypeSelect('square')}
                style={{
                  cursor: 'pointer',
                  padding: '10px',
                  border: tableType === 'square' ? '3px solid #fd7e14' : '2px solid #dee2e6',
                  borderRadius: '8px',
                  backgroundColor: tableType === 'square' ? '#fff3e0' : '#f8f9fa',
                  transition: 'all 0.2s',
                }}
              >
                <TableSquare selected={tableType === 'square'} size={50} />
                <div style={{ textAlign: 'center', marginTop: '5px', fontSize: '12px' }}>Négyzet</div>
              </div>

              <div
                onClick={() => handleTableTypeSelect('four-seat')}
                style={{
                  cursor: 'pointer',
                  padding: '10px',
                  border: tableType === 'four-seat' ? '3px solid #fd7e14' : '2px solid #dee2e6',
                  borderRadius: '8px',
                  backgroundColor: tableType === 'four-seat' ? '#fff3e0' : '#f8f9fa',
                  transition: 'all 0.2s',
                }}
              >
                <TableFourSeat selected={tableType === 'four-seat'} size={60} />
                <div style={{ textAlign: 'center', marginTop: '5px', fontSize: '12px' }}>4 személyes</div>
              </div>

              <div
                onClick={() => handleTableTypeSelect('six-seat')}
                style={{
                  cursor: 'pointer',
                  padding: '10px',
                  border: tableType === 'six-seat' ? '3px solid #fd7e14' : '2px solid #dee2e6',
                  borderRadius: '8px',
                  backgroundColor: tableType === 'six-seat' ? '#fff3e0' : '#f8f9fa',
                  transition: 'all 0.2s',
                }}
              >
                <TableSixSeat selected={tableType === 'six-seat'} size={65} />
                <div style={{ textAlign: 'center', marginTop: '5px', fontSize: '12px' }}>6 személyes</div>
              </div>
            </div>
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

          {/* Szélesség */}
          <div className="form-group">
            <label htmlFor="width">Szélesség (px)</label>
            <input
              id="width"
              name="width"
              type="number"
              value={formData.width}
              onChange={handleChange}
              placeholder="pl. 60"
              min={20}
              max={300}
              step={5}
            />
            <small className="field-hint">
              Az asztal szélessége pixelben (asztaltérképen)
            </small>
          </div>

          {/* Magasság */}
          <div className="form-group">
            <label htmlFor="height">Magasság (px)</label>
            <input
              id="height"
              name="height"
              type="number"
              value={formData.height}
              onChange={handleChange}
              placeholder="pl. 60"
              min={20}
              max={300}
              step={5}
            />
            <small className="field-hint">
              Az asztal magassága pixelben (asztaltérképen)
            </small>
          </div>

          {/* Forgatás */}
          <div className="form-group">
            <label htmlFor="rotation">Forgatás (°)</label>
            <input
              id="rotation"
              name="rotation"
              type="number"
              value={formData.rotation}
              onChange={handleChange}
              placeholder="pl. 0"
              min={0}
              max={359}
              step={15}
            />
            <small className="field-hint">
              Az asztal elforgatása fokban (0-359)
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
