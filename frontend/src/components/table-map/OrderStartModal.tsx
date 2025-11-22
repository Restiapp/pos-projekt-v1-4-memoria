/**
 * OrderStartModal Component
 * Modal for starting a new order from a table
 *
 * Features:
 * - Displays next sequence number with skeleton loader
 * - Auto-refreshes sequence after order creation
 * - Shows toast notifications on errors
 * - Allows selection of order type (Dine-in, Takeout, Delivery)
 */

import { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Skeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/components/common/Toast';
import { getNextSequenceNumber } from '@/services/sequenceService';
import { createOrder } from '@/services/orderService';
import type { Table } from '@/types/table';
import './OrderStartModal.css';

interface OrderStartModalProps {
  isOpen: boolean;
  onClose: () => void;
  table: Table | null;
  onOrderCreated?: (orderId: number) => void;
}

type OrderType = 'Helyben' | 'Elvitel' | 'Kiszállítás';

export const OrderStartModal = ({
  isOpen,
  onClose,
  table,
  onOrderCreated,
}: OrderStartModalProps) => {
  const { showToast } = useToast();
  const [sequenceNumber, setSequenceNumber] = useState<string | null>(null);
  const [isLoadingSequence, setIsLoadingSequence] = useState(false);
  const [isCreatingOrder, setIsCreatingOrder] = useState(false);
  const [orderType, setOrderType] = useState<OrderType>('Helyben');

  // Fetch sequence number when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchSequenceNumber();
    }
  }, [isOpen]);

  const fetchSequenceNumber = async () => {
    setIsLoadingSequence(true);
    try {
      const nextNumber = await getNextSequenceNumber();
      setSequenceNumber(nextNumber);
    } catch (error) {
      console.error('Error fetching sequence number:', error);
      showToast('Nem sikerült betölteni a sorszámot', 'error');
      setSequenceNumber(null);
    } finally {
      setIsLoadingSequence(false);
    }
  };

  const handleCreateOrder = async () => {
    if (!table) {
      showToast('Nincs kiválasztott asztal', 'error');
      return;
    }

    setIsCreatingOrder(true);
    try {
      const orderData = {
        order_type: orderType,
        status: 'NYITOTT' as const,
        table_id: table.id,
        total_amount: 0,
        final_vat_rate: 27.0,
      };

      const newOrder = await createOrder(orderData);

      showToast(
        `Rendelés sikeresen létrehozva! Sorszám: ${newOrder.order_number || 'N/A'}`,
        'success'
      );

      // Auto-refresh sequence number for next order
      await fetchSequenceNumber();

      // Notify parent component
      if (onOrderCreated && newOrder.id) {
        onOrderCreated(newOrder.id);
      }

      // Close modal
      onClose();
    } catch (error) {
      console.error('Error creating order:', error);
      showToast('Nem sikerült létrehozni a rendelést', 'error');
    } finally {
      setIsCreatingOrder(false);
    }
  };

  const handleClose = () => {
    if (!isCreatingOrder) {
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Új Rendelés Indítása"
      maxWidth="500px"
    >
      <div className="order-start-modal">
        {/* Table Information */}
        <div className="modal-section">
          <h3>Asztal</h3>
          {table ? (
            <div className="table-info">
              <span className="table-number">#{table.table_number}</span>
              <span className="table-capacity">
                Kapacitás: {table.capacity} fő
              </span>
            </div>
          ) : (
            <p className="no-table">Nincs kiválasztott asztal</p>
          )}
        </div>

        {/* Sequence Number Display */}
        <div className="modal-section sequence-section">
          <h3>Rendelés Sorszáma</h3>
          {isLoadingSequence ? (
            <Skeleton width="150px" height="40px" />
          ) : sequenceNumber ? (
            <div className="sequence-number">{sequenceNumber}</div>
          ) : (
            <div className="sequence-error">
              <span>Sorszám betöltése sikertelen</span>
              <button
                onClick={fetchSequenceNumber}
                className="retry-btn"
                type="button"
              >
                Újrapróbálkozás
              </button>
            </div>
          )}
        </div>

        {/* Order Type Selection */}
        <div className="modal-section">
          <h3>Rendelés Típusa</h3>
          <div className="order-type-buttons">
            <button
              type="button"
              className={`order-type-btn ${orderType === 'Helyben' ? 'active' : ''}`}
              onClick={() => setOrderType('Helyben')}
            >
              🍽️ Helyben
            </button>
            <button
              type="button"
              className={`order-type-btn ${orderType === 'Elvitel' ? 'active' : ''}`}
              onClick={() => setOrderType('Elvitel')}
            >
              📦 Elvitel
            </button>
            <button
              type="button"
              className={`order-type-btn ${orderType === 'Kiszállítás' ? 'active' : ''}`}
              onClick={() => setOrderType('Kiszállítás')}
            >
              🚚 Kiszállítás
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="modal-actions">
          <button
            onClick={handleClose}
            className="btn btn-secondary"
            disabled={isCreatingOrder}
            type="button"
          >
            Mégse
          </button>
          <button
            onClick={handleCreateOrder}
            className="btn btn-primary"
            disabled={isCreatingOrder || !table || !sequenceNumber}
            type="button"
          >
            {isCreatingOrder ? 'Létrehozás...' : 'Rendelés Indítása'}
          </button>
        </div>
      </div>
    </Modal>
  );
};
