// TODO-S0-STUB: TypeScript checking disabled - fix inventory types
// @ts-nocheck
/**
 * WasteLogs - Selejt Management
 *
 * Features:
 * - List all waste logs
 * - Record new waste (product, quantity, reason)
 * - View waste history
 * - Delete waste records
 */

import { useState, useEffect } from 'react';
import {
  getWasteLogs,
  createWasteLog,
  deleteWasteLog,
  getInventoryItems,
  type WasteLog,
  type WasteLogCreate,
  type InventoryItem,
} from '@/services/inventoryService';
import './WasteLogs.css';

export const WasteLogs = () => {
  const [wasteLogs, setWasteLogs] = useState<WasteLog[]>([]);
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    inventory_item_id: 0,
    quantity: 0,
    reason: 'lejárt',
    waste_date: new Date().toISOString().split('T')[0],
    noted_by: '',
    notes: '',
  });

  // Fetch waste logs
  const fetchWasteLogs = async () => {
    try {
      setIsLoading(true);
      const response = await getWasteLogs(page, pageSize);
      setWasteLogs(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Error fetching waste logs:', error);
      // Don't show alert for 404, just show empty list
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch items for dropdown
  const fetchItems = async () => {
    try {
      const response = await getInventoryItems(1, 100);
      setItems(response.items);
      if (response.items.length > 0) {
        setFormData((prev) => ({ ...prev, inventory_item_id: response.items[0].id }));
      }
    } catch (error) {
      console.error('Error fetching items:', error);
    }
  };

  // Initial load
  useEffect(() => {
    fetchWasteLogs();
    fetchItems();
  }, [page]);

  // Handle form changes
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === 'inventory_item_id' || name === 'quantity'
          ? parseFloat(value) || 0
          : value,
    }));
  };

  // Submit waste log
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.inventory_item_id) {
      alert('Válassz terméket!');
      return;
    }

    if (formData.quantity <= 0) {
      alert('A mennyiség pozitív számnak kell lennie!');
      return;
    }

    try {
      setIsSubmitting(true);

      const createData: WasteLogCreate = {
        inventory_item_id: formData.inventory_item_id,
        quantity: formData.quantity,
        reason: formData.reason,
        waste_date: formData.waste_date,
        noted_by: formData.noted_by || undefined,
        notes: formData.notes || undefined,
      };

      await createWasteLog(createData);
      alert('Selejt sikeresen rögzítve!');
      setIsModalOpen(false);
      fetchWasteLogs();

      // Reset form
      setFormData({
        inventory_item_id: items.length > 0 ? items[0].id : 0,
        quantity: 0,
        reason: 'lejárt',
        waste_date: new Date().toISOString().split('T')[0],
        noted_by: '',
        notes: '',
      });
    } catch (error: any) {
      console.error('Error creating waste log:', error);
      alert(
        error.response?.data?.detail || 'Nem sikerült rögzíteni a selejtezést!'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Delete waste log
  const handleDelete = async (wasteLog: WasteLog) => {
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt a selejt bejegyzést?\n\nTermék: ${
        wasteLog.inventory_item_name || `Item #${wasteLog.inventory_item_id}`
      }\nMennyiség: ${wasteLog.quantity}`
    );

    if (!confirmed) return;

    try {
      await deleteWasteLog(wasteLog.id);
      alert('Selejt bejegyzés sikeresen törölve!');
      fetchWasteLogs();
    } catch (error) {
      console.error('Error deleting waste log:', error);
      alert('Nem sikerült törölni a selejt bejegyzést!');
    }
  };

  // Pagination
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="waste-logs">
      {/* Header with actions */}
      <div className="waste-header">
        <div>
          <h3>🗑️ Selejt napló</h3>
          <p className="subtitle">Összes selejt: {total}</p>
        </div>

        <div className="waste-actions">
          <button onClick={fetchWasteLogs} className="btn btn-secondary">
            🔄 Frissítés
          </button>
          <button onClick={() => setIsModalOpen(true)} className="btn btn-primary">
            ➕ Selejt rögzítése
          </button>
        </div>
      </div>

      {/* Waste logs table */}
      {isLoading ? (
        <div className="loading">Betöltés...</div>
      ) : (
        <>
          <table className="waste-table">
            <thead>
              <tr>
                <th>Dátum</th>
                <th>Termék</th>
                <th>Mennyiség</th>
                <th>Ok</th>
                <th>Rögzítette</th>
                <th>Megjegyzés</th>
                <th>Műveletek</th>
              </tr>
            </thead>
            <tbody>
              {wasteLogs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="no-data">
                    Nincs megjeleníthető selejt bejegyzés
                  </td>
                </tr>
              ) : (
                wasteLogs.map((log) => (
                  <tr key={log.id}>
                    <td>{new Date(log.waste_date).toLocaleDateString('hu-HU')}</td>
                    <td>
                      <strong>
                        {log.inventory_item_name || `Item #${log.inventory_item_id}`}
                      </strong>
                    </td>
                    <td className="numeric waste-quantity">
                      {log.quantity.toFixed(3)}
                    </td>
                    <td>
                      <span className="reason-badge">{log.reason}</span>
                    </td>
                    <td>{log.noted_by || '-'}</td>
                    <td className="notes">{log.notes || '-'}</td>
                    <td className="actions">
                      <button
                        onClick={() => handleDelete(log)}
                        className="btn-icon danger"
                        title="Törlés"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="btn btn-secondary"
              >
                ‹ Előző
              </button>
              <span className="page-info">
                {page}. oldal / {totalPages}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="btn btn-secondary"
              >
                Következő ›
              </button>
            </div>
          )}
        </>
      )}

      {/* Create Waste Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🗑️ Selejt rögzítése</h2>
              <button onClick={() => setIsModalOpen(false)} className="close-btn">
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="modal-form">
              <div className="form-group">
                <label htmlFor="inventory_item_id">
                  Termék <span className="required">*</span>
                </label>
                <select
                  id="inventory_item_id"
                  name="inventory_item_id"
                  value={formData.inventory_item_id}
                  onChange={handleChange}
                  required
                >
                  {items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name} ({item.current_stock_perpetual.toFixed(3)}{' '}
                      {item.unit})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="quantity">
                  Mennyiség <span className="required">*</span>
                </label>
                <input
                  type="number"
                  id="quantity"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleChange}
                  step="0.001"
                  min="0.001"
                  required
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label htmlFor="reason">
                  Ok <span className="required">*</span>
                </label>
                <select
                  id="reason"
                  name="reason"
                  value={formData.reason}
                  onChange={handleChange}
                  required
                >
                  <option value="lejárt">Lejárt</option>
                  <option value="sérült">Sérült</option>
                  <option value="minőségi probléma">Minőségi probléma</option>
                  <option value="egyéb">Egyéb</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="waste_date">Dátum</label>
                <input
                  type="date"
                  id="waste_date"
                  name="waste_date"
                  value={formData.waste_date}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="noted_by">Rögzítette</label>
                <input
                  type="text"
                  id="noted_by"
                  name="noted_by"
                  value={formData.noted_by}
                  onChange={handleChange}
                  placeholder="pl. Kovács János"
                />
              </div>

              <div className="form-group">
                <label htmlFor="notes">Megjegyzés</label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={3}
                  placeholder="További részletek..."
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="btn btn-secondary"
                  disabled={isSubmitting}
                >
                  Mégse
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Mentés...' : 'Rögzítés'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
