/**
 * PaymentPage - Fizetési képernyő oldal
 * V3.0 Fázis 5: GlobalHeader integrálva
 *
 * Az URL paraméterből veszi az order_id-t (react-router useParams)
 * Megjeleníti a PaymentModal komponenst
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { getOrderDetails } from '@/services/paymentService';
import { PaymentModal } from '@/components/payment/PaymentModal';
import type { Order } from '@/types/payment';
import './PaymentPage.css';

export const PaymentPage = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrder = async () => {
      if (!orderId) {
        setError('Rendelés azonosító hiányzik!');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        const orderData = await getOrderDetails(parseInt(orderId, 10));
        setOrder(orderData);
      } catch (err: any) {
        console.error('Error fetching order:', err);
        setError(err.response?.data?.detail || 'Hiba történt a rendelés betöltése közben!');
      } finally {
        setIsLoading(false);
      }
    };

    fetchOrder();
  }, [orderId]);

  const handlePaymentSuccess = () => {
    // Navigálás vissza az asztaltérképre vagy dashboard-ra
    navigate('/tables');
  };

  const handleClose = () => {
    navigate('/tables');
  };

  return (
    <div className="payment-page">
      {/* Globális navigációs header */}
      <GlobalHeader currentPage="tables" />

      <main className="page-content">
        {isLoading && <div className="loading-state">Betöltés...</div>}
        {error && (
          <div className="error-state">
            <p>{error}</p>
            <button onClick={() => navigate('/tables')} className="back-btn">
              Vissza az asztaltérképre
            </button>
          </div>
        )}
        {order && (
          <PaymentModal
            order={order}
            onClose={handleClose}
            onPaymentSuccess={handlePaymentSuccess}
          />
        )}
      </main>
    </div>
  );
};
