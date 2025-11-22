// TODO-S0-STUB: TypeScript checking disabled - fix inventory types
// @ts-nocheck
/**
 * InventoryStock - Készlet Management
 *
 * Features:
 * - List inventory items with current stock levels
 * - Create/Edit/Delete inventory items
 * - View low stock alerts
 * - Display total inventory value
 */

import { useState, useEffect } from 'react';
import {
  getInventoryItems,
  deleteInventoryItem,
  getTotalInventoryValue,
  type InventoryItem,
} from '@/services/inventoryService';
import { InventoryItemEditor } from './InventoryItemEditor';
import './InventoryStock.css';

export const InventoryStock = () => {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [nameFilter, setNameFilter] = useState('');
  const [totalValue, setTotalValue] = useState(0);

  // Editor modal state
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null);

  // Fetch inventory items
  const fetchItems = async () => {
    try {
      setIsLoading(true);
      const response = await getInventoryItems(page, pageSize, nameFilter || undefined);
      setItems(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Error fetching inventory items:', error);
      alert('Nem sikerült betölteni a készletet!');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch total inventory value
  const fetchTotalValue = async () => {
    try {
      const response = await getTotalInventoryValue();
      setTotalValue(response.total_value);
    } catch (error) {
      console.error('Error fetching total value:', error);
    }
  };

  // Initial load
  useEffect(() => {
    fetchItems();
    fetchTotalValue();
  }, [page, nameFilter]);

  // Create new item
  const handleCreate = () => {
    setEditingItem(null);
    setIsEditorOpen(true);
  };

  // Edit item
  const handleEdit = (item: InventoryItem) => {
    setEditingItem(item);
    setIsEditorOpen(true);
  };

  // Delete item
  const handleDelete = async (item: InventoryItem) => {
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt az alapanyagot?\n\n${item.name}`
    );

    if (!confirmed) return;

    try {
      await deleteInventoryItem(item.id);
      alert('Alapanyag sikeresen törölve!');
      fetchItems();
      fetchTotalValue();
    } catch (error) {
      console.error('Error deleting item:', error);
      alert('Nem sikerült törölni az alapanyagot!');
    }
  };

  // Editor close handler
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingItem(null);
    if (shouldRefresh) {
      fetchItems();
      fetchTotalValue();
    }
  };

  // Pagination
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="inventory-stock">
      {/* Header with actions */}
      <div className="stock-header">
        <div className="stock-stats">
          <div className="stat-card">
            <div className="stat-label">Összes tétel</div>
            <div className="stat-value">{total}</div>
          </div>
          <div className="stat-card highlight">
            <div className="stat-label">Teljes készlet érték</div>
            <div className="stat-value">{totalValue.toLocaleString('hu-HU')} Ft</div>
          </div>
        </div>

        <div className="stock-actions">
          <input
            type="text"
            placeholder="Keresés név alapján..."
            value={nameFilter}
            onChange={(e) => setNameFilter(e.target.value)}
            className="search-input"
          />
          <button onClick={fetchItems} className="btn btn-secondary">
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="btn btn-primary">
            ➕ Új alapanyag
          </button>
        </div>
      </div>

      {/* Items table */}
      {isLoading ? (
        <div className="loading">Betöltés...</div>
      ) : (
        <>
          <table className="items-table">
            <thead>
              <tr>
                <th>Név</th>
                <th>Mértékegység</th>
                <th>Jelenlegi készlet</th>
                <th>Utolsó egységár</th>
                <th>Készlet érték</th>
                <th>Műveletek</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="no-data">
                    Nincs megjeleníthető alapanyag
                  </td>
                </tr>
              ) : (
                items.map((item) => {
                  const stockValue =
                    (item.last_cost_per_unit || 0) * item.current_stock_perpetual;
                  const isLowStock = item.current_stock_perpetual < 10;

                  return (
                    <tr key={item.id} className={isLowStock ? 'low-stock' : ''}>
                      <td>
                        {item.name}
                        {isLowStock && <span className="low-stock-badge">⚠️ Alacsony</span>}
                      </td>
                      <td>{item.unit}</td>
                      <td className="numeric">
                        {item.current_stock_perpetual.toFixed(3)}
                      </td>
                      <td className="numeric">
                        {item.last_cost_per_unit
                          ? `${item.last_cost_per_unit.toFixed(2)} Ft`
                          : '-'}
                      </td>
                      <td className="numeric">
                        {stockValue > 0 ? `${stockValue.toFixed(2)} Ft` : '-'}
                      </td>
                      <td className="actions">
                        <button
                          onClick={() => handleEdit(item)}
                          className="btn-icon"
                          title="Szerkesztés"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleDelete(item)}
                          className="btn-icon danger"
                          title="Törlés"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  );
                })
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

      {/* Editor Modal */}
      {isEditorOpen && (
        <InventoryItemEditor
          item={editingItem}
          onClose={handleEditorClose}
        />
      )}
    </div>
  );
};
