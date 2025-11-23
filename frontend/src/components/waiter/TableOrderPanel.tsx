/**
 * TableOrderPanel - Waiter-facing order management panel
 *
 * Features:
 * - Display current order for selected table
 * - Round/course management with renaming
 * - Add items to rounds
 * - Empty states and loading states
 * - Error handling with Toast
 * - Visual design per UI_UX_FOUNDATION
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/components/common/Toast';
import { getOrders, createOrder, updateOrder } from '@/services/orderService';
import { addItemToOrder } from '@/services/orderService';
import type { Order } from '@/types/order';
import type { Table } from '@/types/table';
import { Spinner } from '@/components/ui/Spinner';
import './TableOrderPanel.css';

interface OrderItem {
  id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  round_number?: number;
  is_urgent?: boolean;
  kds_status?: string;
  created_at: string;
}

interface RoundData {
  round_number: number;
  label: string;
  items: OrderItem[];
}

interface TableOrderPanelProps {
  table: Table | null;
  onClose?: () => void;
}

export const TableOrderPanel = ({ table, onClose }: TableOrderPanelProps) => {
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [order, setOrder] = useState<Order | null>(null);
  const [orderItems, setOrderItems] = useState<OrderItem[]>([]);
  const [rounds, setRounds] = useState<RoundData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreatingOrder, setIsCreatingOrder] = useState(false);
  const [editingRoundNumber, setEditingRoundNumber] = useState<number | null>(null);
  const [editingRoundLabel, setEditingRoundLabel] = useState('');

  // Load order for the selected table
  const loadOrder = useCallback(async () => {
    if (!table) return;

    setIsLoading(true);
    try {
      const response = await getOrders(1, 100, undefined, 'NYITOTT', table.id);

      if (response.items && response.items.length > 0) {
        const activeOrder = response.items[0];
        setOrder(activeOrder);

        // Load order items (mocked for now - would need API endpoint)
        // In a real implementation, there would be GET /api/orders/{id}/items
        setOrderItems([]);
        organizeRounds([]);
      } else {
        setOrder(null);
        setOrderItems([]);
        setRounds([]);
      }
    } catch (error: any) {
      console.error('Failed to load order:', error);
      showToast('Nem sikerült betölteni a rendelést. Próbáld újra.', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [table, showToast]);

  // Organize items into rounds
  const organizeRounds = (items: OrderItem[]) => {
    const roundMap = new Map<number, OrderItem[]>();
    const roundLabels = (order?.ntak_data as any)?.round_labels || {};

    items.forEach(item => {
      const roundNum = item.round_number || 1;
      if (!roundMap.has(roundNum)) {
        roundMap.set(roundNum, []);
      }
      roundMap.get(roundNum)!.push(item);
    });

    const roundsData: RoundData[] = Array.from(roundMap.entries())
      .sort(([a], [b]) => a - b)
      .map(([roundNumber, roundItems]) => ({
        round_number: roundNumber,
        label: roundLabels[roundNumber] || `${roundNumber}. kör`,
        items: roundItems.sort((a, b) =>
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        ),
      }));

    setRounds(roundsData);
  };

  useEffect(() => {
    loadOrder();
  }, [loadOrder]);

  // Create new order for table
  const handleCreateOrder = async () => {
    if (!table) return;

    setIsCreatingOrder(true);
    try {
      const newOrder = await createOrder({
        order_type: 'Helyben',
        status: 'NYITOTT',
        table_id: table.id,
        total_amount: 0,
        final_vat_rate: 27.0,
      });

      setOrder(newOrder);
      showToast('Új rendelés létrehozva', 'success');
    } catch (error: any) {
      console.error('Failed to create order:', error);
      showToast('Nem sikerült létrehozni a rendelést. Próbáld újra.', 'error');
    } finally {
      setIsCreatingOrder(false);
    }
  };

  // Save round label
  const handleSaveRoundLabel = async (roundNumber: number, newLabel: string) => {
    if (!order) return;

    try {
      const currentMetadata = (order.ntak_data || {}) as any;
      const roundLabels = currentMetadata.round_labels || {};
      roundLabels[roundNumber] = newLabel;

      await updateOrder(order.id, {
        ntak_data: {
          ...currentMetadata,
          round_labels: roundLabels,
        },
      });

      // Update local state
      setRounds(prev =>
        prev.map(r =>
          r.round_number === roundNumber ? { ...r, label: newLabel } : r
        )
      );

      setEditingRoundNumber(null);
      showToast('Kör átnevezve', 'success');
    } catch (error: any) {
      console.error('Failed to update round label:', error);
      showToast('Nem sikerült átnevezni a kört', 'error');
    }
  };

  // Start editing round label
  const startEditingRound = (round: RoundData) => {
    setEditingRoundNumber(round.round_number);
    setEditingRoundLabel(round.label);
  };

  // Cancel editing
  const cancelEditingRound = () => {
    setEditingRoundNumber(null);
    setEditingRoundLabel('');
  };

  // Add items to order
  const handleAddItems = () => {
    if (!table || !order) return;
    navigate(`/orders/new?table_id=${table.id}&order_id=${order.id}`);
  };

  // Format price
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  // Format elapsed time
  const formatElapsedTime = (timestamp: string): string => {
    const elapsed = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Empty state: No table selected
  if (!table) {
    return (
      <div className="table-order-panel">
        <div className="panel-empty-state">
          <div className="empty-state-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" strokeWidth="2" />
              <path d="M9 3v18M15 3v18M3 9h18M3 15h18" strokeWidth="2" />
            </svg>
          </div>
          <h3>Válassz asztalt a térképen</h3>
          <p>Kattints egy asztalra a rendelés kezeléséhez</p>
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="table-order-panel">
        <div className="panel-header">
          <div className="panel-header-info">
            <h2>Asztal {table.table_number}</h2>
            <span className="table-capacity">{table.capacity} fő</span>
          </div>
        </div>
        <div className="panel-loading">
          <Spinner />
          <p>Rendelés betöltése...</p>
        </div>
      </div>
    );
  }

  // Empty state: No active order
  if (!order) {
    return (
      <div className="table-order-panel">
        <div className="panel-header">
          <div className="panel-header-info">
            <h2>Asztal {table.table_number}</h2>
            <span className="table-capacity">{table.capacity} fő</span>
          </div>
          {onClose && (
            <button className="panel-close-btn" onClick={onClose} aria-label="Bezárás">
              ×
            </button>
          )}
        </div>
        <div className="panel-empty-state">
          <div className="empty-state-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" strokeWidth="2" />
              <path d="M12 6v6l4 2" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <h3>Nincs nyitott rendelés</h3>
          <p>Kattints az Új rendelés gombra a rendelés indításához</p>
          <button
            className="btn-primary btn-lg"
            onClick={handleCreateOrder}
            disabled={isCreatingOrder}
          >
            {isCreatingOrder ? 'Létrehozás...' : 'Új rendelés'}
          </button>
        </div>
      </div>
    );
  }

  // Main view: Order with rounds
  return (
    <div className="table-order-panel">
      <div className="panel-header">
        <div className="panel-header-info">
          <h2>Asztal {table.table_number}</h2>
          <span className="table-capacity">{table.capacity} fő</span>
          <span className="order-badge">#{order.id}</span>
        </div>
        {onClose && (
          <button className="panel-close-btn" onClick={onClose} aria-label="Bezárás">
            ×
          </button>
        )}
      </div>

      <div className="panel-actions">
        <button className="btn-primary" onClick={handleAddItems}>
          + Tételek hozzáadása
        </button>
        <button className="btn-secondary" onClick={loadOrder}>
          Frissítés
        </button>
      </div>

      <div className="panel-content">
        {rounds.length === 0 ? (
          <div className="empty-state-small">
            <p>Nincsenek tételek ebben a rendelésben</p>
            <p className="hint">Kattints a "Tételek hozzáadása" gombra</p>
          </div>
        ) : (
          <div className="rounds-container">
            {rounds.map(round => (
              <div key={round.round_number} className="round-card">
                <div className="round-header">
                  {editingRoundNumber === round.round_number ? (
                    <div className="round-label-edit">
                      <input
                        type="text"
                        value={editingRoundLabel}
                        onChange={e => setEditingRoundLabel(e.target.value)}
                        className="round-label-input"
                        autoFocus
                        onKeyDown={e => {
                          if (e.key === 'Enter') {
                            handleSaveRoundLabel(round.round_number, editingRoundLabel);
                          } else if (e.key === 'Escape') {
                            cancelEditingRound();
                          }
                        }}
                      />
                      <button
                        className="btn-icon btn-success"
                        onClick={() => handleSaveRoundLabel(round.round_number, editingRoundLabel)}
                        title="Mentés"
                      >
                        ✓
                      </button>
                      <button
                        className="btn-icon btn-ghost"
                        onClick={cancelEditingRound}
                        title="Mégse"
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <div className="round-label">
                      <h3>{round.label}</h3>
                      <button
                        className="btn-icon btn-ghost"
                        onClick={() => startEditingRound(round)}
                        title="Átnevezés"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>

                {round.items.length === 0 ? (
                  <div className="round-empty">
                    <p>Nincsenek tételek ebben a körben</p>
                  </div>
                ) : (
                  <div className="round-items">
                    {round.items.map(item => (
                      <div
                        key={item.id}
                        className={`order-item ${item.is_urgent ? 'item-urgent' : ''}`}
                      >
                        <div className="item-info">
                          <div className="item-header">
                            <span className="item-name">{item.product_name}</span>
                            {item.is_urgent && (
                              <span className="urgent-badge" title="Sürgős">
                                ⚡
                              </span>
                            )}
                          </div>
                          <div className="item-meta">
                            <span className="item-quantity">{item.quantity}x</span>
                            <span className="item-price">
                              {formatPrice(item.unit_price * item.quantity)}
                            </span>
                            {item.kds_status && (
                              <span className={`kds-status kds-${item.kds_status.toLowerCase()}`}>
                                {item.kds_status}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="panel-footer">
        <div className="order-total">
          <span className="total-label">Összesen:</span>
          <span className="total-amount">{formatPrice(order.total_amount || 0)}</span>
        </div>
        <button className="btn-secondary btn-block">
          Fizetés
        </button>
      </div>
    </div>
  );
};
