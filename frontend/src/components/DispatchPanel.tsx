/**
 * DispatchPanel - Kiszállítási rendelések kezelése és futár hozzárendelés
 *
 * Funkciók:
 *   - Kiszállítási rendelések listázása
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
  const [deliveryOrders, setDeliveryOrders] = useState<Order[]>([]);
  const [availableCouriers, setAvailableCouriers] = useState<Courier[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [assignmentLoading, setAssignmentLoading] = useState<number | null>(null);

  // Load delivery orders and available couriers
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch delivery orders (Kiszállítás type only)
      const ordersResponse = await getOrders(0, 100, 'Kiszállítás', undefined, undefined);
      setDeliveryOrders(ordersResponse.items);

      // Fetch available couriers
      const couriers = await getAvailableCouriers();
      setAvailableCouriers(couriers);
    } catch (err: any) {
      console.error('Failed to load data:', err);
      setError(err.response?.data?.detail || 'Hiba történt az adatok betöltése során');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignCourier = async (orderId: number, courierId: number) => {
    try {
      setAssignmentLoading(orderId);
      setError(null);

      await assignCourierToOrder(orderId, courierId);

      // Reload data after successful assignment
      await loadData();

      alert('Futár sikeresen hozzárendelve!');
    } catch (err: any) {
      console.error('Failed to assign courier:', err);
      setError(err.response?.data?.detail || 'Hiba történt a futár hozzárendelése során');
      alert(`Hiba: ${err.response?.data?.detail || 'Hiba történt a futár hozzárendelése során'}`);
    } finally {
      setAssignmentLoading(null);
    }
  };

  if (loading) {
    return (
      <div className="dispatch-panel">
        <div className="loading-message">⏳ Adatok betöltése...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dispatch-panel">
        <div className="error-message">
          ❌ {error}
          <button onClick={loadData} className="retry-btn">
            🔄 Újrapróbálás
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dispatch-panel">
      <header className="dispatch-header">
        <h2>📦 Aktív Kiszállítások</h2>
        <button onClick={loadData} className="refresh-btn">
          🔄 Frissítés
        </button>
      </header>

      {deliveryOrders.length === 0 ? (
        <div className="empty-state">
          <p>Nincsenek aktív kiszállítási rendelések</p>
        </div>
      ) : (
        <div className="orders-list">
          {deliveryOrders.map((order) => (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <span className="order-id">Rendelés #{order.id}</span>
                <span className={`order-status status-${order.status.toLowerCase()}`}>
                  {order.status}
                </span>
              </div>

              <div className="order-details">
                <p>
                  <strong>Típus:</strong> {order.order_type}
                </p>
                <p>
                  <strong>Összeg:</strong> {order.total_amount?.toLocaleString('hu-HU') || 0} Ft
                </p>
                <p>
                  <strong>Létrehozva:</strong>{' '}
                  {new Date(order.created_at).toLocaleString('hu-HU')}
                </p>
                {order.notes && (
                  <p>
                    <strong>Megjegyzés:</strong> {order.notes}
                  </p>
                )}
              </div>

              <div className="courier-assignment">
                {order.courier_id ? (
                  <div className="assigned-courier">
                    <span className="courier-label">✅ Hozzárendelt futár:</span>
                    <span className="courier-id">Futár #{order.courier_id}</span>
                  </div>
                ) : (
                  <div className="assign-courier-section">
                    <label htmlFor={`courier-select-${order.id}`}>
                      Futár hozzárendelése:
                    </label>
                    <div className="assign-controls">
                      <select
                        id={`courier-select-${order.id}`}
                        className="courier-select"
                        disabled={assignmentLoading === order.id}
                        onChange={(e) => {
                          const courierId = parseInt(e.target.value);
                          if (courierId) {
                            handleAssignCourier(order.id, courierId);
                          }
                        }}
                        defaultValue=""
                      >
                        <option value="" disabled>
                          Válassz futárt...
                        </option>
                        {availableCouriers.map((courier) => (
                          <option key={courier.id} value={courier.id}>
                            {courier.courier_name} ({courier.phone}) - {courier.status}
                          </option>
                        ))}
                      </select>
                      {assignmentLoading === order.id && (
                        <span className="loading-spinner">⏳</span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {availableCouriers.length === 0 && deliveryOrders.length > 0 && (
        <div className="warning-message">
          ⚠️ Nincsenek elérhető futárok. Kérlek, adj hozzá futárokat a "Futárok" fülön!
        </div>
      )}
    </div>
  );
};
