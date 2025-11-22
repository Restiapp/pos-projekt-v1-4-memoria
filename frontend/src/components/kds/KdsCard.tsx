/**
 * KdsCard - Egyetlen KDS tétel kártyája
 * Megjeleníti a terméket és státuszváltó gombokat
 */

import { useState } from 'react';
import type { KdsItem, KdsStatus } from '@/types/kds';
import { updateItemStatus, toggleUrgentFlag } from '@/services/kdsService';
import { useToast } from '@/components/common/Toast';
import { ElapsedTime } from '@/components/common/ElapsedTime';
import { IconAlertCircle } from '@tabler/icons-react';
import './KdsCard.css';

interface KdsCardProps {
  item: KdsItem;
  onStatusChange?: () => void; // Callback státusz változás után
}

export const KdsCard = ({ item, onStatusChange }: KdsCardProps) => {
  const { showToast } = useToast();
  const [isUpdating, setIsUpdating] = useState(false);
  const [isTogglingUrgent, setIsTogglingUrgent] = useState(false);

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
      showToast('Hiba történt a státusz frissítése közben!', 'error');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleToggleUrgent = async () => {
    if (isTogglingUrgent) return;

    try {
      setIsTogglingUrgent(true);
      await toggleUrgentFlag(item.id, !item.is_urgent);
      if (onStatusChange) {
        onStatusChange();
      }
    } catch (error) {
      console.error('Failed to toggle urgent flag:', error);
      showToast('Hiba történt a sürgős jelző váltásakor!', 'error');
    } finally {
      setIsTogglingUrgent(false);
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
      case 'SERVED':
        return 'status-served';
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
      case 'SERVED':
        return 'Kiszolgálva';
      default:
        return item.kds_status;
    }
  };

  // Időbélyeg formázása (pl. "14:32") - Kept for reference, but now using ElapsedTime
  const formatTime = (isoDate: string) => {
    const date = new Date(isoDate);
    return date.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`kds-card ${getStatusClass()} ${item.is_urgent ? 'urgent' : ''}`}>
      {/* Fejléc: Asztalszám + Rendelésszám */}
      <div className="kds-card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="table-number">{item.table_number || 'N/A'}</span>
          {item.is_urgent && (
            <IconAlertCircle
              size={20}
              color="#ff4d4d"
              className="urgent-icon"
            />
          )}
        </div>
        <span className="order-id">#{item.order_id}</span>
      </div>

      {/* Termék neve + mennyiség */}
      <div className="kds-card-body">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <h3 className="product-name" style={{ margin: 0 }}>{item.product_name}</h3>
          {item.course && (
            <span className="course-badge" style={{
              fontSize: '0.75rem',
              padding: '2px 8px',
              borderRadius: '12px',
              backgroundColor: '#f0f0f0',
              color: '#555',
              fontWeight: '500'
            }}>
              {item.course}
            </span>
          )}
        </div>
        <p className="quantity">Mennyiség: {item.quantity}x</p>
        {item.notes && <p className="notes">📝 {item.notes}</p>}
      </div>

      {/* Státusz + Időbélyeg */}
      <div className="kds-card-status">
        <span className="status-label">{getStatusLabel()}</span>
        <ElapsedTime timestamp={item.created_at} />
      </div>

      {/* Akció gombok */}
      <div className="kds-card-actions">
        {item.kds_status === 'PENDING' && (
          <button
            onClick={() => handleStatusChange('PREPARING' as KdsStatus)}
            disabled={isUpdating}
            className="btn btn-start"
          >
            ▶️ Elkezdeni
          </button>
        )}
        {item.kds_status === 'PREPARING' && (
          <button
            onClick={() => handleStatusChange('READY' as KdsStatus)}
            disabled={isUpdating}
            className="btn btn-complete"
          >
            ✅ Kész
          </button>
        )}
        {item.kds_status === 'READY' && (
          <button
            onClick={() => handleStatusChange('SERVED' as KdsStatus)}
            disabled={isUpdating}
            className="btn btn-serve"
          >
            🍽️ Kiszolgálva
          </button>
        )}
        {item.kds_status === 'SERVED' && (
          <div className="btn-placeholder">Kiszolgálva! ✨</div>
        )}
      </div>

      {/* Sürgős jelző gomb (csak nem SERVED státusznál) */}
      {item.kds_status !== 'SERVED' && (
        <div className="kds-card-urgent-toggle" style={{ marginTop: '8px' }}>
          <button
            onClick={handleToggleUrgent}
            disabled={isTogglingUrgent}
            className={`btn btn-urgent-toggle ${item.is_urgent ? 'active' : ''}`}
          >
            {item.is_urgent ? '🔥 Sürgős (kikapcs.)' : '⚠️ Jelölés sürgősnek'}
          </button>
        </div>
      )}
    </div>
  );
};
