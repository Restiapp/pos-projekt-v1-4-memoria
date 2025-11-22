/**
 * TakeawayOrders - Displays takeaway orders for the bar
 * Shows orders with order_type = 'Elvitel' that need bar attention
 */

import { useState, useEffect } from 'react';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { Skeleton } from '@/components/ui/Skeleton';
import type { Order } from '@/types/order';
import './TakeawayOrders.css';

const REFRESH_INTERVAL = 15000; // 15 seconds
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';

export const TakeawayOrders = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTakeawayOrders = async () => {
    try {
      setError(null);
      const response = await fetch(
        `${API_BASE_URL}/api/v1/orders?order_type=Elvitel&status=NYITOTT`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch takeaway orders');
      }

      const data = await response.json();
      setOrders(data.items || []);
    } catch (err) {
      console.error('Error fetching takeaway orders:', err);
      setError(err instanceof Error ? err.message : 'Hiba történt');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTakeawayOrders();
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchTakeawayOrders, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (isoDate: string) => {
    const date = new Date(isoDate);
    return date.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit' });
  };

  if (isLoading) {
    return (
      <div className="takeaway-orders">
        <div className="takeaway-section-header">
          <h2>📦 Elviteles Rendelések</h2>
        </div>
        <div className="takeaway-orders-list">
          <Skeleton variant="card" count={2} height={120} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="takeaway-orders">
        <div className="takeaway-section-header">
          <h2>📦 Elviteles Rendelések</h2>
        </div>
        <div className="takeaway-error">
          <p>⚠️ {error}</p>
          <button onClick={fetchTakeawayOrders} className="retry-btn">
            🔄 Újrapróbálás
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="takeaway-orders">
      <div className="takeaway-section-header">
        <h2>📦 Elviteles Rendelések</h2>
        <span className="order-count">{orders.length} rendelés</span>
      </div>
      <div className="takeaway-orders-list">
        {orders.length === 0 ? (
          <div className="empty-state">
            <p>Nincs elviteles rendelés</p>
          </div>
        ) : (
          orders.map((order) => (
            <ErrorBoundary key={order.id}>
              <div className="takeaway-order-card">
                <div className="order-header">
                  <span className="order-number">#{order.id}</span>
                  <span className="order-time">{formatTime(order.created_at)}</span>
                </div>
                <div className="order-body">
                  <div className="order-status">
                    <span className={`status-badge status-${order.status.toLowerCase()}`}>
                      {order.status}
                    </span>
                  </div>
                  {order.notes && (
                    <div className="order-notes">
                      <span>📝 {order.notes}</span>
                    </div>
                  )}
                  {order.total_amount !== undefined && (
                    <div className="order-total">
                      <strong>{order.total_amount.toLocaleString('hu-HU')} Ft</strong>
                    </div>
                  )}
                </div>
              </div>
            </ErrorBoundary>
          ))
        )}
      </div>
    </div>
  );
};
