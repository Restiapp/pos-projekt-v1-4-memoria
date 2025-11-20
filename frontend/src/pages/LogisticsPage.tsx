/**
 * LogisticsPage - Logisztikai Adminisztrációs Dashboard
 *
 * Funkciók:
 *   - Futárok listázása és kezelése (státusz, CRUD)
 *   - Kiszállítási zónák kezelése (CRUD)
 *   - Aktív kiszállítások listázása (placeholder - V4.0)
 *
 * Tab struktúra:
 *   1. Futárok (CourierManager)
 *   2. Kiszállítási Zónák (ZoneManager)
 *   3. Aktív Kiszállítások (DeliveryList - placeholder)
 */

import { useState } from 'react';
import { DispatchPanel } from '@/components/DispatchPanel';
import './LogisticsPage.css';

type TabType = 'couriers' | 'zones' | 'deliveries';

export const LogisticsPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('couriers');

  return (
    <div className="logistics-page">
      <header className="logistics-header">
        <h1>🚚 Logisztikai Adminisztráció</h1>
        <p className="logistics-subtitle">
          Futárok, zónák és kiszállítások kezelése
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
          onClick={() => setActiveTab('zones')}
          className={`tab-btn ${activeTab === 'zones' ? 'active' : ''}`}
        >
          📍 Kiszállítási Zónák
        </button>
        <button
          onClick={() => setActiveTab('deliveries')}
          className={`tab-btn ${activeTab === 'deliveries' ? 'active' : ''}`}
        >
          📦 Aktív Kiszállítások
        </button>
      </nav>

      {/* Tab Tartalom */}
      <main className="logistics-content">
        {activeTab === 'couriers' && <CourierManagerPlaceholder />}
        {activeTab === 'zones' && <ZoneManagerPlaceholder />}
        {activeTab === 'deliveries' && <DispatchPanel />}
      </main>
    </div>
  );
};

// =============================================================
// PLACEHOLDER KOMPONENSEK (V4.0-ban teljes implementáció)
// =============================================================

const CourierManagerPlaceholder = () => (
  <div className="placeholder-section">
    <h2>👷 Futárok Kezelése</h2>
    <p>
      Itt kezelheted a futárokat: új futár létrehozása, státusz módosítása,
      szerkesztés, törlés.
    </p>
    <div className="placeholder-box">
      <p>📋 Futárok listája (táblázat)</p>
      <p>✏️ CRUD műveletek (Létrehozás, Szerkesztés, Törlés)</p>
      <p>🔄 Státusz módosítás (Elérhető, Úton, Szünet, Offline)</p>
      <p>🔍 Szűrés és keresés</p>
    </div>
    <p className="todo-note">
      TODO (V4.0): Teljes CourierManager komponens implementálása
    </p>
  </div>
);

const ZoneManagerPlaceholder = () => (
  <div className="placeholder-section">
    <h2>📍 Kiszállítási Zónák Kezelése</h2>
    <p>
      Itt kezelheted a kiszállítási zónákat: új zóna létrehozása, szerkesztés,
      törlés, zóna részletei.
    </p>
    <div className="placeholder-box">
      <p>📋 Zónák listája (táblázat)</p>
      <p>✏️ CRUD műveletek (Létrehozás, Szerkesztés, Törlés)</p>
      <p>💰 Kiszállítási díj és minimum rendelési érték beállítása</p>
      <p>🗺️ Irányítószámok kezelése (V3.0 / Phase 3.B)</p>
    </div>
    <p className="todo-note">
      TODO (V4.0): Teljes ZoneManager komponens implementálása
    </p>
  </div>
);

const DeliveryListPlaceholder = () => (
  <div className="placeholder-section">
    <h2>📦 Aktív Kiszállítások</h2>
    <p>
      Itt láthatod az összes aktív kiszállítást: futárhoz rendelés, státusz
      követés, útvonal nézet.
    </p>
    <div className="placeholder-box">
      <p>📋 Aktív kiszállítások listája</p>
      <p>👷 Futár hozzárendelése</p>
      <p>📊 Státusz követés (Új, Úton, Kiszállítva)</p>
      <p>🗺️ Útvonal megtekintése (Google Maps integráció)</p>
    </div>
    <p className="todo-note">
      TODO (V4.0): Teljes DeliveryList komponens implementálása
    </p>
  </div>
);
