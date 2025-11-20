/**
 * InventoryPage - Raktárkezelés oldal
 *
 * Főbb funkciók:
 *   - Tab navigáció: Raktári tételek, Számlák (OCR), Leltár, Selejt
 *   - InventoryItemsList komponens (raktári tételek kezelése)
 *   - InvoicesList komponens (számlák OCR feldolgozása és véglegesítése)
 *   - StocktakingList komponens (leltár számlálások eltérés megjelenítéssel)
 *   - WasteRecordingModal komponens (selejt rögzítése)
 */

import { useState } from 'react';
import { InventoryItemsList } from '@/components/inventory/InventoryItemsList';
import { InvoicesList } from '@/components/inventory/InvoicesList';
import { StocktakingList } from '@/components/inventory/StocktakingList';
import { WasteRecordingList } from '@/components/inventory/WasteRecordingList';
import './InventoryPage.css';

type TabType = 'items' | 'invoices' | 'stocktaking' | 'waste';

export const InventoryPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('items');

  return (
    <div className="inventory-page">
      {/* Fejléc */}
      <header className="inventory-header">
        <h1>📦 Raktárkezelés</h1>
        <p className="inventory-description">
          Készlet, számlák, leltár és selejt kezelése
        </p>
      </header>

      {/* Tab navigáció */}
      <nav className="inventory-tabs">
        <button
          className={`tab-button ${activeTab === 'items' ? 'active' : ''}`}
          onClick={() => setActiveTab('items')}
        >
          📦 Raktári tételek
        </button>
        <button
          className={`tab-button ${activeTab === 'invoices' ? 'active' : ''}`}
          onClick={() => setActiveTab('invoices')}
        >
          📄 Számlák (OCR)
        </button>
        <button
          className={`tab-button ${activeTab === 'stocktaking' ? 'active' : ''}`}
          onClick={() => setActiveTab('stocktaking')}
        >
          📋 Leltár
        </button>
        <button
          className={`tab-button ${activeTab === 'waste' ? 'active' : ''}`}
          onClick={() => setActiveTab('waste')}
        >
          🗑️ Selejt
        </button>
      </nav>

      {/* Tab tartalom */}
      <div className="inventory-content">
        {activeTab === 'items' && <InventoryItemsList />}
        {activeTab === 'invoices' && <InvoicesList />}
        {activeTab === 'stocktaking' && <StocktakingList />}
        {activeTab === 'waste' && <WasteRecordingList />}
      </div>
    </div>
  );
};
