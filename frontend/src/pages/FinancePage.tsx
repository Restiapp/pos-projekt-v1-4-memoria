/**
 * FinancePage - Pénzügy és Zárások oldal
 *
 * Főbb funkciók:
 *   - Tab navigáció a Pénztár és Napi Zárások között
 *   - CashDrawer komponens (befizetés/kivétel)
 *   - DailyClosureList komponens (napi zárások kezelése)
 */

import { useState } from 'react';
import { CashDrawer } from '@/components/finance/CashDrawer';
import { DailyClosureList } from '@/components/finance/DailyClosureList';
import './FinancePage.css';

type TabType = 'cash-drawer' | 'daily-closures';

export const FinancePage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('cash-drawer');

  return (
    <div className="finance-page">
      {/* Fejléc */}
      <header className="finance-header">
        <h1>💰 Pénzügy és Zárások</h1>
        <p className="finance-description">
          Pénztár műveletek, napi zárások és pénzügyi jelentések kezelése
        </p>
      </header>

      {/* Tab navigáció */}
      <nav className="finance-tabs">
        <button
          className={`tab-button ${activeTab === 'cash-drawer' ? 'active' : ''}`}
          onClick={() => setActiveTab('cash-drawer')}
        >
          💵 Pénztár
        </button>
        <button
          className={`tab-button ${activeTab === 'daily-closures' ? 'active' : ''}`}
          onClick={() => setActiveTab('daily-closures')}
        >
          📊 Napi Zárások
        </button>
      </nav>

      {/* Tab tartalom */}
      <div className="finance-content">
        {activeTab === 'cash-drawer' && <CashDrawer />}
        {activeTab === 'daily-closures' && <DailyClosureList />}
      </div>
    </div>
  );
};
