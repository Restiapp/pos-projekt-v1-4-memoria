/**
 * KdsPage - Konyhai Kijelző Oldal
 * Valós idejű frissítéssel (12 másodpercenként - throttled)
 * V3.0 Fázis 5: GlobalHeader integrálva
 * Sprint 0: Performance optimizations with throttling & error handling
 */

import { useState, useEffect, useMemo } from 'react';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { getItemsByStation } from '@/services/kdsService';
import { KdsLane } from '@/components/kds/KdsLane';
import type { KdsItem, KdsStation } from '@/types/kds';
import { useUrgentAudio } from '@/hooks/useUrgentAudio';
import './KdsPage.css';

const STATIONS: KdsStation[] = ['PULT', 'KONYHA', 'PIZZA'];
const REFRESH_INTERVAL = 12000; // 12 seconds - throttled for performance (Sprint 0)

export const KdsPage = () => {
  const [items, setItems] = useState<Record<KdsStation, KdsItem[]>>({
    KONYHA: [],
    PIZZA: [],
    PULT: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isPolling, setIsPolling] = useState(false); // Loading state for background polls
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null); // Toast error state

  // Flatten all items for urgent audio detection
  const allItems = useMemo(() => {
    return [...items.PULT, ...items.KONYHA, ...items.PIZZA];
  }, [items]);

  // Audio notifications for urgent items
  const { audioEnabled, toggleAudio } = useUrgentAudio(allItems);

  // Összes állomás adatának lekérése (with throttling & error handling)
  const fetchAllStations = async (isBackgroundPoll = false) => {
    try {
      // Set appropriate loading state
      if (isBackgroundPoll) {
        setIsPolling(true);
      } else {
        setIsLoading(true);
      }

      // Clear any previous errors
      setError(null);

      const results = await Promise.all(
        STATIONS.map((station) => getItemsByStation(station))
      );

      const newItems: Record<KdsStation, KdsItem[]> = {
        KONYHA: results[1],
        PIZZA: results[2],
        PULT: results[0],
      };

      setItems(newItems);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching KDS data:', error);

      // Show toast error
      const errorMessage = error instanceof Error
        ? `KDS hiba: ${error.message}`
        : 'Hiba történt az adatok betöltése során';
      setError(errorMessage);

      // Auto-hide toast after 5 seconds
      setTimeout(() => setError(null), 5000);
    } finally {
      setIsLoading(false);
      setIsPolling(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    fetchAllStations();
  }, []);

  // Automatikus frissítés (12 másodpercenként - throttled)
  useEffect(() => {
    const interval = setInterval(() => {
      fetchAllStations(true); // Mark as background poll
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  // Kézi frissítés
  const handleManualRefresh = () => {
    fetchAllStations(false); // Manual refresh, not a background poll
  };

  // Utolsó frissítés időpontjának formázása
  const formatLastUpdate = () => {
    if (!lastUpdate) return 'Betöltés...';
    return lastUpdate.toLocaleTimeString('hu-HU');
  };

  return (
    <div className="kds-page">
      {/* Globális navigációs header */}
      <GlobalHeader currentPage="kds" />

      {/* Toast Error Notification */}
      {error && (
        <div className="toast-error" role="alert">
          ⚠️ {error}
        </div>
      )}

      {/* KDS-specifikus vezérlők */}
      <div className="kds-controls">
        <button onClick={handleManualRefresh} className="refresh-btn" disabled={isLoading}>
          🔄 Frissítés
        </button>
        <button
          onClick={toggleAudio}
          className={`audio-toggle-btn ${audioEnabled ? 'active' : ''}`}
          title={audioEnabled ? 'Hang kikapcsolása' : 'Hang bekapcsolása'}
        >
          {audioEnabled ? '🔊 Hang BE' : '🔇 Hang KI'}
        </button>
        <span className="last-update">
          Utolsó frissítés: {formatLastUpdate()}
          {isPolling && <span className="polling-indicator"> 🔄 Frissítés...</span>}
        </span>
      </div>

      {/* Állomások (oszlopok) */}
      <main className="kds-content">
        {isLoading && items.KONYHA.length === 0 ? (
          <div className="loading-state">Betöltés...</div>
        ) : (
          STATIONS.map((station) => (
            <KdsLane
              key={station}
              station={station}
              items={items[station]}
              onRefresh={fetchAllStations}
            />
          ))
        )}
      </main>
    </div>
  );
};
