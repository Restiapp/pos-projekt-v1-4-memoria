/**
 * TableOrderPanel - Order panel for guest floor page
 * Displays and manages orders for selected tables
 */

import { useEffect, useState, useMemo } from 'react';
import type { Table } from '@/types/table';
import type { Order, OrderWithItems, OrderItem } from '@/types/order';
import { openOrGetActiveOrder, getOrderWithItems } from '@/services/orderService';
import { useToast } from '@/hooks/useToast';
import { Spinner } from '@/components/ui/Spinner';
import './TableOrderPanel.css';

interface TableOrderPanelProps {
  table: Table | null;
  onOrderUpdated?: (order: Order) => void;
}

interface RoundGroup {
  roundNumber: number;
  items: OrderItem[];
}

export const TableOrderPanel = ({ table, onOrderUpdated }: TableOrderPanelProps) => {
  const toast = useToast();
  const [order, setOrder] = useState<OrderWithItems | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Group items by round_number
  const roundGroups = useMemo<RoundGroup[]>(() => {
    if (!order?.items) return [];

    const groups = new Map<number, OrderItem[]>();

    order.items.forEach((item) => {
      const roundNum = item.round_number ?? 1; // Default to round 1 if not specified
      if (!groups.has(roundNum)) {
        groups.set(roundNum, []);
      }
      groups.get(roundNum)!.push(item);
    });

    // Convert to array and sort by round number
    return Array.from(groups.entries())
      .map(([roundNumber, items]) => ({ roundNumber, items }))
      .sort((a, b) => a.roundNumber - b.roundNumber);
  }, [order]);

  // Load or create order when table changes
  useEffect(() => {
    if (!table) {
      setOrder(null);
      setError(null);
      return;
    }

    const loadOrder = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Open or get active order for this table
        const activeOrder = await openOrGetActiveOrder(table.id);

        // Try to fetch full order details with items
        try {
          const orderWithItems = await getOrderWithItems(activeOrder.id);
          setOrder(orderWithItems);
          onOrderUpdated?.(orderWithItems);
        } catch (err: any) {
          // If items endpoint fails, use the basic order
          console.warn('Failed to fetch order items, using basic order:', err);
          setOrder({ ...activeOrder, items: [] });
          onOrderUpdated?.(activeOrder);
        }
      } catch (err: any) {
        console.error('Failed to load order:', err);
        const errorMessage =
          err.response?.status === 404
            ? 'A rendelés nem található. A backend végpont még nem elérhető.'
            : 'Nem sikerült betölteni a rendelést.';

        setError(errorMessage);
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    loadOrder();
  }, [table]);

  // Render content based on state
  const renderContent = () => {
    if (!table) {
      return (
        <div className="order-panel-empty">
          <p className="order-panel-empty-text">Válassz egy asztalt a rendelés megkezdéséhez.</p>
        </div>
      );
    }

    if (isLoading) {
      return (
        <div className="order-panel-loading">
          <Spinner size="medium" />
          <p>Rendelés betöltése...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="order-panel-error">
          <p className="order-panel-error-text">{error}</p>
          <p className="order-panel-error-hint">
            A backend API még fejlesztés alatt állhat. Ellenőrizd a konzolt további
            részletekért.
          </p>
        </div>
      );
    }

    if (!order) {
      return (
        <div className="order-panel-empty">
          <p className="order-panel-empty-text">Nincs aktív rendelés ehhez az asztalhoz.</p>
        </div>
      );
    }

    return (
      <div className="order-panel-content">
        {/* Order Header */}
        <div className="order-panel-header">
          <h3 className="order-panel-title">Rendelés #{order.id}</h3>
          <div className="order-panel-meta">
            <span className="order-panel-meta-item">
              <strong>Asztal:</strong> {table.table_number}
            </span>
            <span className="order-panel-meta-item">
              <strong>Státusz:</strong> {order.status}
            </span>
            <span className="order-panel-meta-item">
              <strong>Létrehozva:</strong> {new Date(order.created_at).toLocaleString('hu-HU')}
            </span>
          </div>
        </div>

        {/* Order Items by Round */}
        <div className="order-panel-rounds">
          {roundGroups.length === 0 ? (
            <div className="order-panel-no-items">
              <p>Még nincsenek tételek ehhez a rendeléshez.</p>
              <p className="order-panel-hint">
                A tételek hozzáadása a későbbi FE feladatokban kerül implementálásra.
              </p>
            </div>
          ) : (
            roundGroups.map((group) => (
              <div key={group.roundNumber} className="order-panel-round">
                <h4 className="order-panel-round-title">Forduló {group.roundNumber}</h4>
                <div className="order-panel-items">
                  {group.items.map((item) => (
                    <div key={item.id} className="order-panel-item">
                      <div className="order-panel-item-main">
                        <span className="order-panel-item-name">{item.name}</span>
                        <span className="order-panel-item-quantity">x{item.quantity}</span>
                      </div>
                      <div className="order-panel-item-footer">
                        <span className="order-panel-item-price">
                          {item.total_price.toLocaleString('hu-HU')} Ft
                        </span>
                        {item.notes && (
                          <span className="order-panel-item-notes">{item.notes}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Order Total */}
        {order.total_amount !== undefined && order.total_amount > 0 && (
          <div className="order-panel-total">
            <span className="order-panel-total-label">Összesen:</span>
            <span className="order-panel-total-value">
              {order.total_amount.toLocaleString('hu-HU')} Ft
            </span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="order-panel">
      <div className="order-panel-wrapper">{renderContent()}</div>
    </div>
  );
};
