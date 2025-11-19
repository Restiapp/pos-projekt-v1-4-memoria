/**
 * KdsCard - Egyetlen KDS tétel kártyája
 * Megjeleníti a terméket és státuszváltó gombokat
 * V2: Magyar státuszok (VÁRAKOZIK, KÉSZÜL, KÉSZ) és eltelt idő megjelenítés
 */

import { useState, useEffect } from 'react';
import { KdsStatus } from '@/types/kds';
import type { KdsItem } from '@/types/kds';
import { updateItemStatus } from '@/services/kdsService';
import './KdsCard.css';

interface KdsCardProps {
  item: KdsItem;
  onStatusChange?: () => void; // Callback státusz változás után
}

export const KdsCard = ({ item, onStatusChange }: KdsCardProps) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [elapsedTime, setElapsedTime] = useState('');

  // Eltelt idő számítása és frissítése
  useEffect(() => {
    const updateElapsedTime = () => {
      const now = new Date();
      const created = new Date(item.created_at);
      const diffMs = now.getTime() - created.getTime();
      const diffMins = Math.floor(diffMs / 60000);

      if (diffMins < 1) {
        setElapsedTime('< 1 perc');
      } else if (diffMins < 60) {
        setElapsedTime(`${diffMins} perc`);
      } else {
        const hours = Math.floor(diffMins / 60);
        const mins = diffMins % 60;
        setElapsedTime(`${hours}ó ${mins}p`);
      }
    };

    updateElapsedTime();
    const interval = setInterval(updateElapsedTime, 30000); // 30 másodpercenként frissítés

    return () => clearInterval(interval);
  }, [item.created_at]);

  const handleStatusChange = async (newStatus: KdsStatus) => {
    if (isUpdating) return;

    try {
      setIsUpdating(true);
      await updateItemStatus(item.id, newStatus);
      if (onStatusChange) {
        onStatusChange();
      }
    } catch (error) {
      console.error('Failed to update KDS status:', error);
      alert('Hiba történt a státusz frissítése közben!');
    } finally {
      setIsUpdating(false);
    }
  };

  // Státusz specifikus CSS osztály
  const getStatusClass = () => {
    switch (item.kds_status) {
      case KdsStatus.VARAKOZIK:
        return 'status-pending';
      case KdsStatus.KESZUL:
        return 'status-preparing';
      case KdsStatus.KESZ:
        return 'status-ready';
      case KdsStatus.KISZOLGALVA:
        return 'status-served';
      default:
        return '';
    }
  };

  // Időbélyeg formázása (pl. "14:32")
  const formatTime = (isoDate: string) => {
    const date = new Date(isoDate);
    return date.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`kds-card ${getStatusClass()}`}>
      {/* Fejléc: Asztalszám + Rendelésszám + Eltelt idő */}
      <div className="kds-card-header">
        <span className="table-number">{item.table_number || 'N/A'}</span>
        <span className="order-id">#{item.order_id}</span>
        <span className="elapsed-time">⏱️ {elapsedTime}</span>
      </div>

      {/* Termék neve + mennyiség */}
      <div className="kds-card-body">
        <h3 className="product-name">{item.product_name}</h3>
        <p className="quantity">Mennyiség: {item.quantity}x</p>
        {item.notes && <p className="notes">📝 {item.notes}</p>}
      </div>

      {/* Státusz + Időbélyeg */}
      <div className="kds-card-status">
        <span className="status-label">{item.kds_status}</span>
        <span className="timestamp">{formatTime(item.created_at)}</span>
      </div>

      {/* Akció gombok */}
      <div className="kds-card-actions">
        {item.kds_status === KdsStatus.VARAKOZIK && (
          <button
            onClick={() => handleStatusChange(KdsStatus.KESZUL)}
            disabled={isUpdating}
            className="btn btn-start"
          >
            ▶️ Elkezdeni
          </button>
        )}
        {item.kds_status === KdsStatus.KESZUL && (
          <button
            onClick={() => handleStatusChange(KdsStatus.KESZ)}
            disabled={isUpdating}
            className="btn btn-complete"
          >
            ✅ Kész
          </button>
        )}
        {item.kds_status === KdsStatus.KESZ && (
          <button
            onClick={() => handleStatusChange(KdsStatus.KISZOLGALVA)}
            disabled={isUpdating}
            className="btn btn-served"
          >
            🍽️ Kiszolgálva
          </button>
        )}
        {item.kds_status === KdsStatus.KISZOLGALVA && (
          <div className="btn-placeholder">Kiszolgálva ✨</div>
        )}
      </div>
    </div>
  );
};
