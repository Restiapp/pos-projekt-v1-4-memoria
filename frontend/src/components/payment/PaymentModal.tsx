/**
 * PaymentModal - Fizetési Modal Komponens
 *
 * Funkciók:
 * - Rendelés összegének megjelenítése
 * - Split-Check bontás megjelenítése (személyenként)
 * - Fizetési mód gombok (Készpénz, Bankkártya, SZÉP Kártyák)
 * - Fizetés rögzítése és hátralévő összeg számítása
 * - Rendelés lezárása (ha teljesen kifizetve)
 */

import { useState, useEffect } from 'react';
import type {
  Order,
  Payment,
  PaymentMethod,
  SplitCheckResponse,
} from '@/types/payment';
import {
  getSplitCheck,
  recordPayment,
  closeOrder,
  getPaymentsForOrder,
} from '@/services/paymentService';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './PaymentModal.css';

interface PaymentModalProps {
  order: Order;
  onClose: () => void;
  onPaymentSuccess: () => void; // Callback amikor a fizetés sikeres
}

export const PaymentModal = ({
  order,
  onClose,
  onPaymentSuccess,
}: PaymentModalProps) => {
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();
  const [splitCheck, setSplitCheck] = useState<SplitCheckResponse | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Összes fizetés összege
  const totalPaid = payments.reduce((sum, p) => sum + p.amount, 0);
  // Hátralévő összeg
  const remainingAmount = (order.total_amount || 0) - totalPaid;
  // Teljesen kifizetve?
  const isFullyPaid = remainingAmount <= 0;

  // Kezdeti betöltés: split-check és fizetések
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [splitData, paymentsData] = await Promise.all([
          getSplitCheck(order.id),
          getPaymentsForOrder(order.id),
        ]);
        setSplitCheck(splitData);
        setPayments(paymentsData);
      } catch (error) {
        console.error('Error loading payment data:', error);
        showToast('Hiba történt az adatok betöltése közben!', 'error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [order.id]);

  // Fizetés rögzítése
  const handlePayment = async (method: PaymentMethod, amount: number) => {
    if (isProcessing) return;

    try {
      setIsProcessing(true);
      const payment = await recordPayment(order.id, {
        payment_method: method,
        amount,
      });
      setPayments((prev) => [...prev, payment]);
      showToast(`Fizetés rögzítve: ${amount} HUF (${method})`, 'success');
    } catch (error: any) {
      console.error('Payment recording failed:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a fizetés rögzítése közben!';
      showToast(errorMsg, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  // Rendelés lezárása
  const handleCloseOrder = async () => {
    if (isProcessing) return;
    if (!isFullyPaid) {
      showToast('A rendelés még nincs teljesen kifizetve!', 'error');
      return;
    }

    const confirmed = await showConfirm(
      'Biztos, hogy lezárod a rendelést? Ez a művelet nem visszavonható.'
    );
    if (!confirmed) return;

    try {
      setIsProcessing(true);
      await closeOrder(order.id);
      showToast('Rendelés sikeresen lezárva!', 'success');
      onPaymentSuccess();
      onClose();
    } catch (error: any) {
      console.error('Order close failed:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a rendelés lezárása közben!';
      showToast(errorMsg, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  // Fizetési mód gombok
  const paymentMethods: { label: string; method: PaymentMethod; icon: string }[] = [
    { label: 'Készpénz', method: 'Készpénz', icon: '💵' },
    { label: 'Bankkártya', method: 'Bankkártya', icon: '💳' },
    { label: 'OTP SZÉP', method: 'OTP SZÉP', icon: '🎫' },
    { label: 'K&H SZÉP', method: 'K&H SZÉP', icon: '🎫' },
    { label: 'MKB SZÉP', method: 'MKB SZÉP', icon: '🎫' },
  ];

  return (
    <div className="payment-modal-overlay" onClick={onClose}>
      <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="payment-modal-header">
          <h2>💳 Fizetés - Rendelés #{order.id}</h2>
          <button onClick={onClose} className="close-btn" disabled={isProcessing}>
            ✕
          </button>
        </div>

        {isLoading ? (
          <div className="loading-state">Betöltés...</div>
        ) : (
          <>
            {/* Összegek */}
            <div className="payment-summary">
              <div className="summary-row">
                <span>Teljes összeg:</span>
                <strong>{order.total_amount?.toFixed(2) || '0.00'} HUF</strong>
              </div>
              <div className="summary-row paid">
                <span>Befizetett összeg:</span>
                <strong>{totalPaid.toFixed(2)} HUF</strong>
              </div>
              <div className={`summary-row remaining ${isFullyPaid ? 'completed' : ''}`}>
                <span>Hátralévő összeg:</span>
                <strong>
                  {remainingAmount > 0 ? remainingAmount.toFixed(2) : '0.00'} HUF
                </strong>
              </div>
              {isFullyPaid && (
                <div className="fully-paid-badge">✅ Teljesen kifizetve</div>
              )}
            </div>

            {/* Split-Check bontás */}
            {splitCheck && splitCheck.items.length > 0 && (
              <div className="split-check-section">
                <h3>📊 Számlamegosztás (Split-Check)</h3>
                <div className="split-check-list">
                  {splitCheck.items.map((item, index) => (
                    <div key={index} className="split-check-item">
                      <span className="seat-info">
                        {item.seat_number
                          ? `🪑 Ülés #${item.seat_number}`
                          : '❓ Nem hozzárendelt'}
                      </span>
                      <span className="item-count">{item.item_count} tétel</span>
                      <strong className="person-amount">
                        {item.person_amount.toFixed(2)} HUF
                      </strong>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Fizetési módok */}
            <div className="payment-methods-section">
              <h3>💳 Fizetési módok</h3>
              <div className="payment-methods-grid">
                {paymentMethods.map(({ label, method, icon }) => (
                  <button
                    key={method}
                    onClick={() => handlePayment(method, remainingAmount > 0 ? remainingAmount : 0)}
                    disabled={isProcessing || isFullyPaid}
                    className="payment-method-btn"
                  >
                    <span className="icon">{icon}</span>
                    <span className="label">{label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Fizetési előzmények */}
            {payments.length > 0 && (
              <div className="payment-history-section">
                <h3>📜 Fizetési előzmények</h3>
                <div className="payment-history-list">
                  {payments.map((payment) => (
                    <div key={payment.id} className="payment-history-item">
                      <span className="method">{payment.payment_method}</span>
                      <span className="amount">{payment.amount.toFixed(2)} HUF</span>
                      <span className="timestamp">
                        {new Date(payment.created_at).toLocaleTimeString('hu-HU')}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Rendelés lezárása gomb */}
            <div className="payment-modal-footer">
              <button
                onClick={handleCloseOrder}
                disabled={!isFullyPaid || isProcessing}
                className={`close-order-btn ${isFullyPaid ? 'enabled' : 'disabled'}`}
              >
                {isProcessing ? 'Feldolgozás...' : '✅ Rendelés lezárása'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
