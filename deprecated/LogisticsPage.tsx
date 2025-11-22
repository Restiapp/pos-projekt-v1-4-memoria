/**
 * LogisticsPage - Logisztikai Adminisztrációs Dashboard
 *
 * Funkciók:
 *   - Tab 1: Futárok kezelése (létrehozás, szerkesztés, státusz módosítás)
 *   - Tab 2: Diszpécser (várakozó rendelések + futár hozzárendelés)
 *
 * Tab struktúra:
 *   1. Futárok (CourierList)
 *   2. Diszpécser (DispatchPanel)
 */

import { useState } from 'react';
import { CourierList } from '@/components/logistics/CourierList';
import { DispatchPanel } from '@/components/logistics/DispatchPanel';
import './LogisticsPage.css';

type TabType = 'couriers' | 'dispatch';

export const LogisticsPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('couriers');

  return (
    <div className="logistics-page">
      <header className="logistics-header">
        <h1>🚚 Logisztikai Adminisztráció</h1>
        <p className="logistics-subtitle">
          Futárok és kiszállítások kezelése
        </p>
      </header>

      {/* Tab Navigáció */}
      <nav className="logistics-tabs">
        <button
          onClick={() => setActiveTab('couriers')}
          className={`tab-btn ${activeTab === 'couriers' ? 'active' : ''}`}
        >
          👷 Futárok
        </button>
        <button
          onClick={() => setActiveTab('dispatch')}
          className={`tab-btn ${activeTab === 'dispatch' ? 'active' : ''}`}
        >
          📦 Diszpécser
        </button>
      </nav>

      {/* Tab Tartalom */}
      <main className="logistics-content">
        {activeTab === 'couriers' && <CourierList />}
        {activeTab === 'dispatch' && <DispatchPanel />}
      </main>
    </div>
  );
};

