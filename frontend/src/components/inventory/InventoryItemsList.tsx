/**
 * InventoryItemsList - Raktári tételek listázása
 *
 * Funkciók:
 *   - Raktári tételek táblázatos megjelenítése
 *   - Készlet szintek jelzése (alacsony készlet warning)
 *   - Kategória és keresés szerinti szűrés
 *   - Új tétel létrehozása
 *   - Tétel szerkesztése/törlése
 */

import { useState, useEffect } from 'react';
import { getInventoryItems, deleteInventoryItem } from '@/services/inventoryService';
import type { InventoryItem } from '@/types/inventory';
import './Inventory.css';

export const InventoryItemsList = () => {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Tételek betöltése
  const fetchItems = async () => {
    try {
      setIsLoading(true);
      const data = await getInventoryItems({
        category: categoryFilter || undefined,
        search: searchTerm || undefined,
        limit: 100,
      });
      setItems(data);
    } catch (error) {
      console.error('Hiba a raktári tételek betöltésekor:', error);
      alert('Nem sikerült betölteni a raktári tételeket!');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [categoryFilter, searchTerm]);

  // Tétel törlése
  const handleDelete = async (itemId: number) => {
    if (!confirm('Biztosan törölni szeretnéd ezt a tételt?')) return;

    try {
      await deleteInventoryItem(itemId);
      alert('Tétel sikeresen törölve!');
      fetchItems();
    } catch (error) {
      console.error('Hiba a tétel törlésekor:', error);
      alert('Nem sikerült törölni a tételt!');
    }
  };

  // Ár formázás
  const formatPrice = (price?: number): string => {
    if (price === undefined || price === null) return '-';
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  // Mennyiség formázás
  const formatQuantity = (quantity: number, unit: string): string => {
    return `${quantity.toFixed(2)} ${unit}`;
  };

  // Készlet szint badge
  const getStockLevelBadge = (item: InventoryItem): JSX.Element | null => {
    if (!item.min_stock_level) return null;

    if (item.current_stock <= item.min_stock_level) {
      return <span className="stock-badge stock-low">⚠️ Alacsony</span>;
    }

    if (item.max_stock_level && item.current_stock >= item.max_stock_level) {
      return <span className="stock-badge stock-high">📈 Magas</span>;
    }

    return <span className="stock-badge stock-ok">✅ OK</span>;
  };

  // Kategóriák kinyerése (unique)
  const categories = Array.from(new Set(items.map((item) => item.category).filter(Boolean)));

  return (
    <div className="inventory-items-list">
      {/* Fejléc */}
      <header className="list-header">
        <h2>📦 Raktári tételek</h2>
        <div className="header-controls">
          <input
            type="text"
            placeholder="Keresés név, SKU szerint..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="category-filter"
          >
            <option value="">Összes kategória</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          <button onClick={fetchItems} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && items.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="inventory-table">
              <thead>
                <tr>
                  <th>Azonosító</th>
                  <th>Név</th>
                  <th>SKU</th>
                  <th>Kategória</th>
                  <th>Jelenlegi készlet</th>
                  <th>Min. készlet</th>
                  <th>Max. készlet</th>
                  <th>Egységár</th>
                  <th>Szállító</th>
                  <th>Státusz</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {items.length === 0 ? (
                  <tr>
                    <td colSpan={11} className="empty-state">
                      Nincsenek raktári tételek
                    </td>
                  </tr>
                ) : (
                  items.map((item) => (
                    <tr key={item.id}>
                      <td>#{item.id}</td>
                      <td>{item.name}</td>
                      <td>{item.sku || '-'}</td>
                      <td>{item.category || '-'}</td>
                      <td>{formatQuantity(item.current_stock, item.unit)}</td>
                      <td>{item.min_stock_level ? formatQuantity(item.min_stock_level, item.unit) : '-'}</td>
                      <td>{item.max_stock_level ? formatQuantity(item.max_stock_level, item.unit) : '-'}</td>
                      <td>{formatPrice(item.unit_price)}</td>
                      <td>{item.supplier || '-'}</td>
                      <td>{getStockLevelBadge(item)}</td>
                      <td>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="action-btn delete-btn"
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
          </div>
        </>
      )}
    </div>
  );
};
