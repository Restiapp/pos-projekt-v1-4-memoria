/**
 * WasteRecordingList - Selejt naplózás és listázás
 *
 * Funkciók:
 *   - Selejt bejegyzések táblázatos megjelenítése
 *   - **SELEJT RÖGZÍTÉSE MODAL** - Új selejt bejegyzés létrehozása
 *   - Szűrés tétel és dátum szerint
 */

import { useState, useEffect } from 'react';
import { getWasteLogs, createWasteLog, getInventoryItems } from '@/services/inventoryService';
import type { WasteLog, WasteLogCreateRequest, InventoryItem } from '@/types/inventory';
import './Inventory.css';

export const WasteRecordingList = () => {
  const [wasteLogs, setWasteLogs] = useState<WasteLog[]>([]);
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [itemFilter, setItemFilter] = useState<string>('');

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState<WasteLogCreateRequest>({
    inventory_item_id: 0,
    quantity: 0,
    reason: 'expired',
    waste_date: new Date().toISOString().split('T')[0],
    noted_by: '',
    notes: '',
  });

  // Selejt naplók és tételek betöltése
  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [wasteData, itemsData] = await Promise.all([
        getWasteLogs({
          inventory_item_id: itemFilter ? parseInt(itemFilter) : undefined,
          limit: 100,
        }),
        getInventoryItems({ limit: 1000 }),
      ]);
      setWasteLogs(wasteData);
      setItems(itemsData);
    } catch (error) {
      console.error('Hiba a selejt adatok betöltésekor:', error);
      alert('Nem sikerült betölteni a selejt adatokat!');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [itemFilter]);

  // Modal megnyitása
  const openModal = () => {
    setFormData({
      inventory_item_id: 0,
      quantity: 0,
      reason: 'expired',
      waste_date: new Date().toISOString().split('T')[0],
      noted_by: '',
      notes: '',
    });
    setIsModalOpen(true);
  };

  // Modal bezárása
  const closeModal = () => {
    setIsModalOpen(false);
  };

  // Form mező frissítése
  const handleInputChange = (
    field: keyof WasteLogCreateRequest,
    value: string | number
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // **SELEJT RÖGZÍTÉSE** - Submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.inventory_item_id === 0) {
      alert('Kérlek válassz egy tételt!');
      return;
    }

    if (formData.quantity <= 0) {
      alert('A mennyiségnek nagyobbnak kell lennie 0-nál!');
      return;
    }

    try {
      await createWasteLog(formData);
      alert('Selejt sikeresen rögzítve!');
      closeModal();
      fetchData();
    } catch (error) {
      console.error('Hiba a selejt rögzítésekor:', error);
      alert('Nem sikerült rögzíteni a selejtezést!');
    }
  };

  // Tétel név lekérése ID alapján
  const getItemName = (itemId: number): string => {
    const item = items.find((i) => i.id === itemId);
    return item ? item.name : `Tétel #${itemId}`;
  };

  // Tétel egység lekérése ID alapján
  const getItemUnit = (itemId: number): string => {
    const item = items.find((i) => i.id === itemId);
    return item ? item.unit : '';
  };

  // Dátum formázás
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('hu-HU');
  };

  // Selejt ok formázás
  const formatReason = (reason: string): string => {
    const reasonMap: Record<string, string> = {
      expired: 'Lejárt',
      damaged: 'Sérült',
      quality_issue: 'Minőségi probléma',
      other: 'Egyéb',
    };
    return reasonMap[reason] || reason;
  };

  return (
    <div className="waste-recording-list">
      {/* Fejléc */}
      <header className="list-header">
        <h2>🗑️ Selejt naplók</h2>
        <div className="header-controls">
          <select
            value={itemFilter}
            onChange={(e) => setItemFilter(e.target.value)}
            className="item-filter"
          >
            <option value="">Összes tétel</option>
            {items.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
          <button onClick={fetchData} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={openModal} className="create-btn">
            ➕ Selejt rögzítése
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && wasteLogs.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="waste-table">
              <thead>
                <tr>
                  <th>Azonosító</th>
                  <th>Tétel</th>
                  <th>Mennyiség</th>
                  <th>Ok</th>
                  <th>Selejtezés dátuma</th>
                  <th>Rögzítette</th>
                  <th>Megjegyzések</th>
                </tr>
              </thead>
              <tbody>
                {wasteLogs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="empty-state">
                      Nincsenek selejt bejegyzések
                    </td>
                  </tr>
                ) : (
                  wasteLogs.map((log) => (
                    <tr key={log.id}>
                      <td>#{log.id}</td>
                      <td>{getItemName(log.inventory_item_id)}</td>
                      <td>
                        {log.quantity.toFixed(2)} {getItemUnit(log.inventory_item_id)}
                      </td>
                      <td>{formatReason(log.reason)}</td>
                      <td>{formatDate(log.waste_date)}</td>
                      <td>{log.noted_by || '-'}</td>
                      <td>{log.notes || '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* **SELEJT RÖGZÍTÉSE MODAL** */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <header className="modal-header">
              <h2>🗑️ Új selejt bejegyzés</h2>
              <button onClick={closeModal} className="modal-close-btn">
                ✕
              </button>
            </header>

            <form onSubmit={handleSubmit} className="waste-form">
              <div className="form-group">
                <label htmlFor="inventory_item_id">Tétel *</label>
                <select
                  id="inventory_item_id"
                  value={formData.inventory_item_id}
                  onChange={(e) => handleInputChange('inventory_item_id', parseInt(e.target.value))}
                  required
                >
                  <option value={0}>-- Válassz tételt --</option>
                  {items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name} (Készlet: {item.current_stock.toFixed(2)} {item.unit})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="quantity">Mennyiség *</label>
                <input
                  type="number"
                  id="quantity"
                  value={formData.quantity}
                  onChange={(e) => handleInputChange('quantity', parseFloat(e.target.value))}
                  min="0.01"
                  step="0.01"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="reason">Ok *</label>
                <select
                  id="reason"
                  value={formData.reason}
                  onChange={(e) => handleInputChange('reason', e.target.value)}
                  required
                >
                  <option value="expired">Lejárt</option>
                  <option value="damaged">Sérült</option>
                  <option value="quality_issue">Minőségi probléma</option>
                  <option value="other">Egyéb</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="waste_date">Selejtezés dátuma *</label>
                <input
                  type="date"
                  id="waste_date"
                  value={formData.waste_date}
                  onChange={(e) => handleInputChange('waste_date', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="noted_by">Rögzítette</label>
                <input
                  type="text"
                  id="noted_by"
                  value={formData.noted_by}
                  onChange={(e) => handleInputChange('noted_by', e.target.value)}
                  placeholder="Például: Nagy János"
                />
              </div>

              <div className="form-group">
                <label htmlFor="notes">Megjegyzések</label>
                <textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  rows={3}
                  placeholder="További információk..."
                />
              </div>

              <footer className="modal-footer">
                <button type="button" onClick={closeModal} className="cancel-btn">
                  Mégse
                </button>
                <button type="submit" className="submit-btn">
                  ✅ Rögzítés
                </button>
              </footer>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
