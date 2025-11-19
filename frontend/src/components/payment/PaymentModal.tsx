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
import { createInvoice } from '@/services/invoiceService';
import type { InvoiceItem } from '@/types/invoice';
import apiClient from '@/services/api';
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
  const [splitCheck, setSplitCheck] = useState<SplitCheckResponse | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Invoice state
  const [requestInvoice, setRequestInvoice] = useState(false);
  const [customerName, setCustomerName] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');

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
        alert('Hiba történt az adatok betöltése közben!');
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
      alert(`Fizetés rögzítve: ${amount} HUF (${method})`);
    } catch (error: any) {
      console.error('Payment recording failed:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a fizetés rögzítése közben!';
      alert(errorMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  // Rendelés lezárása
  const handleCloseOrder = async () => {
    if (isProcessing) return;
    if (!isFullyPaid) {
      alert('A rendelés még nincs teljesen kifizetve!');
      return;
    }

    // Validate invoice request
    if (requestInvoice && !customerName.trim()) {
      alert('Kérjük, adja meg a vásárló nevét a számlához!');
      return;
    }

    const confirmed = window.confirm(
      'Biztos, hogy lezárod a rendelést? Ez a művelet nem visszavonható.'
    );
    if (!confirmed) return;

    try {
      setIsProcessing(true);

      // Close the order first
      await closeOrder(order.id);

      // Create invoice if requested
      if (requestInvoice) {
        try {
          // Fetch order items for invoice
          const orderItemsResponse = await apiClient.get(
            `/api/order_items/${order.id}/items`
          );
          const orderItems = orderItemsResponse.data;

          // Convert order items to invoice items
          const invoiceItems: InvoiceItem[] = orderItems.map((item: any) => ({
            name: `Termék #${item.product_id}`, // Simplified: use product_id for now
            quantity: item.quantity,
            unit: 'db',
            unit_price: Number(item.unit_price),
            vat_rate: order.final_vat_rate || 27.0,
          }));

          // Create invoice
          const invoiceResponse = await createInvoice({
            order_id: order.id,
            customer_name: customerName,
            customer_email: customerEmail || undefined,
            items: invoiceItems,
            payment_method: 'CASH', // Simplified for now
            notes: `Rendelés #${order.id}`,
          });

          if (invoiceResponse.success) {
            alert(
              `Rendelés sikeresen lezárva!\nSzámla: ${invoiceResponse.invoice_number}\n${invoiceResponse.message || ''}`
            );
          } else {
            alert(
              `Rendelés lezárva, de a számla létrehozása sikertelen:\n${invoiceResponse.message || 'Ismeretlen hiba'}`
            );
          }
        } catch (invoiceError: any) {
          console.error('Invoice creation failed:', invoiceError);
          const errorMsg =
            invoiceError.response?.data?.detail || 'Hiba történt a számla létrehozása közben!';
          alert(`Rendelés lezárva, de a számla létrehozása sikertelen:\n${errorMsg}`);
        }
      } else {
        alert('Rendelés sikeresen lezárva!');
      }

      onPaymentSuccess();
      onClose();
    } catch (error: any) {
      console.error('Order close failed:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a rendelés lezárása közben!';
      alert(errorMsg);
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

            {/* Számla kérése szekció */}
            <div className="invoice-section">
              <h3>📄 Számla</h3>
              <div className="invoice-checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={requestInvoice}
                    onChange={(e) => setRequestInvoice(e.target.checked)}
                    disabled={isProcessing}
                  />
                  <span>Számla kérése</span>
                </label>
              </div>

              {requestInvoice && (
                <div className="invoice-customer-info">
                  <div className="form-group">
                    <label htmlFor="customerName">Vásárló neve *</label>
                    <input
                      id="customerName"
                      type="text"
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                      placeholder="Kovács János"
                      disabled={isProcessing}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="customerEmail">Email (opcionális)</label>
                    <input
                      id="customerEmail"
                      type="email"
                      value={customerEmail}
                      onChange={(e) => setCustomerEmail(e.target.value)}
                      placeholder="kovacs@example.com"
                      disabled={isProcessing}
                    />
                  </div>
                </div>
              )}
            </div>

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
