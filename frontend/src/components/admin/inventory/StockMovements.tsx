/**
 * StockMovements - Készletnapló
 *
 * Features:
 * - List all stock movements (increases/decreases)
 * - Filter by product
 * - Filter by reason (purchase, sale, waste, adjustment)
 * - View movement history
 */

import { useState, useEffect } from 'react';
import {
  getStockMovements,
  getInventoryItems,
  type StockMovement,
  type InventoryItem,
} from '@/services/inventoryService';
import './StockMovements.css';

export const StockMovements = () => {
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Filters
  const [selectedItemId, setSelectedItemId] = useState<number | undefined>(undefined);
  const [selectedReason, setSelectedReason] = useState<string | undefined>(undefined);

  // Fetch movements
  const fetchMovements = async () => {
    try {
      setIsLoading(true);
      const response = await getStockMovements(
        page,
        pageSize,
        selectedItemId,
        selectedReason
      );
      setMovements(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Error fetching movements:', error);
      // Don't show alert for 404, just show empty list
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch items for filter dropdown
  const fetchItems = async () => {
    try {
      const response = await getInventoryItems(1, 100);
      setItems(response.items);
    } catch (error) {
      console.error('Error fetching items:', error);
    }
  };

  // Initial load
  useEffect(() => {
    fetchMovements();
    fetchItems();
  }, [page, selectedItemId, selectedReason]);

  // Reset filters
  const handleResetFilters = () => {
    setSelectedItemId(undefined);
    setSelectedReason(undefined);
    setPage(1);
  };

  // Pagination
  const totalPages = Math.ceil(total / pageSize);

  // Movement type helper
  const getMovementType = (quantityChange: number) => {
    return quantityChange >= 0 ? 'increase' : 'decrease';
  };

  const getMovementIcon = (quantityChange: number) => {
    return quantityChange >= 0 ? '📈' : '📉';
  };

  return (
    <div className="stock-movements">
      {/* Header with filters */}
      <div className="movements-header">
        <div>
          <h3>📊 Készletmozgások</h3>
          <p className="subtitle">Összes mozgás: {total}</p>
        </div>

        <div className="movements-filters">
          <select
            value={selectedItemId || ''}
            onChange={(e) =>
              setSelectedItemId(e.target.value ? parseInt(e.target.value) : undefined)
            }
            className="filter-select"
          >
            <option value="">Minden termék</option>
            {items.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>

          <select
            value={selectedReason || ''}
            onChange={(e) => setSelectedReason(e.target.value || undefined)}
            className="filter-select"
          >
            <option value="">Minden ok</option>
            <option value="purchase">Beszerzés</option>
            <option value="sale">Eladás</option>
            <option value="waste">Selejt</option>
            <option value="adjustment">Korrekció</option>
            <option value="transfer">Átcsoportosítás</option>
          </select>

          <button onClick={handleResetFilters} className="btn btn-secondary">
            🔄 Szűrők törlése
          </button>

          <button onClick={fetchMovements} className="btn btn-secondary">
            ⟳ Frissítés
          </button>
        </div>
      </div>

      {/* Movements table */}
      {isLoading ? (
        <div className="loading">Betöltés...</div>
      ) : (
        <>
          <table className="movements-table">
            <thead>
              <tr>
                <th>Dátum</th>
                <th>Termék</th>
                <th>Mennyiség</th>
                <th>Ok</th>
                <th>Felhasználó</th>
                <th>Megjegyzés</th>
              </tr>
            </thead>
            <tbody>
              {movements.length === 0 ? (
                <tr>
                  <td colSpan={6} className="no-data">
                    Nincs megjeleníthető mozgás
                  </td>
                </tr>
              ) : (
                movements.map((movement) => (
                  <tr
                    key={movement.id}
                    className={getMovementType(movement.quantity_change)}
                  >
                    <td>
                      {new Date(movement.movement_date).toLocaleString('hu-HU')}
                    </td>
                    <td>
                      <strong>
                        {movement.inventory_item_name || `Item #${movement.inventory_item_id}`}
                      </strong>
                    </td>
                    <td className="numeric movement-quantity">
                      {getMovementIcon(movement.quantity_change)}{' '}
                      <span
                        className={
                          movement.quantity_change >= 0 ? 'positive' : 'negative'
                        }
                      >
                        {movement.quantity_change >= 0 ? '+' : ''}
                        {movement.quantity_change.toFixed(3)}
                      </span>
                    </td>
                    <td>
                      <span className="reason-badge">{movement.reason}</span>
                    </td>
                    <td>{movement.user_name || '-'}</td>
                    <td className="notes">{movement.notes || '-'}</td>
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
    </div>
  );
};
