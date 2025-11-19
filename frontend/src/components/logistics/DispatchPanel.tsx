/**
 * DispatchPanel - Diszpécser panel (Várakozó rendelések + Futár hozzárendelés)
 *
 * Funkciók:
 *   - Várakozó kiszállítási rendelések listázása (order_type=Kiszállítás)
 *   - Csak NYITOTT vagy FELDOLGOZVA státuszú rendelések, amiknek nincs futárjuk
 *   - Elérhető futárok listája
 *   - Futár hozzárendelése rendeléshez (POST /api/logistics/couriers/{id}/assign-order)
 *   - Automatikus frissítés
 */

import { useState, useEffect } from 'react';
import apiClient from '@/services/api';
import { getAvailableCouriers, assignCourierToOrder } from '@/services/logisticsService';
import type { Order } from '@/types/payment';
import type { Courier } from '@/types/logistics';
import './DispatchPanel.css';

export const DispatchPanel = () => {
  const [pendingOrders, setPendingOrders] = useState<Order[]>([]);
  const [availableCouriers, setAvailableCouriers] = useState<Courier[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAssigning, setIsAssigning] = useState(false);

  // Várakozó rendelések betöltése
  const fetchPendingOrders = async () => {
    try {
      // Kérjük le a kiszállítási rendeléseket (order_type=Kiszállítás)
      // Amik NYITOTT vagy FELDOLGOZVA státuszúak
      const response = await apiClient.get<{ items: Order[]; total: number }>(
        '/api/orders',
        {
          params: {
            page: 1,
            page_size: 50,
            // order_type: 'Kiszállítás', // Ha a backend támogatja ezt a filtert
            // status: 'NYITOTT,FELDOLGOZVA', // Ha a backend támogatja ezt a filtert
          },
        }
      );

      // Szűrés frontend oldalon: csak Kiszállítás típusú, NYITOTT vagy FELDOLGOZVA státuszú rendelések
      const filtered = response.data.items.filter(
        (order) =>
          order.order_type === 'Kiszállítás' &&
          (order.status === 'NYITOTT' || order.status === 'FELDOLGOZVA')
      );

      setPendingOrders(filtered);
    } catch (error) {
      console.error('Hiba a várakozó rendelések betöltésekor:', error);
      alert('Nem sikerült betölteni a várakozó rendeléseket!');
    }
  };

  // Elérhető futárok betöltése
  const fetchAvailableCouriers = async () => {
    try {
      const couriers = await getAvailableCouriers();
      setAvailableCouriers(couriers);
    } catch (error) {
      console.error('Hiba az elérhető futárok betöltésekor:', error);
      alert('Nem sikerült betölteni az elérhető futárokat!');
    }
  };

  // Adatok betöltése
  const loadData = async () => {
    setIsLoading(true);
    await Promise.all([fetchPendingOrders(), fetchAvailableCouriers()]);
    setIsLoading(false);
  };

  // Első betöltés
  useEffect(() => {
    loadData();

    // Automatikus frissítés 30 másodpercenként
    const interval = setInterval(() => {
      loadData();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // Futár hozzárendelése rendeléshez
  const handleAssignCourier = async (orderId: number, courierId: number) => {
    const confirmed = window.confirm(
      `Biztosan hozzárendeled ezt a futárt a #${orderId} rendeléshez?`
    );

    if (!confirmed) return;

    setIsAssigning(true);

    try {
      await assignCourierToOrder(courierId, orderId);
      alert(`Futár sikeresen hozzárendelve a #${orderId} rendeléshez!`);
      loadData(); // Lista frissítése
    } catch (error: any) {
      console.error('Hiba a futár hozzárendelésekor:', error);
      const errorMessage =
        error?.response?.data?.detail || 'Nem sikerült hozzárendelni a futárt!';
      alert(errorMessage);
    } finally {
      setIsAssigning(false);
    }
  };

  // Ár formázása
  const formatPrice = (price: number | null): string => {
    if (price === null) return '-';
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  // Dátum formázása
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleString('hu-HU');
  };

  // Státusz badge class
  const getStatusBadgeClass = (status: string): string => {
    switch (status) {
      case 'NYITOTT':
        return 'status-open';
      case 'FELDOLGOZVA':
        return 'status-processing';
      default:
        return '';
    }
  };

  return (
    <div className="dispatch-panel">
      {/* Fejléc */}
      <header className="panel-header">
        <h2>📦 Diszpécser - Várakozó rendelések</h2>
        <button onClick={loadData} className="refresh-btn" disabled={isLoading}>
          🔄 Frissítés
        </button>
      </header>

      {/* Töltés állapot */}
      {isLoading ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <div className="dispatch-content">
          {/* Bal oldal: Várakozó rendelések */}
          <section className="pending-orders-section">
            <h3>📋 Várakozó kiszállítások ({pendingOrders.length})</h3>

            {pendingOrders.length === 0 ? (
              <div className="empty-state">
                <p>Jelenleg nincsenek várakozó kiszállítási rendelések.</p>
              </div>
            ) : (
              <div className="orders-list">
                {pendingOrders.map((order) => (
                  <div key={order.id} className="order-card">
                    <div className="order-header">
                      <span className="order-id">Rendelés #{order.id}</span>
                      <span className={`status-badge ${getStatusBadgeClass(order.status)}`}>
                        {order.status}
                      </span>
                    </div>
                    <div className="order-info">
                      <p>
                        <strong>Típus:</strong> {order.order_type}
                      </p>
                      <p>
                        <strong>Összeg:</strong> {formatPrice(order.total_amount)}
                      </p>
                      <p>
                        <strong>Létrehozva:</strong> {formatDate(order.created_at)}
                      </p>
                    </div>

                    {/* Futár hozzárendelése */}
                    <div className="assign-section">
                      <label htmlFor={`courier-select-${order.id}`}>Futár kiválasztása:</label>
                      <div className="assign-controls">
                        <select
                          id={`courier-select-${order.id}`}
                          className="courier-select"
                          disabled={isAssigning || availableCouriers.length === 0}
                          onChange={(e) => {
                            const courierId = parseInt(e.target.value);
                            if (courierId) {
                              handleAssignCourier(order.id, courierId);
                              e.target.value = ''; // Reset select
                            }
                          }}
                        >
                          <option value="">
                            {availableCouriers.length === 0
                              ? 'Nincs elérhető futár'
                              : 'Válassz futárt...'}
                          </option>
                          {availableCouriers.map((courier) => (
                            <option key={courier.id} value={courier.id}>
                              {courier.courier_name} ({courier.phone})
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Jobb oldal: Elérhető futárok */}
          <aside className="available-couriers-section">
            <h3>👷 Elérhető futárok ({availableCouriers.length})</h3>

            {availableCouriers.length === 0 ? (
              <div className="empty-state">
                <p>Jelenleg nincsenek elérhető futárok.</p>
                <p className="hint">
                  (Csak az "Elérhető" státuszú futárok jelennek meg itt)
                </p>
              </div>
            ) : (
              <div className="couriers-list">
                {availableCouriers.map((courier) => (
                  <div key={courier.id} className="courier-card">
                    <div className="courier-header">
                      <strong>{courier.courier_name}</strong>
                      <span className="status-badge status-available">Elérhető</span>
                    </div>
                    <div className="courier-info">
                      <p>📞 {courier.phone}</p>
                      {courier.email && <p>✉️ {courier.email}</p>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  );
};
