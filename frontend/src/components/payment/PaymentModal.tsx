/**
 * PaymentModal - Komplett Fizetési és Kedvezmény Modal Komponens
 *
 * Funkciók:
 * - Rendelés összegének megjelenítése
 * - Split-Check bontás megjelenítése (személyenként)
 * - Fizetési mód gombok (Készpénz, Bankkártya, SZÉP Kártyák)
 * - Manuális split payment (osztott fizetés több tétellel)
 * - Kedvezmény kezelés (kupon, százalék, fix összeg)
 * - Fizetés rögzítése és hátralévő összeg számítása
 * - Számla nyomtatás
 * - NTAK státusz megjelenítés
 * - Rendelés lezárása (ha teljesen kifizetve)
 */

import { useState, useEffect } from 'react';
import type {
  Order,
  Payment,
  PaymentMethod,
  SplitCheckResponse,
  DiscountType,
} from '@/types/payment';
import {
  getSplitCheck,
  recordPayment,
  closeOrder,
  getPaymentsForOrder,
} from '@/services/paymentService';
import {
  applyDiscountToOrder,
  validateCoupon,
  type ApplyOrderDiscountRequest,
} from '@/services/discountService';
import {
  createInvoice,
  type CreateInvoiceRequest,
  type InvoiceItem,
} from '@/services/invoiceService';
import { useAuthStore } from '@/stores/authStore';
import { notify } from '@/utils/notifications';
import './PaymentModal.css';

interface PaymentModalProps {
  order: Order;
  onClose: () => void;
  onPaymentSuccess: () => void;
}

