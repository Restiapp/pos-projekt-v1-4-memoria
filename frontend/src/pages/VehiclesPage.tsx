/**
 * VehiclesPage - Gépjárművek oldal
 *
 * Főbb funkciók:
 *   - Tab navigáció: Járművek, Tankolások, Karbantartások
 *   - VehicleList komponens (járművek kezelése)
 *   - RefuelingList komponens (tankolások kezelése)
 *   - MaintenanceList komponens (karbantartások kezelése)
 */

import { useState } from 'react';
import { VehicleList } from '@/components/admin/VehicleList';
import { RefuelingList } from '@/components/admin/RefuelingList';
import { MaintenanceList } from '@/components/admin/MaintenanceList';
import './VehiclesPage.css';

type TabType = 'vehicles' | 'refuelings' | 'maintenances';

export const VehiclesPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('vehicles');

  return (
    <div className="vehicles-page">
      {/* Fejléc */}
      <header className="vehicles-header">
        <h1>Gépjárművek</h1>
        <p className="vehicles-description">
          Járművek, tankolások és karbantartások nyilvántartása
        </p>
      </header>

      {/* Tab navigáció */}
      <nav className="vehicles-tabs">
        <button
          className={`tab-button ${activeTab === 'vehicles' ? 'active' : ''}`}
          onClick={() => setActiveTab('vehicles')}
        >
          Járművek
        </button>
        <button
          className={`tab-button ${activeTab === 'refuelings' ? 'active' : ''}`}
          onClick={() => setActiveTab('refuelings')}
        >
          Tankolások
        </button>
        <button
          className={`tab-button ${activeTab === 'maintenances' ? 'active' : ''}`}
          onClick={() => setActiveTab('maintenances')}
        >
          Karbantartások
        </button>
      </nav>

      {/* Tab tartalom */}
      <div className="vehicles-content">
        {activeTab === 'vehicles' && <VehicleList />}
        {activeTab === 'refuelings' && <RefuelingList />}
        {activeTab === 'maintenances' && <MaintenanceList />}
      </div>
    </div>
  );
};
