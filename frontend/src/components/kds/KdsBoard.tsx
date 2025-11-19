/**
 * KdsBoard - Konyhai Kijelző Tábla (Kitchen Display System Board)
 *
 * Feladat B2: KDS UI Frontend komponens
 * - Állomások közötti váltás (fülek)
 * - Rendelési tételek csempékként való megjelenítése
 * - Termék neve, mennyisége, jegyzetek, eltelt idő megjelenítése
 * - Státusz változtatás (VÁRAKOZIK -> KÉSZÜL -> KÉSZ -> KISZOLGÁLVA)
 * - PATCH /api/orders/items/{itemId}/kds-status API hívás
 */

import { useState, useEffect } from 'react';
import { KdsStatus } from '@/types/kds';
import type { KdsItem, KdsStation } from '@/types/kds';
import { getItemsByStation } from '@/services/kdsService';
import { KdsCard } from './KdsCard';
import './KdsBoard.css';

const STATIONS: KdsStation[] = ['KONYHA', 'PIZZA', 'PULT'];
const REFRESH_INTERVAL = 10000; // 10 másodperc

export const KdsBoard = () => {
  const [activeStation, setActiveStation] = useState<KdsStation>('KONYHA');
  const [items, setItems] = useState<KdsItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Aktív állomás adatainak lekérése
  const fetchStationData = async (station: KdsStation) => {
    try {
      setIsLoading(true);
      const data = await getItemsByStation(station);
      setItems(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error(`Error fetching KDS data for station ${station}:`, error);
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés és állomásváltás
  useEffect(() => {
    fetchStationData(activeStation);
  }, [activeStation]);

  // Automatikus frissítés (10 másodpercenként)
  useEffect(() => {
    const interval = setInterval(() => {
      fetchStationData(activeStation);
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, [activeStation]);

  // Kézi frissítés
  const handleManualRefresh = () => {
    fetchStationData(activeStation);
  };

  // Állomás címkéjének meghatározása
  const getStationLabel = (station: KdsStation) => {
    switch (station) {
      case 'KONYHA':
        return '🍳 Forró Konyha';
      case 'PIZZA':
        return '🍕 Pizza Állomás';
      case 'PULT':
        return '🥤 Ital Pult';
      default:
        return station;
    }
  };

  // Utolsó frissítés időpontjának formázása
  const formatLastUpdate = () => {
    if (!lastUpdate) return 'Betöltés...';
    return lastUpdate.toLocaleTimeString('hu-HU');
  };

  // Tételek szűrése státusz szerint
  const varakozikItems = items.filter((item) => item.kds_status === KdsStatus.VARAKOZIK);
  const keszulItems = items.filter((item) => item.kds_status === KdsStatus.KESZUL);
  const keszItems = items.filter((item) => item.kds_status === KdsStatus.KESZ);

  return (
    <div className="kds-board">
      {/* Állomás váltó fülek */}
      <div className="kds-board-tabs">
        {STATIONS.map((station) => (
          <button
            key={station}
            className={`kds-tab ${activeStation === station ? 'active' : ''}`}
            onClick={() => setActiveStation(station)}
          >
            {getStationLabel(station)}
          </button>
        ))}
      </div>

      {/* Vezérlő sáv */}
      <div className="kds-board-controls">
        <div className="station-stats">
          <span className="stat stat-pending">{varakozikItems.length} Várakozik</span>
          <span className="stat stat-preparing">{keszulItems.length} Készül</span>
          <span className="stat stat-ready">{keszItems.length} Kész</span>
        </div>
        <div className="control-buttons">
          <button
            onClick={handleManualRefresh}
            className="refresh-btn"
            disabled={isLoading}
          >
            🔄 Frissítés
          </button>
          <span className="last-update">Utolsó frissítés: {formatLastUpdate()}</span>
        </div>
      </div>

      {/* Tételek csempéi */}
      <div className="kds-board-content">
        {isLoading && items.length === 0 ? (
          <div className="loading-state">
            <p>⏳ Betöltés...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="empty-state">
            <p>✨ Nincs aktív tétel ezen az állomáson</p>
          </div>
        ) : (
          <div className="kds-tiles-grid">
            {items.map((item) => (
              <KdsCard
                key={item.id}
                item={item}
                onStatusChange={() => fetchStationData(activeStation)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