export const PaymentModal = ({
  order,
  onClose,
  onPaymentSuccess,
}: PaymentModalProps) => {
  const { isAuthenticated } = useAuthStore();

  const [splitCheck, setSplitCheck] = useState<SplitCheckResponse | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Kedvezmény state
  const [showDiscountForm, setShowDiscountForm] = useState(false);
  const [discountType, setDiscountType] = useState<DiscountType>('PERCENTAGE');
  const [discountValue, setDiscountValue] = useState<string>('');
  const [couponCode, setCouponCode] = useState<string>('');
  const [discountReason, setDiscountReason] = useState<string>('');

  // Manuális split payment state
  const [showSplitPaymentForm, setShowSplitPaymentForm] = useState(false);
  const [splitPaymentAmount, setSplitPaymentAmount] = useState<string>('');
  const [selectedPaymentMethod, setSelectedPaymentMethod] =
    useState<PaymentMethod>('Készpénz');

  // Számla state
  const [invoiceNumber, setInvoiceNumber] = useState<string | null>(null);

  // Összes fizetés összege
  const totalPaid = payments.reduce((sum, p) => sum + p.amount, 0);
  // Hátralévő összeg
  const remainingAmount = (order.total_amount || 0) - totalPaid;
  // Teljesen kifizetve?
  const isFullyPaid = remainingAmount <= 0;

  // NTAK státusz meghatározása
  const getNTAKStatus = () => {
    if (!order.ntak_data) return { text: 'Nincs NTAK adat', color: 'gray' };

    const hasVatChange = order.ntak_data.vat_change_reason;
    const vatRate = order.final_vat_rate;

    if (hasVatChange && vatRate === 5) {
      return { text: 'NTAK: Helyi 5% ÁFA', color: 'green' };
    } else if (vatRate === 27) {
      return { text: 'NTAK: Normál 27% ÁFA', color: 'blue' };
    }

    return { text: 'NTAK: Feldolgozva', color: 'orange' };
  };

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
        notify.error('Hiba történt az adatok betöltése közben!');
      } finally {
        setIsLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchData();
    }
  }, [isAuthenticated, order.id]);

  // Fizetés rögzítése (quick action - teljes hátralévő összeg)
  const handleQuickPayment = async (method: PaymentMethod) => {
    if (isProcessing || remainingAmount <= 0) return;

    try {
      setIsProcessing(true);
      const payment = await recordPayment(order.id, {
        payment_method: method,
        amount: remainingAmount,
      });
      setPayments((prev) => [...prev, payment]);
<<<<<<< HEAD
      alert(`Fizetés rögzítve: ${remainingAmount.toFixed(2)} HUF (${method})`);
=======
      notify.success(`Fizetés rögzítve: ${amount} HUF (${method})`);
>>>>>>> origin/claude/fix-alert-popups-01DoqcMZnPzPADz1FcQk2gix
    } catch (error: any) {
      console.error('Payment recording failed:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a fizetés rögzítése közben!';
      notify.error(errorMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  // Split fizetés rögzítése (manuális összeg)
  const handleSplitPayment = async () => {
    const amount = parseFloat(splitPaymentAmount);
    if (isNaN(amount) || amount <= 0) {
      alert('Kérlek adj meg egy érvényes összeget!');
      return;
    }

    if (amount > remainingAmount) {
      alert(`A megadott összeg (${amount.toFixed(2)} HUF) nagyobb mint a hátralévő összeg (${remainingAmount.toFixed(2)} HUF)!`);
      return;
    }

    try {
      setIsProcessing(true);
      const payment = await recordPayment(order.id, {
        payment_method: selectedPaymentMethod,
        amount,
      });
      setPayments((prev) => [...prev, payment]);
      setSplitPaymentAmount('');
      setShowSplitPaymentForm(false);
      alert(`Split fizetés rögzítve: ${amount.toFixed(2)} HUF (${selectedPaymentMethod})`);
    } catch (error: any) {
      console.error('Split payment failed:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a fizetés rögzítése közben!';
      alert(errorMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  // Kedvezmény alkalmazása
  const handleApplyDiscount = async () => {
    if (isProcessing) return;

    // Validálás
    if (discountType === 'COUPON' && !couponCode.trim()) {
      alert('Kérlek adj meg egy kuponkódot!');
      return;
    }

    if (discountType !== 'COUPON' && !discountValue.trim()) {
      alert('Kérlek add meg a kedvezmény értékét!');
      return;
    }

    const value = parseFloat(discountValue);
    if (discountType !== 'COUPON' && (isNaN(value) || value <= 0)) {
      alert('Érvénytelen kedvezmény érték!');
      return;
    }

    if (discountType === 'PERCENTAGE' && value > 100) {
      alert('A százalékos kedvezmény nem lehet több mint 100%!');
      return;
    }

    try {
      setIsProcessing(true);

      // Kupon esetén először validáljuk
      if (discountType === 'COUPON') {
        const validation = await validateCoupon({
          code: couponCode,
          order_amount: order.total_amount || 0,
        });

        if (!validation.valid) {
          alert(`Kupon érvénytelen: ${validation.message}`);
          return;
        }
      }

      // Kedvezmény alkalmazása
      const request: ApplyOrderDiscountRequest = {
        discount_type: discountType,
        discount_value: discountType === 'COUPON' ? undefined : value,
        coupon_code: discountType === 'COUPON' ? couponCode : undefined,
        reason: discountReason || undefined,
      };

      const response = await applyDiscountToOrder(order.id, request);

      if (response.success) {
        alert(
          `Kedvezmény sikeresen alkalmazva!\n` +
          `Kedvezmény összege: ${response.discount_amount.toFixed(2)} HUF\n` +
          `Új összeg: ${response.new_total.toFixed(2)} HUF`
        );

        // Frissítjük a rendelés összegét
        order.total_amount = response.new_total;

        // Bezárjuk a kedvezmény formot
        setShowDiscountForm(false);
        setDiscountValue('');
        setCouponCode('');
        setDiscountReason('');
      } else {
        alert(`Kedvezmény alkalmazása sikertelen: ${response.message}`);
      }
    } catch (error: any) {
      console.error('Discount application failed:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a kedvezmény alkalmazása közben!';
      alert(errorMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  // Számla nyomtatás
  const handlePrintInvoice = async () => {
    if (isProcessing) return;

    if (!isFullyPaid) {
      alert('A számla csak teljesen kifizetett rendeléshez készíthető!');
      return;
    }

    const confirmed = window.confirm(
      'Biztos, hogy számlát szeretnél kiállítani ehhez a rendeléshez?'
    );
    if (!confirmed) return;

    try {
      setIsProcessing(true);

      // Mock adatok - éles környezetben ezeket az order items-ből kell betölteni
      const invoiceItems: InvoiceItem[] = [
        {
          name: 'Rendelés #' + order.id,
          quantity: 1,
          unit: 'db',
          unit_price: order.total_amount || 0,
          vat_rate: order.final_vat_rate,
        },
      ];

      // Számla létrehozása
      const invoiceRequest: CreateInvoiceRequest = {
        order_id: order.id,
        customer_name: 'Vendég', // TODO: order.customer_name-ből kellene jönnie
        customer_email: undefined,
        items: invoiceItems,
        payment_method: payments[0]?.payment_method === 'Készpénz' ? 'CASH' : 'CARD',
        notes: `Rendelés típus: ${order.order_type}`,
      };

      const response = await createInvoice(invoiceRequest);

      if (response.success && response.invoice_number) {
        setInvoiceNumber(response.invoice_number);
        alert(
          `Számla sikeresen létrehozva!\n` +
          `Számlaszám: ${response.invoice_number}\n` +
          (response.pdf_url ? `PDF: ${response.pdf_url}` : '')
        );

        // Ha van PDF URL, megnyitjuk új ablakban
        if (response.pdf_url) {
          window.open(response.pdf_url, '_blank');
        }
      } else {
        alert(`Számla létrehozása sikertelen: ${response.message}`);
      }
    } catch (error: any) {
      console.error('Invoice creation failed:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a számla létrehozása közben!';
      alert(errorMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  // Rendelés lezárása
  const handleCloseOrder = async () => {
    if (isProcessing) return;
    if (!isFullyPaid) {
      notify.warning('A rendelés még nincs teljesen kifizetve!');
      return;
    }

    const confirmed = window.confirm(
      'Biztos, hogy lezárod a rendelést? Ez a művelet nem visszavonható.'
    );
    if (!confirmed) return;

    try {
      setIsProcessing(true);
      await closeOrder(order.id);
      notify.success('Rendelés sikeresen lezárva!');
      onPaymentSuccess();
      onClose();
    } catch (error: any) {
      console.error('Order close failed:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a rendelés lezárása közben!';
      notify.error(errorMsg);
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

  const ntakStatus = getNTAKStatus();

  return (
    <div className="payment-modal-overlay" onClick={onClose}>
      <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="payment-modal-header">
          <div>
            <h2>💳 Fizetés - Rendelés #{order.id}</h2>
            <span className={`ntak-badge ntak-${ntakStatus.color}`}>
              {ntakStatus.text}
            </span>
          </div>
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

            {/* Kedvezmény szekció */}
            <div className="discount-section">
              <div className="section-header">
                <h3>🎁 Kedvezmények</h3>
                <button
                  onClick={() => setShowDiscountForm(!showDiscountForm)}
                  className="toggle-btn"
                  disabled={isFullyPaid || isProcessing}
                >
                  {showDiscountForm ? '➖ Bezár' : '➕ Kedvezmény hozzáadása'}
                </button>
              </div>

              {showDiscountForm && (
                <div className="discount-form">
                  <div className="form-row">
                    <label>Kedvezmény típusa:</label>
                    <select
                      value={discountType}
                      onChange={(e) => setDiscountType(e.target.value as DiscountType)}
                      className="discount-type-select"
                    >
                      <option value="PERCENTAGE">Százalék (%)</option>
                      <option value="FIXED_AMOUNT">Fix összeg (HUF)</option>
                      <option value="COUPON">Kuponkód</option>
                    </select>
                  </div>

                  {discountType === 'COUPON' ? (
                    <div className="form-row">
                      <label>Kuponkód:</label>
                      <input
                        type="text"
                        value={couponCode}
                        onChange={(e) => setCouponCode(e.target.value)}
                        placeholder="pl. WELCOME10"
                        className="discount-input"
                      />
                    </div>
                  ) : (
                    <div className="form-row">
                      <label>
                        {discountType === 'PERCENTAGE' ? 'Százalék (%)' : 'Összeg (HUF)'}:
                      </label>
                      <input
                        type="number"
                        value={discountValue}
                        onChange={(e) => setDiscountValue(e.target.value)}
                        placeholder={discountType === 'PERCENTAGE' ? '10' : '1000'}
                        min="0"
                        max={discountType === 'PERCENTAGE' ? '100' : undefined}
                        className="discount-input"
                      />
                    </div>
                  )}

                  <div className="form-row">
                    <label>Indoklás (opcionális):</label>
                    <input
                      type="text"
                      value={discountReason}
                      onChange={(e) => setDiscountReason(e.target.value)}
                      placeholder="pl. Törzsvásárlói kedvezmény"
                      className="discount-input"
                    />
                  </div>

                  <button
                    onClick={handleApplyDiscount}
                    disabled={isProcessing}
                    className="apply-discount-btn"
                  >
                    {isProcessing ? 'Feldolgozás...' : '✔️ Kedvezmény alkalmazása'}
                  </button>
                </div>
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
              <div className="section-header">
                <h3>💳 Gyors fizetés (teljes hátralévő összeg)</h3>
              </div>
              <div className="payment-methods-grid">
                {paymentMethods.map(({ label, method, icon }) => (
                  <button
                    key={method}
                    onClick={() => handleQuickPayment(method)}
                    disabled={isProcessing || isFullyPaid}
                    className="payment-method-btn"
                  >
                    <span className="icon">{icon}</span>
                    <span className="label">{label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Split Payment (Osztott fizetés) */}
            <div className="split-payment-section">
              <div className="section-header">
                <h3>💰 Osztott fizetés (részösszeg)</h3>
                <button
                  onClick={() => setShowSplitPaymentForm(!showSplitPaymentForm)}
                  className="toggle-btn"
                  disabled={isFullyPaid || isProcessing}
                >
                  {showSplitPaymentForm ? '➖ Bezár' : '➕ Részösszeg megadása'}
                </button>
              </div>

              {showSplitPaymentForm && (
                <div className="split-payment-form">
                  <div className="form-row">
                    <label>Összeg (HUF):</label>
                    <input
                      type="number"
                      value={splitPaymentAmount}
                      onChange={(e) => setSplitPaymentAmount(e.target.value)}
                      placeholder={`Max: ${remainingAmount.toFixed(2)} HUF`}
                      min="0"
                      max={remainingAmount}
                      step="0.01"
                      className="split-payment-input"
                    />
                  </div>

                  <div className="form-row">
                    <label>Fizetési mód:</label>
                    <select
                      value={selectedPaymentMethod}
                      onChange={(e) =>
                        setSelectedPaymentMethod(e.target.value as PaymentMethod)
                      }
                      className="payment-method-select"
                    >
                      {paymentMethods.map(({ label, method }) => (
                        <option key={method} value={method}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <button
                    onClick={handleSplitPayment}
                    disabled={isProcessing}
                    className="split-payment-btn"
                  >
                    {isProcessing ? 'Feldolgozás...' : '✔️ Részösszeg rögzítése'}
                  </button>
                </div>
              )}
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

            {/* Számla és lezárás gombok */}
            <div className="payment-modal-footer">
              <button
                onClick={handlePrintInvoice}
                disabled={!isFullyPaid || isProcessing}
                className={`invoice-btn ${isFullyPaid ? 'enabled' : 'disabled'}`}
              >
                {invoiceNumber
                  ? `📄 Számla: ${invoiceNumber}`
                  : '🖨️ Számla nyomtatása'}
              </button>

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
