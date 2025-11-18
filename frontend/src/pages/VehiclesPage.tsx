/**
 * VehiclesPage - Gépjárművek oldal
 *
 * Főbb funkciók:
 *   - Tab navigáció: Járművek, Karbantartások, Tankolások
 *   - VehicleList komponens (járművek kezelése)
 *   - VehicleMaintenanceList komponens (karbantartások)
 *   - VehicleRefuelingList komponens (tankolások)
 */

import { useState } from 'react';
import { VehicleList } from '@/components/admin/VehicleList';
import { VehicleMaintenanceList } from '@/components/admin/VehicleMaintenanceList';
import { VehicleRefuelingList } from '@/components/admin/VehicleRefuelingList';
import './VehiclesPage.css';

type TabType = 'vehicles' | 'maintenances' | 'refuelings';

export const VehiclesPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('vehicles');

  return (
    <div className="vehicles-page">
      {/* Fejléc */}
      <header className="vehicles-header">
        <h1>🚗 Gépjárművek</h1>
        <p className="vehicles-description">
          Járművek, karbantartások és tankolások nyilvántartása
        </p>
      </header>

      {/* Tab navigáció */}
      <nav className="vehicles-tabs">
        <button
          className={`tab-button ${activeTab === 'vehicles' ? 'active' : ''}`}
          onClick={() => setActiveTab('vehicles')}
        >
          🚗 Járművek
        </button>
        <button
          className={`tab-button ${activeTab === 'maintenances' ? 'active' : ''}`}
          onClick={() => setActiveTab('maintenances')}
        >
          🔧 Karbantartások
        </button>
        <button
          className={`tab-button ${activeTab === 'refuelings' ? 'active' : ''}`}
          onClick={() => setActiveTab('refuelings')}
        >
          ⛽ Tankolások
        </button>
      </nav>

      {/* Tab tartalom */}
      <div className="vehicles-content">
        {activeTab === 'vehicles' && <VehicleList />}
        {activeTab === 'maintenances' && <VehicleMaintenanceList />}
        {activeTab === 'refuelings' && <VehicleRefuelingList />}
      </div>
    </div>
  );
};
