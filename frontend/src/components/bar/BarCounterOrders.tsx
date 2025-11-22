/**
 * BarCounterOrders - Displays bar counter orders (PULT station)
 * Shows orders assigned to the bar counter with real-time updates
 */

import { useState, useEffect } from 'react';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { Skeleton } from '@/components/ui/Skeleton';
import { KdsCard } from '@/components/kds/KdsCard';
import { getItemsByStation } from '@/services/kdsService';
import type { KdsItem } from '@/types/kds';
import './BarCounterOrders.css';

const REFRESH_INTERVAL = 12000; // 12 seconds

export const BarCounterOrders = () => {
  const [items, setItems] = useState<KdsItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBarOrders = async () => {
    try {
      setError(null);
      const barItems = await getItemsByStation('PULT');
      setItems(barItems);
    } catch (err) {
      console.error('Error fetching bar counter orders:', err);
      setError(err instanceof Error ? err.message : 'Hiba történt');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBarOrders();
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchBarOrders, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="bar-counter-orders">
        <div className="bar-section-header">
          <h2>🍹 Pult Rendelések</h2>
        </div>
        <div className="bar-orders-list">
          <Skeleton variant="card" count={3} height={200} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bar-counter-orders">
        <div className="bar-section-header">
          <h2>🍹 Pult Rendelések</h2>
        </div>
        <div className="bar-error">
          <p>⚠️ {error}</p>
          <button onClick={fetchBarOrders} className="retry-btn">
            🔄 Újrapróbálás
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bar-counter-orders">
      <div className="bar-section-header">
        <h2>🍹 Pult Rendelések</h2>
        <span className="item-count">{items.length} tétel</span>
      </div>
      <div className="bar-orders-list">
        {items.length === 0 ? (
          <div className="empty-state">
            <p>Nincs aktív rendelés</p>
          </div>
        ) : (
          items.map((item) => (
            <ErrorBoundary key={item.id}>
              <KdsCard item={item} onStatusChange={fetchBarOrders} />
            </ErrorBoundary>
          ))
        )}
      </div>
    </div>
  );
};
