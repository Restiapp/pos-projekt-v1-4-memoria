/**
 * InventoryPage - Raktárkezelés Dashboard
 *
 * Tabbed interface for inventory management:
 * - Készlet (Stock): Current inventory levels
 * - Bevételezés (Invoices): Incoming supplier invoices
 * - Készletnapló (Movements): Stock movement history
 * - Selejt (Waste): Waste logging
 */

import { useState } from 'react';
import { InventoryStock } from '@/components/admin/inventory/InventoryStock';
import { IncomingInvoices } from '@/components/admin/inventory/IncomingInvoices';
import { StockMovements } from '@/components/admin/inventory/StockMovements';
import { WasteLogs } from '@/components/admin/inventory/WasteLogs';
import './InventoryPage.css';

type TabType = 'stock' | 'invoices' | 'movements' | 'waste';

interface Tab {
  id: TabType;
  label: string;
  icon: string;
}

const TABS: Tab[] = [
  { id: 'stock', label: 'Készlet', icon: '📦' },
  { id: 'invoices', label: 'Bevételezés', icon: '📋' },
  { id: 'movements', label: 'Készletnapló', icon: '📊' },
  { id: 'waste', label: 'Selejt', icon: '🗑️' },
];

export const InventoryPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('stock');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'stock':
        return <InventoryStock />;
      case 'invoices':
        return <IncomingInvoices />;
      case 'movements':
        return <StockMovements />;
      case 'waste':
        return <WasteLogs />;
      default:
        return null;
    }
  };

  return (
    <div className="inventory-page">
      <div className="inventory-header">
        <h1>📦 Raktárkezelés</h1>
      </div>

      {/* Tab Navigation */}
      <div className="inventory-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="inventory-content">
        {renderTabContent()}
      </div>
    </div>
  );
};
