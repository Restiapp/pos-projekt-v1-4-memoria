/**
 * DispatchPanel - Futár hozzárendelése rendeléshez
 *
 * V3.0 / LOGISTICS-FIX: Komponens a kiszállítási rendelések futárhoz rendeléséhez.
 *
 * Funkciók:
 *   - Kiszállítási rendelések listázása (futár nélkül)
 *   - Elérhető futárok listázása
 *   - Futár hozzárendelése rendeléshez
 */

import { useState, useEffect } from 'react';
import { getOrders } from '@/services/orderService';
import { getAvailableCouriers } from '@/services/logisticsService';
import { assignCourierToOrder } from '@/services/orderService';
import type { Order } from '@/types/order';
import type { Courier } from '@/types/logistics';
import './DispatchPanel.css';

export const DispatchPanel = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [couriers, setCouriers] = useState<Courier[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Rendelések és futárok betöltése
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Kiszállítási rendelések lekérése (futár nélkül)
      const ordersResponse = await getOrders(1, 100, 'Kiszállítás', 'NYITOTT');
      const ordersWithoutCourier = ordersResponse.items.filter(
        (order) => !order.courier_id
      );
      setOrders(ordersWithoutCourier);

      // Elérhető futárok lekérése
      const availableCouriers = await getAvailableCouriers();
      setCouriers(availableCouriers);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Hiba történt az adatok betöltése során');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignCourier = async (orderId: number, courierId: number) => {
    setError(null);
    setSuccessMessage(null);
    try {
      await assignCourierToOrder(orderId, courierId);
      setSuccessMessage(`Futár sikeresen hozzárendelve a rendeléshez (ID: ${orderId})`);
      // Adatok újratöltése
      await loadData();
      // Sikeres üzenet törlése 3 másodperc után
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Hiba történt a futár hozzárendelése során'
      );
    }
  };

  if (loading) {
    return (
      <div className="dispatch-panel">
        <div className="loading">Betöltés...</div>
      </div>
    );
  }

  return (
    <div className="dispatch-panel">
      <header className="dispatch-header">
        <h2>📦 Kiszállítások Futárhoz Rendelése</h2>
        <button onClick={loadData} className="refresh-btn" title="Frissítés">
          🔄
        </button>
      </header>

      {error && (
        <div className="alert alert-error">
          ❌ {error}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          ✅ {successMessage}
        </div>
      )}

      {orders.length === 0 ? (
        <div className="empty-state">
          <p>📭 Nincs futárra váró kiszállítási rendelés</p>
        </div>
      ) : (
        <div className="dispatch-content">
          <div className="orders-section">
            <h3>Rendelések (futár nélkül)</h3>
            <div className="orders-list">
              {orders.map((order) => (
                <OrderCard
                  key={order.id}
                  order={order}
                  couriers={couriers}
                  onAssign={handleAssignCourier}
                />
              ))}
            </div>
          </div>

          <div className="couriers-section">
            <h3>Elérhető Futárok ({couriers.length})</h3>
            <div className="couriers-list">
              {couriers.length === 0 ? (
                <p className="no-couriers">Nincs elérhető futár</p>
              ) : (
                couriers.map((courier) => (
                  <CourierCard key={courier.id} courier={courier} />
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// =====================================================
// ORDER CARD KOMPONENS
// =====================================================

interface OrderCardProps {
  order: Order;
  couriers: Courier[];
  onAssign: (orderId: number, courierId: number) => void;
}

const OrderCard = ({ order, couriers, onAssign }: OrderCardProps) => {
  const [selectedCourierId, setSelectedCourierId] = useState<number | null>(null);

  const handleAssignClick = () => {
    if (selectedCourierId) {
      onAssign(order.id, selectedCourierId);
      setSelectedCourierId(null);
    }
  };

  // Determine VAT indicator style based on VAT rate
  const vatRate = order.final_vat_rate || 27;
  const vatClass = vatRate === 5 ? 'vat-low' : 'vat-high';
  const vatColor = vatRate === 5 ? '#28a745' : '#ffc107'; // green for 5%, yellow for 27%

  return (
    <div className="order-card">
      <div className="order-header">
        <span className="order-id">#{order.id}</span>
        <span className="order-status">{order.status}</span>
      </div>
      <div className="order-body">
        <p>
          <strong>Típus:</strong> {order.order_type}
        </p>
        <p>
          <strong>Összeg:</strong> {order.total_amount?.toFixed(2) || '0.00'} HUF
        </p>
        <p>
          <strong>ÁFA:</strong>{' '}
          <span
            className={`vat-indicator ${vatClass}`}
            style={{
              backgroundColor: vatColor,
              color: '#000',
              padding: '2px 8px',
              borderRadius: '4px',
              fontWeight: 'bold',
              fontSize: '0.9em',
            }}
          >
            {vatRate}%
          </span>
        </p>
        {order.notes && (
          <p className="order-notes">
            <strong>Megjegyzés:</strong> {order.notes}
          </p>
        )}
      </div>
      <div className="order-actions">
        <select
          value={selectedCourierId || ''}
          onChange={(e) => setSelectedCourierId(Number(e.target.value))}
          className="courier-select"
        >
          <option value="">-- Válassz futárt --</option>
          {couriers.map((courier) => (
            <option key={courier.id} value={courier.id}>
              {courier.courier_name} ({courier.phone})
            </option>
          ))}
        </select>
        <button
          onClick={handleAssignClick}
          disabled={!selectedCourierId}
          className="assign-btn"
        >
          Hozzárendel
        </button>
      </div>
    </div>
  );
};

// =====================================================
// COURIER CARD KOMPONENS
// =====================================================

interface CourierCardProps {
  courier: Courier;
}

const CourierCard = ({ courier }: CourierCardProps) => {
  const statusIcon = {
    available: '✅',
    on_delivery: '🚚',
    offline: '❌',
    break: '☕',
  };

  const statusLabel = {
    available: 'Elérhető',
    on_delivery: 'Úton',
    offline: 'Offline',
    break: 'Szünet',
  };

  return (
    <div className="courier-card">
      <div className="courier-icon">{statusIcon[courier.status]}</div>
      <div className="courier-info">
        <p className="courier-name">{courier.courier_name}</p>
        <p className="courier-phone">{courier.phone}</p>
        <p className="courier-status">
          <span className={`status-badge status-${courier.status}`}>
            {statusLabel[courier.status]}
          </span>
        </p>
      </div>
    </div>
  );
};
