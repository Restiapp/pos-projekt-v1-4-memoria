/**
 * InventoryItemEditor - Modal for creating/editing inventory items
 */

import { useState, useEffect } from 'react';
import {
  createInventoryItem,
  updateInventoryItem,
  type InventoryItem,
  type InventoryItemCreate,
  type InventoryItemUpdate,
} from '@/services/inventoryService';
import './InventoryItemEditor.css';

interface InventoryItemEditorProps {
  item: InventoryItem | null;
  onClose: (shouldRefresh: boolean) => void;
}

export const InventoryItemEditor = ({ item, onClose }: InventoryItemEditorProps) => {
  const isEditMode = !!item;

  const [formData, setFormData] = useState({
    name: item?.name || '',
    unit: item?.unit || 'kg',
    current_stock_perpetual: item?.current_stock_perpetual || 0,
    last_cost_per_unit: item?.last_cost_per_unit || 0,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle form field changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'name' || name === 'unit' ? value : parseFloat(value) || 0,
    }));
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert('Az alapanyag neve kötelező!');
      return;
    }

    try {
      setIsSubmitting(true);

      if (isEditMode) {
        // Update existing item
        const updateData: InventoryItemUpdate = {
          name: formData.name,
          unit: formData.unit,
          current_stock_perpetual: formData.current_stock_perpetual,
          last_cost_per_unit: formData.last_cost_per_unit || undefined,
        };
        await updateInventoryItem(item.id, updateData);
        alert('Alapanyag sikeresen frissítve!');
      } else {
        // Create new item
        const createData: InventoryItemCreate = {
          name: formData.name,
          unit: formData.unit,
          current_stock_perpetual: formData.current_stock_perpetual,
          last_cost_per_unit: formData.last_cost_per_unit || undefined,
        };
        await createInventoryItem(createData);
        alert('Alapanyag sikeresen létrehozva!');
      }

      onClose(true); // Close modal and refresh list
    } catch (error: any) {
      console.error('Error saving item:', error);
      alert(
        error.response?.data?.detail ||
          `Nem sikerült ${isEditMode ? 'frissíteni' : 'létrehozni'} az alapanyagot!`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Close on ESC key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose(false);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  return (
    <div className="modal-overlay" onClick={() => onClose(false)}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditMode ? '✏️ Alapanyag szerkesztése' : '➕ Új alapanyag'}</h2>
          <button onClick={() => onClose(false)} className="close-btn">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="name">
              Név <span className="required">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="pl. Liszt, Cukor, Tej"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="unit">
              Mértékegység <span className="required">*</span>
            </label>
            <select id="unit" name="unit" value={formData.unit} onChange={handleChange}>
              <option value="kg">kg (kilogramm)</option>
              <option value="g">g (gramm)</option>
              <option value="liter">liter</option>
              <option value="ml">ml (milliliter)</option>
              <option value="db">db (darab)</option>
              <option value="csomag">csomag</option>
              <option value="doboz">doboz</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="current_stock_perpetual">Jelenlegi készlet</label>
            <input
              type="number"
              id="current_stock_perpetual"
              name="current_stock_perpetual"
              value={formData.current_stock_perpetual}
              onChange={handleChange}
              step="0.001"
              min="0"
            />
          </div>

          <div className="form-group">
            <label htmlFor="last_cost_per_unit">Utolsó egységár (Ft)</label>
            <input
              type="number"
              id="last_cost_per_unit"
              name="last_cost_per_unit"
              value={formData.last_cost_per_unit}
              onChange={handleChange}
              step="0.01"
              min="0"
            />
          </div>

          <div className="modal-actions">
            <button
              type="button"
              onClick={() => onClose(false)}
              className="btn btn-secondary"
              disabled={isSubmitting}
            >
              Mégse
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting
                ? 'Mentés...'
                : isEditMode
                ? 'Frissítés'
                : 'Létrehozás'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
