/**
 * ReportsPage - Dashboard Analitika és Riportok oldal
 *
 * Főbb funkciók:
 *   - Tab navigáció a különböző riportok között
 *   - Értékesítési statisztikák (napi bontás)
 *   - Top termékek elemzése
 *   - Készletfogyási riportok
 */

import { useState, useEffect } from 'react';
import {
  getSalesReport,
  getTopProducts,
  getConsumptionReport,
  getDateRangePresets,
} from '@/services/reportsService';
import type {
  SalesReportResponse,
  TopProductsResponse,
  ConsumptionReportResponse,
} from '@/types/reports';
import './ReportsPage.css';

type TabType = 'sales' | 'top-products' | 'consumption';
type PresetType = 'today' | 'yesterday' | 'last7Days' | 'last30Days' | 'thisMonth' | 'lastMonth';

export const ReportsPage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('sales');
  const [selectedPreset, setSelectedPreset] = useState<PresetType>('last30Days');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Report data
  const [salesReport, setSalesReport] = useState<SalesReportResponse | null>(null);
  const [topProductsReport, setTopProductsReport] = useState<TopProductsResponse | null>(null);
  const [consumptionReport, setConsumptionReport] = useState<ConsumptionReportResponse | null>(null);

  const presets = getDateRangePresets();

  // Fetch data when tab or preset changes
  useEffect(() => {
    fetchData();
  }, [activeTab, selectedPreset]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = presets[selectedPreset];

      if (activeTab === 'sales') {
        const data = await getSalesReport(params);
        setSalesReport(data);
      } else if (activeTab === 'top-products') {
        const data = await getTopProducts({ ...params, limit: 10 });
        setTopProductsReport(data);
      } else if (activeTab === 'consumption') {
        const data = await getConsumptionReport(params);
        setConsumptionReport(data);
      }
    } catch (err: any) {
      console.error('Error fetching report data:', err);
      setError(err.response?.data?.detail || 'Hiba történt az adatok lekérdezése során');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('hu-HU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(date);
  };

  return (
    <div className="reports-page">
      {/* Fejléc */}
      <header className="reports-header">
        <h1>📊 Dashboard Analitika</h1>
        <p className="reports-description">
          Értékesítési statisztikák, top termékek és készletfogyási riportok
        </p>
      </header>

      {/* Időszak választó */}
      <div className="date-preset-selector">
        <label>Időszak:</label>
        <select
          value={selectedPreset}
          onChange={(e) => setSelectedPreset(e.target.value as PresetType)}
          className="preset-select"
        >
          <option value="today">Ma</option>
          <option value="yesterday">Tegnap</option>
          <option value="last7Days">Utolsó 7 nap</option>
          <option value="last30Days">Utolsó 30 nap</option>
          <option value="thisMonth">Ez a hónap</option>
          <option value="lastMonth">Előző hónap</option>
        </select>
        <button onClick={fetchData} className="refresh-button">
          🔄 Frissítés
        </button>
      </div>

      {/* Tab navigáció */}
      <nav className="reports-tabs">
        <button
          className={`tab-button ${activeTab === 'sales' ? 'active' : ''}`}
          onClick={() => setActiveTab('sales')}
        >
          💰 Értékesítés
        </button>
        <button
          className={`tab-button ${activeTab === 'top-products' ? 'active' : ''}`}
          onClick={() => setActiveTab('top-products')}
        >
          🏆 Top Termékek
        </button>
        <button
          className={`tab-button ${activeTab === 'consumption' ? 'active' : ''}`}
          onClick={() => setActiveTab('consumption')}
        >
          📦 Készletfogyás
        </button>
      </nav>

      {/* Tartalom */}
      <div className="reports-content">
        {loading && (
          <div className="loading-message">
            <p>⏳ Adatok betöltése...</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            <p>❌ {error}</p>
          </div>
        )}

        {!loading && !error && activeTab === 'sales' && salesReport && (
          <div className="sales-report">
            <div className="summary-cards">
              <div className="summary-card">
                <h3>Összesített bevétel</h3>
                <p className="big-number">{formatCurrency(salesReport.total_revenue)}</p>
              </div>
              <div className="summary-card">
                <h3>Összes rendelés</h3>
                <p className="big-number">{salesReport.total_orders}</p>
              </div>
              <div className="summary-card">
                <h3>Átlagos napi bevétel</h3>
                <p className="big-number">{formatCurrency(salesReport.average_daily_revenue)}</p>
              </div>
            </div>

            <h2>Napi bontás</h2>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Dátum</th>
                    <th>Összesített bevétel</th>
                    <th>Készpénz</th>
                    <th>Kártya</th>
                    <th>Rendelések</th>
                    <th>Átlag rendelés</th>
                  </tr>
                </thead>
                <tbody>
                  {salesReport.sales_data.map((day, index) => (
                    <tr key={index}>
                      <td>{formatDate(day.date)}</td>
                      <td className="currency">{formatCurrency(day.total_revenue)}</td>
                      <td className="currency">{formatCurrency(day.cash_revenue)}</td>
                      <td className="currency">{formatCurrency(day.card_revenue)}</td>
                      <td>{day.order_count}</td>
                      <td className="currency">{formatCurrency(day.average_order_value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {!loading && !error && activeTab === 'top-products' && topProductsReport && (
          <div className="top-products-report">
            <div className="summary-cards">
              <div className="summary-card">
                <h3>Elemzett termékek</h3>
                <p className="big-number">{topProductsReport.total_products_analyzed}</p>
              </div>
              <div className="summary-card">
                <h3>Top termékek</h3>
                <p className="big-number">{topProductsReport.products.length}</p>
              </div>
            </div>

            <h2>Top termékek</h2>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Termék név</th>
                    <th>Kategória</th>
                    <th>Eladott db</th>
                    <th>Összes bevétel</th>
                    <th>Átlag ár</th>
                  </tr>
                </thead>
                <tbody>
                  {topProductsReport.products.map((product, index) => (
                    <tr key={product.product_id}>
                      <td className="rank">
                        {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
                      </td>
                      <td className="product-name">{product.product_name}</td>
                      <td>{product.category_name || '-'}</td>
                      <td>{product.quantity_sold}</td>
                      <td className="currency">{formatCurrency(product.total_revenue)}</td>
                      <td className="currency">{formatCurrency(product.average_price)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {!loading && !error && activeTab === 'consumption' && consumptionReport && (
          <div className="consumption-report">
            <div className="summary-cards">
              <div className="summary-card">
                <h3>Fogyó tételek</h3>
                <p className="big-number">{consumptionReport.total_items}</p>
              </div>
              <div className="summary-card">
                <h3>Becsült költség</h3>
                <p className="big-number">
                  {consumptionReport.total_estimated_cost
                    ? formatCurrency(consumptionReport.total_estimated_cost)
                    : 'N/A'}
                </p>
              </div>
            </div>

            <h2>Készletfogyás</h2>
            {consumptionReport.consumption_data.length === 0 ? (
              <div className="empty-message">
                <p>Nincs készletfogyási adat az adott időszakban</p>
              </div>
            ) : (
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Alapanyag név</th>
                      <th>Fogyott mennyiség</th>
                      <th>Egység</th>
                      <th>Becsült költség</th>
                    </tr>
                  </thead>
                  <tbody>
                    {consumptionReport.consumption_data.map((item) => (
                      <tr key={item.ingredient_id}>
                        <td className="ingredient-name">{item.ingredient_name}</td>
                        <td>{item.quantity_consumed.toFixed(2)}</td>
                        <td>{item.unit}</td>
                        <td className="currency">
                          {item.estimated_cost ? formatCurrency(item.estimated_cost) : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
