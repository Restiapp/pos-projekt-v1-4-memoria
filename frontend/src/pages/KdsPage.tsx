/**
 * KdsPage - Konyhai Kijelző Oldal
 * Valós idejű frissítéssel (10 másodpercenként)
 * V3.0 Fázis 5: GlobalHeader integrálva
 */

import { useState, useEffect } from 'react';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { getItemsByStation } from '@/services/kdsService';
import { KdsLane } from '@/components/kds/KdsLane';
import type { KdsItem, KdsStation } from '@/types/kds';
import './KdsPage.css';

const STATIONS: KdsStation[] = ['PULT', 'KONYHA', 'PIZZA'];
const REFRESH_INTERVAL = 10000; // 10 másodperc

export const KdsPage = () => {
  const [items, setItems] = useState<Record<KdsStation, KdsItem[]>>({
    KONYHA: [],
    PIZZA: [],
    PULT: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Összes állomás adatának lekérése
  const fetchAllStations = async () => {
    try {
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
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    fetchAllStations();
  }, []);

  // Automatikus frissítés (10 másodpercenként)
  useEffect(() => {
    const interval = setInterval(() => {
      fetchAllStations();
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  // Kézi frissítés
  const handleManualRefresh = () => {
    setIsLoading(true);
    fetchAllStations();
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

      {/* KDS-specifikus vezérlők */}
      <div className="kds-controls">
        <button onClick={handleManualRefresh} className="refresh-btn" disabled={isLoading}>
          🔄 Frissítés
        </button>
        <span className="last-update">Utolsó frissítés: {formatLastUpdate()}</span>
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
