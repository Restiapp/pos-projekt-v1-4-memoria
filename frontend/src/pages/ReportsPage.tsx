/**
 * ReportsPage - Analytics Dashboard
 * Látványos vezetői nézet értékesítési és készletadatokkal
 */

import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import reportsService from '@/services/reportsService';
import type { ReportsResponse, DateRange, DateRangePreset } from '@/types/reports';
import './ReportsPage.css';

// Színek a grafikonokhoz
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

export const ReportsPage = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ReportsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'consumption'>('overview');

  // Dátumszűrő állapot
  const [dateRangePreset, setDateRangePreset] = useState<DateRangePreset>('week');
  const [customDateRange] = useState<DateRange>({
    start_date: '',
    end_date: '',
  });

  /**
   * Dátumtartomány kiszámítása a preset alapján
   */
  const getDateRangeFromPreset = (preset: DateRangePreset): DateRange => {
    const today = new Date();
    const endDate = today.toISOString().split('T')[0];

    let startDate: string;

    switch (preset) {
      case 'today':
        startDate = endDate;
        break;
      case 'week':
        const weekAgo = new Date(today);
        weekAgo.setDate(today.getDate() - 7);
        startDate = weekAgo.toISOString().split('T')[0];
        break;
      case 'month':
        const monthAgo = new Date(today);
        monthAgo.setMonth(today.getMonth() - 1);
        startDate = monthAgo.toISOString().split('T')[0];
        break;
      case 'custom':
        return customDateRange;
      default:
        startDate = endDate;
    }

    return { start_date: startDate, end_date: endDate };
  };

  /**
   * Riport adatok betöltése
   */
  const loadReportsData = async () => {
    setLoading(true);
    setError(null);

    try {
      const dateRange = getDateRangeFromPreset(dateRangePreset);
      const reportsData = await reportsService.getReportsData(dateRange);
      setData(reportsData);
    } catch (err: any) {
      console.error('Hiba a riport betöltésekor:', err);
      setError(err?.response?.data?.detail || 'Hiba történt a riport betöltésekor');
    } finally {
      setLoading(false);
    }
  };

  // Első betöltés és dátumszűrő változáskor újratöltés
  useEffect(() => {
    loadReportsData();
  }, [dateRangePreset]);

  /**
   * Szám formázása (ezer elválasztó, 2 tizedesjegy)
   */
  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  /**
   * Pénz formázása (HUF)
   */
  const formatCurrency = (num: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(num);
  };

  if (loading) {
    return (
      <div className="reports-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Riport betöltése...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="reports-page">
        <div className="error-container">
          <h2>Hiba történt</h2>
          <p>{error}</p>
          <button onClick={loadReportsData} className="btn-retry">
            Újrapróbálkozás
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="reports-page">
        <p>Nincs elérhető adat</p>
      </div>
    );
  }

  return (
    <div className="reports-page">
      <header className="reports-header">
        <h1>📊 Analytics Dashboard</h1>

        {/* Date Range Picker */}
        <div className="date-range-picker">
          <button
            className={`preset-btn ${dateRangePreset === 'today' ? 'active' : ''}`}
            onClick={() => setDateRangePreset('today')}
          >
            Ma
          </button>
          <button
            className={`preset-btn ${dateRangePreset === 'week' ? 'active' : ''}`}
            onClick={() => setDateRangePreset('week')}
          >
            Hét
          </button>
          <button
            className={`preset-btn ${dateRangePreset === 'month' ? 'active' : ''}`}
            onClick={() => setDateRangePreset('month')}
          >
            Hónap
          </button>
          {/* TODO: Egyedi dátumtartomány választó */}
        </div>
      </header>

      {/* Tabok: Áttekintés | Fogyás */}
      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Áttekintés
        </button>
        <button
          className={`tab-btn ${activeTab === 'consumption' ? 'active' : ''}`}
          onClick={() => setActiveTab('consumption')}
        >
          Alapanyag Fogyás
        </button>
      </div>

      {/* === ÁTTEKINTÉS TAB === */}
      {activeTab === 'overview' && (
        <div className="overview-tab">
          {/* Key Metrics Cards */}
          <div className="metrics-cards">
            <div className="metric-card">
              <div className="metric-icon">💰</div>
              <div className="metric-content">
                <h3>Összbevétel</h3>
                <p className="metric-value">{formatCurrency(data.metrics.total_revenue)}</p>
                <span className="metric-detail">
                  Készpénz: {formatCurrency(data.metrics.cash_revenue)} | Kártya:{' '}
                  {formatCurrency(data.metrics.card_revenue)}
                </span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🛒</div>
              <div className="metric-content">
                <h3>Rendelések száma</h3>
                <p className="metric-value">{formatNumber(data.metrics.total_orders)}</p>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">📈</div>
              <div className="metric-content">
                <h3>Átlagos kosár</h3>
                <p className="metric-value">{formatCurrency(data.metrics.average_basket)}</p>
              </div>
            </div>
          </div>

          {/* Sales Chart - Stacked Bar Chart (CASH vs CARD) */}
          <div className="chart-section">
            <h2>Napi bevételek (Készpénz vs Kártya)</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={data.daily_sales}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value as number)} />
                <Legend />
                <Bar dataKey="revenue_cash" stackId="a" fill="#4CAF50" name="Készpénz" />
                <Bar dataKey="revenue_card" stackId="a" fill="#2196F3" name="Kártya" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Sales Trend Line Chart */}
          <div className="chart-section">
            <h2>Bevételi trend</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.daily_sales}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value as number)} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="revenue_total"
                  stroke="#8884d8"
                  strokeWidth={2}
                  name="Összes bevétel"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Top Products - Pie Chart & List */}
          <div className="top-products-section">
            <h2>Top termékek</h2>
            <div className="top-products-container">
              {/* Pie Chart */}
              <div className="top-products-chart">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={data.top_products as any[]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry: any) => `${entry.product_name} (${entry.percentage?.toFixed(0) || '0'}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="total_revenue"
                    >
                      {data.top_products.map((_entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value as number)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Lista */}
              <div className="top-products-list">
                <table>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Termék</th>
                      <th>Eladott</th>
                      <th>Bevétel</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.top_products.map((product, index) => (
                      <tr key={product.product_id}>
                        <td>{index + 1}</td>
                        <td>{product.product_name}</td>
                        <td>{formatNumber(product.quantity_sold)} db</td>
                        <td>{formatCurrency(product.total_revenue)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* === ALAPANYAG FOGYÁS TAB === */}
      {activeTab === 'consumption' && (
        <div className="consumption-tab">
          <h2>Alapanyag felhasználás</h2>
          <table className="consumption-table">
            <thead>
              <tr>
                <th>Alapanyag</th>
                <th>Felhasznált mennyiség</th>
                <th>Egység</th>
                <th>Költség</th>
              </tr>
            </thead>
            <tbody>
              {data.ingredient_consumption.map((ingredient) => (
                <tr key={ingredient.ingredient_id}>
                  <td>{ingredient.ingredient_name}</td>
                  <td>{formatNumber(ingredient.quantity_consumed)}</td>
                  <td>{ingredient.unit}</td>
                  <td>{formatCurrency(ingredient.cost)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
