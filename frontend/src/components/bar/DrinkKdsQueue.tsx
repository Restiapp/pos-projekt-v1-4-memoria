/**
 * DrinkKdsQueue - Drink preparation queue for bar
 * Displays drink orders from all stations with priority sorting
 */

import { useState, useEffect } from 'react';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { Skeleton } from '@/components/ui/Skeleton';
import { KdsCard } from '@/components/kds/KdsCard';
import { getItemsByStation } from '@/services/kdsService';
import type { KdsItem, KdsStation } from '@/types/kds';
import './DrinkKdsQueue.css';

const REFRESH_INTERVAL = 10000; // 10 seconds - faster for drinks
const DRINK_STATIONS: KdsStation[] = ['PULT', 'KONYHA', 'PIZZA'];

export const DrinkKdsQueue = () => {
  const [drinkItems, setDrinkItems] = useState<KdsItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDrinkItems = async () => {
    try {
      setError(null);

      // Fetch from all stations
      const allStationsPromises = DRINK_STATIONS.map((station) =>
        getItemsByStation(station)
      );

      const allStationsResults = await Promise.all(allStationsPromises);

      // Flatten and filter for drink-related items
      // This is a simplified version - you might want to filter by product category
      const allItems = allStationsResults.flat();

      // Sort by created_at (oldest first for FIFO)
      const sortedItems = allItems.sort((a, b) => {
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      });

      setDrinkItems(sortedItems);
    } catch (err) {
      console.error('Error fetching drink queue:', err);
      setError(err instanceof Error ? err.message : 'Hiba történt');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDrinkItems();
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchDrinkItems, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  // Group items by status for better organization
  const groupedItems = {
    pending: drinkItems.filter((item) => item.kds_status === 'PENDING'),
    preparing: drinkItems.filter((item) => item.kds_status === 'PREPARING'),
    ready: drinkItems.filter((item) => item.kds_status === 'READY'),
  };

  if (isLoading) {
    return (
      <div className="drink-kds-queue">
        <div className="drink-queue-header">
          <h2>🥤 Itallap Sor</h2>
        </div>
        <div className="drink-queue-content">
          <Skeleton variant="card" count={4} height={180} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="drink-kds-queue">
        <div className="drink-queue-header">
          <h2>🥤 Itallap Sor</h2>
        </div>
        <div className="drink-queue-error">
          <p>⚠️ {error}</p>
          <button onClick={fetchDrinkItems} className="retry-btn">
            🔄 Újrapróbálás
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="drink-kds-queue">
      <div className="drink-queue-header">
        <h2>🥤 Itallap Sor</h2>
        <div className="queue-stats">
          <span className="stat-badge stat-pending">{groupedItems.pending.length} Várakozik</span>
          <span className="stat-badge stat-preparing">{groupedItems.preparing.length} Készül</span>
          <span className="stat-badge stat-ready">{groupedItems.ready.length} Kész</span>
        </div>
      </div>

      <div className="drink-queue-content">
        {drinkItems.length === 0 ? (
          <div className="empty-state">
            <p>🎉 Nincs függőben lévő ital</p>
          </div>
        ) : (
          <>
            {/* Pending Items - Highest Priority */}
            {groupedItems.pending.length > 0 && (
              <div className="queue-section">
                <h3 className="section-title">⏳ Várakozik ({groupedItems.pending.length})</h3>
                <div className="queue-items">
                  {groupedItems.pending.map((item) => (
                    <ErrorBoundary key={item.id}>
                      <KdsCard item={item} onStatusChange={fetchDrinkItems} />
                    </ErrorBoundary>
                  ))}
                </div>
              </div>
            )}

            {/* Preparing Items */}
            {groupedItems.preparing.length > 0 && (
              <div className="queue-section">
                <h3 className="section-title">🔄 Készül ({groupedItems.preparing.length})</h3>
                <div className="queue-items">
                  {groupedItems.preparing.map((item) => (
                    <ErrorBoundary key={item.id}>
                      <KdsCard item={item} onStatusChange={fetchDrinkItems} />
                    </ErrorBoundary>
                  ))}
                </div>
              </div>
            )}

            {/* Ready Items */}
            {groupedItems.ready.length > 0 && (
              <div className="queue-section">
                <h3 className="section-title">✅ Kész ({groupedItems.ready.length})</h3>
                <div className="queue-items">
                  {groupedItems.ready.map((item) => (
                    <ErrorBoundary key={item.id}>
                      <KdsCard item={item} onStatusChange={fetchDrinkItems} />
                    </ErrorBoundary>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
