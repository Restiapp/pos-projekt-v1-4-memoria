/**
 * AssetsPage - Tárgyi Eszközök oldal
 *
 * Főbb funkciók:
 *   - Tab navigáció: Eszközcsoportok, Eszközök, Szerviz bejegyzések
 *   - AssetGroupList komponens (eszközcsoportok kezelése)
 *   - AssetList komponens (eszközök kezelése)
 *   - AssetServiceList komponens (szerviz történet)
 */

import { useState } from 'react';
import { AssetGroupList } from '@/components/admin/AssetGroupList';
import { AssetList } from '@/components/admin/AssetList';
import { AssetServiceList } from '@/components/admin/AssetServiceList';
import './AssetsPage.css';

type TabType = 'asset-groups' | 'assets' | 'services';

export const AssetsPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('assets');

  return (
    <div className="assets-page">
      {/* Fejléc */}
      <header className="assets-header">
        <h1>🏭 Tárgyi Eszközök</h1>
        <p className="assets-description">
          Eszközcsoportok, eszközök és szerviz bejegyzések kezelése
        </p>
      </header>

      {/* Tab navigáció */}
      <nav className="assets-tabs">
        <button
          className={`tab-button ${activeTab === 'asset-groups' ? 'active' : ''}`}
          onClick={() => setActiveTab('asset-groups')}
        >
          📁 Eszközcsoportok
        </button>
        <button
          className={`tab-button ${activeTab === 'assets' ? 'active' : ''}`}
          onClick={() => setActiveTab('assets')}
        >
          📦 Eszközök
        </button>
        <button
          className={`tab-button ${activeTab === 'services' ? 'active' : ''}`}
          onClick={() => setActiveTab('services')}
        >
          🔧 Szerviz történet
        </button>
      </nav>

      {/* Tab tartalom */}
      <div className="assets-content">
        {activeTab === 'asset-groups' && <AssetGroupList />}
        {activeTab === 'assets' && <AssetList />}
        {activeTab === 'services' && <AssetServiceList />}
      </div>
    </div>
  );
};
