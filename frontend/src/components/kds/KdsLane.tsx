/**
 * KdsLane - Egyetlen KDS állomás oszlopa
 * Megjeleníti egy állomáshoz tartozó összes tételt
 */

import type { KdsItem, KdsStation } from '@/types/kds';
import { KdsCard } from './KdsCard';
import './KdsLane.css';

interface KdsLaneProps {
  station: KdsStation;
  items: KdsItem[];
  onRefresh?: () => void; // Callback frissítés kéréshez
}

export const KdsLane = ({ station, items, onRefresh }: KdsLaneProps) => {
  // Állomás címkéjének meghatározása
  const getStationLabel = () => {
    switch (station) {
      case 'KONYHA':
        return '🍳 Konyha';
      case 'PIZZA':
        return '🍕 Pizza';
      case 'PULT':
        return '🥤 Pult';
      default:
        return station;
    }
  };

  // Tételek szűrése státusz szerint (csak aktív tételek, SERVED kiszűrve)
  const activeItems = items.filter((item) => item.kds_status !== 'SERVED');
  const pendingItems = activeItems.filter((item) => item.kds_status === 'PENDING');
  const preparingItems = activeItems.filter((item) => item.kds_status === 'PREPARING');
  const readyItems = activeItems.filter((item) => item.kds_status === 'READY');

  return (
    <div className="kds-lane">
      {/* Fejléc */}
      <div className="kds-lane-header">
        <h2>{getStationLabel()}</h2>
        <div className="lane-stats">
          <span className="stat pending">{pendingItems.length} Várakozik</span>
          <span className="stat preparing">{preparingItems.length} Készül</span>
          <span className="stat ready">{readyItems.length} Kész</span>
        </div>
      </div>

      {/* Tételek listája (csak aktív tételek, SERVED kiszűrve) */}
      <div className="kds-lane-content">
        {activeItems.length === 0 ? (
          <div className="empty-state">
            <p>✨ Nincs aktív tétel</p>
          </div>
        ) : (
          activeItems.map((item) => (
            <KdsCard key={item.id} item={item} onStatusChange={onRefresh} />
          ))
        )}
      </div>
    </div>
  );
};
