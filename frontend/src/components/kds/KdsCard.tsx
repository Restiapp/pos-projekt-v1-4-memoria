/**
 * KdsCard - Egyetlen KDS tétel kártyája
 * Megjeleníti a terméket és státuszváltó gombokat
 */

import { useState } from 'react';
import type { KdsItem, KdsStatus } from '@/types/kds';
import { updateItemStatus } from '@/services/kdsService';
import './KdsCard.css';

interface KdsCardProps {
  item: KdsItem;
  onStatusChange?: () => void; // Callback státusz változás után
}

export const KdsCard = ({ item, onStatusChange }: KdsCardProps) => {
  const [isUpdating, setIsUpdating] = useState(false);

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
      case 'PENDING':
        return 'status-pending';
      case 'PREPARING':
        return 'status-preparing';
      case 'READY':
        return 'status-ready';
      default:
        return '';
    }
  };

  // Státusz magyar megjelenítése
  const getStatusLabel = () => {
    switch (item.kds_status) {
      case 'PENDING':
        return 'Várakozik';
      case 'PREPARING':
        return 'Készül';
      case 'READY':
        return 'Kész';
      default:
        return item.kds_status;
    }
  };

  // Időbélyeg formázása (pl. "14:32")
  const formatTime = (isoDate: string) => {
    const date = new Date(isoDate);
    return date.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`kds-card ${getStatusClass()}`}>
      {/* Fejléc: Asztalszám + Rendelésszám */}
      <div className="kds-card-header">
        <span className="table-number">{item.table_number || 'N/A'}</span>
        <span className="order-id">#{item.order_id}</span>
      </div>

      {/* Termék neve + mennyiség */}
      <div className="kds-card-body">
        <h3 className="product-name">{item.product_name}</h3>
        <p className="quantity">Mennyiség: {item.quantity}x</p>
        {item.notes && <p className="notes">📝 {item.notes}</p>}
      </div>

      {/* Státusz + Időbélyeg */}
      <div className="kds-card-status">
        <span className="status-label">{getStatusLabel()}</span>
        <span className="timestamp">{formatTime(item.created_at)}</span>
      </div>

      {/* Akció gombok */}
      <div className="kds-card-actions">
        {item.kds_status === 'PENDING' && (
          <button
            onClick={() => handleStatusChange('PREPARING')}
            disabled={isUpdating}
            className="btn btn-start"
          >
            ▶️ Elkezdeni
          </button>
        )}
        {item.kds_status === 'PREPARING' && (
          <button
            onClick={() => handleStatusChange('READY')}
            disabled={isUpdating}
            className="btn btn-complete"
          >
            ✅ Kész
          </button>
        )}
        {item.kds_status === 'READY' && (
          <div className="btn-placeholder">Kész! ✨</div>
        )}
      </div>
    </div>
  );
};
