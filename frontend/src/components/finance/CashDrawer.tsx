/**
 * CashDrawer - Pénztár műveletek (Befizetés/Kivétel)
 *
 * Funkciók:
 *   - Aktuális pénztár egyenleg megjelenítése
 *   - Készpénz befizetés rögzítése
 *   - Készpénz kivétel rögzítése
 *   - Műveletek közötti váltás (Befizetés/Kivétel)
 */

import { useState, useEffect } from 'react';
import { getCashBalance, cashDeposit, cashWithdraw } from '@/services/financeService';
import type { CashDepositRequest, CashWithdrawRequest } from '@/types/finance';
import { useAuthStore } from '@/stores/authStore';
import { notify } from '@/utils/notifications';
import './Finance.css';

type OperationType = 'deposit' | 'withdraw';

export const CashDrawer = () => {
  const { isAuthenticated } = useAuthStore();

  // State
  const [balance, setBalance] = useState<number>(0);
  const [isLoadingBalance, setIsLoadingBalance] = useState(true);
  const [operationType, setOperationType] = useState<OperationType>('deposit');
  const [amount, setAmount] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Egyenleg betöltése
  const fetchBalance = async () => {
    try {
      setIsLoadingBalance(true);
      const data = await getCashBalance();
      setBalance(data.balance);
    } catch (error) {
      console.error('Hiba az egyenleg betöltésekor:', error);
      notify.error('Nem sikerült betölteni a pénztár egyenleget!');
    } finally {
      setIsLoadingBalance(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchBalance();
    }
  }, [isAuthenticated]);

  // Form submit kezelése
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      notify.error('Érvénytelen összeg!');
      return;
    }

    try {
      setIsSubmitting(true);

      if (operationType === 'deposit') {
        const request: CashDepositRequest = {
          amount: numAmount,
          description: description || undefined,
        };
        await cashDeposit(request);
        notify.success('Befizetés sikeresen rögzítve!');
      } else {
        const request: CashWithdrawRequest = {
          amount: numAmount,
          description: description || undefined,
        };
        await cashWithdraw(request);
        notify.success('Kivétel sikeresen rögzítve!');
      }

      // Form reset és egyenleg frissítése
      setAmount('');
      setDescription('');
      fetchBalance();
    } catch (error: any) {
      console.error('Hiba a művelet során:', error);
      notify.error(error.response?.data?.detail || 'Nem sikerült a művelet!');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Ár formázás
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="cash-drawer">
      {/* Bal oldal: Aktuális egyenleg */}
      <div className="balance-card">
        <h2>💰 Pénztár Egyenleg</h2>
        {isLoadingBalance ? (
          <div className="loading-state">Betöltés...</div>
        ) : (
          <div className="balance-amount">{formatPrice(balance)}</div>
        )}
        <button onClick={fetchBalance} className="refresh-btn" disabled={isLoadingBalance}>
          🔄 Frissítés
        </button>
      </div>

      {/* Jobb oldal: Befizetés/Kivétel műveletek */}
      <div className="cash-operation-card">
        <h2>📝 Pénztár Műveletek</h2>

        {/* Művelet választó gombok */}
        <div className="operation-selector">
          <button
            type="button"
            className={`operation-btn ${operationType === 'deposit' ? 'active' : ''}`}
            onClick={() => setOperationType('deposit')}
          >
            ➕ Befizetés
          </button>
          <button
            type="button"
            className={`operation-btn ${operationType === 'withdraw' ? 'active' : ''}`}
            onClick={() => setOperationType('withdraw')}
          >
            ➖ Kivétel
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="cash-form">
          <div className="form-group">
            <label htmlFor="amount">Összeg (Ft) *</label>
            <input
              id="amount"
              type="number"
              min="0.01"
              step="1"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0"
              required
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Leírás / Megjegyzés</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Opcionális megjegyzés (pl. nyitó egyenleg, költségek, stb.)"
              rows={4}
              disabled={isSubmitting}
            />
          </div>

          <button
            type="submit"
            className={`submit-btn ${operationType}`}
            disabled={isSubmitting}
          >
            {isSubmitting
              ? 'Feldolgozás...'
              : operationType === 'deposit'
                ? '➕ Befizetés Rögzítése'
                : '➖ Kivétel Rögzítése'}
          </button>
        </form>
      </div>
    </div>
  );
};
