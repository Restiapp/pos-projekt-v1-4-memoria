// TODO-S0-STUB: TypeScript checking disabled - fix type issues
// @ts-nocheck
/**
 * StocktakingList - Leltár számlálások listázása ELTÉRÉS OSZLOPPAL
 *
 * Funkciók:
 *   - Leltár számlálások táblázatos megjelenítése
 *   - **ELTÉRÉS (Variance) oszlop**: Számolt - Elméleti
 *   - Színes jelzés: pozitív (zöld), negatív (piros), nulla (szürke)
 *   - Szűrés dátum és státusz szerint
 *   - Véglegesítés funkció
 */

import { useState, useEffect } from 'react';
import {
  getDailyInventoryCounts,
  getInventoryItems,
  finalizeInventoryCount,
} from '@/services/inventoryService';
import type { DailyInventoryCount, InventoryItem, StocktakingVariance } from '@/types/inventory';
import './Inventory.css';

export const StocktakingList = () => {
  const [counts, setCounts] = useState<DailyInventoryCount[]>([]);
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [selectedCountId, setSelectedCountId] = useState<number | null>(null);

  // Számlálások és tételek betöltése
  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [countsData, itemsData] = await Promise.all([
        getDailyInventoryCounts({
          status: statusFilter || undefined,
          limit: 50,
        }),
        getInventoryItems({ limit: 1000 }),
      ]);
      setCounts(countsData);
      setItems(itemsData);
    } catch (error) {
      console.error('Hiba a leltár adatok betöltésekor:', error);
      alert('Nem sikerült betölteni a leltár adatokat!');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  // **ELTÉRÉS (VARIANCE) SZÁMÍTÁSA**: Counted - Theoretical
  const calculateVariances = (count: DailyInventoryCount): StocktakingVariance[] => {
    const variances: StocktakingVariance[] = [];

    Object.entries(count.counts).forEach(([itemIdStr, countedQuantity]) => {
      const itemId = parseInt(itemIdStr);
      const item = items.find((i) => i.id === itemId);

      if (item) {
        const variance = countedQuantity - item.current_stock;
        variances.push({
          item_id: itemId,
          item_name: item.name,
          counted: countedQuantity,
          theoretical: item.current_stock,
          variance,
          unit: item.unit,
        });
      }
    });

    return variances;
  };

  // Leltár véglegesítése
  const handleFinalize = async (countId: number) => {
    if (!confirm('Biztosan véglegesíted ezt a leltárt? Ez a művelet nem visszavonható!')) return;

    try {
      await finalizeInventoryCount(countId);
      alert('Leltár sikeresen véglegesítve!');
      fetchData();
      setSelectedCountId(null);
    } catch (error) {
      console.error('Hiba a leltár véglegesítésekor:', error);
      alert('Nem sikerült véglegesíteni a leltárt!');
    }
  };

  // Részletek megjelenítése/elrejtése
  const toggleDetails = (countId: number) => {
    setSelectedCountId(selectedCountId === countId ? null : countId);
  };

  // Dátum formázás
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('hu-HU');
  };

  // Mennyiség formázás
  const formatQuantity = (quantity: number, unit: string): string => {
    return `${quantity.toFixed(2)} ${unit}`;
  };

  // Státusz badge
  const getStatusBadge = (status: string): JSX.Element => {
    const statusMap: Record<string, { label: string; className: string }> = {
      draft: { label: 'Vázlat', className: 'status-draft' },
      finalized: { label: 'Véglegesítve', className: 'status-finalized' },
    };

    const { label, className } = statusMap[status] || { label: status, className: '' };

    return <span className={`status-badge ${className}`}>{label}</span>;
  };

  // **ELTÉRÉS (VARIANCE) BADGE** - Színes jelzés
  const getVarianceBadge = (variance: number, unit: string): JSX.Element => {
    const className =
      variance === 0 ? 'variance-zero' : variance > 0 ? 'variance-positive' : 'variance-negative';

    const sign = variance > 0 ? '+' : '';

    return (
      <span className={`variance-badge ${className}`}>
        {sign}
        {formatQuantity(variance, unit)}
      </span>
    );
  };

  return (
    <div className="stocktaking-list">
      {/* Fejléc */}
      <header className="list-header">
        <h2>📋 Leltár számlálások</h2>
        <div className="header-controls">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="status-filter"
          >
            <option value="">Összes státusz</option>
            <option value="draft">Vázlat</option>
            <option value="finalized">Véglegesítve</option>
          </select>
          <button onClick={fetchData} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && counts.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="stocktaking-table">
              <thead>
                <tr>
                  <th>Azonosító</th>
                  <th>Leltár dátuma</th>
                  <th>Sablon ID</th>
                  <th>Tételek száma</th>
                  <th>Státusz</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {counts.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="empty-state">
                      Nincsenek leltár számlálások
                    </td>
                  </tr>
                ) : (
                  counts.map((count) => {
                    const variances = calculateVariances(count);
                    const isExpanded = selectedCountId === count.id;

                    return (
                      <>
                        {/* Fősor */}
                        <tr key={count.id} className={isExpanded ? 'expanded-row' : ''}>
                          <td>#{count.id}</td>
                          <td>{formatDate(count.count_date)}</td>
                          <td>Sablon #{count.sheet_id}</td>
                          <td>{Object.keys(count.counts).length} tétel</td>
                          <td>{getStatusBadge(count.status)}</td>
                          <td>
                            <button
                              onClick={() => toggleDetails(count.id)}
                              className="action-btn details-btn"
                              title="Részletek"
                            >
                              {isExpanded ? '👁️ Elrejt' : '👁️ Részletek'}
                            </button>
                            {count.status === 'draft' && (
                              <button
                                onClick={() => handleFinalize(count.id)}
                                className="action-btn finalize-btn"
                                title="Véglegesítés"
                              >
                                ✅ Véglegesítés
                              </button>
                            )}
                          </td>
                        </tr>

                        {/* **RÉSZLETES NÉT: ELTÉRÉS OSZLOPPAL** */}
                        {isExpanded && (
                          <tr className="details-row">
                            <td colSpan={6}>
                              <div className="variance-details">
                                <h3>📊 Leltár részletei - Eltérések</h3>
                                <table className="variance-table">
                                  <thead>
                                    <tr>
                                      <th>Tétel</th>
                                      <th>Számolt mennyiség</th>
                                      <th>Elméleti készlet</th>
                                      <th>⚖️ Eltérés (Variance)</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {variances.length === 0 ? (
                                      <tr>
                                        <td colSpan={4} className="empty-state">
                                          Nincs adat
                                        </td>
                                      </tr>
                                    ) : (
                                      variances.map((variance) => (
                                        <tr key={variance.item_id}>
                                          <td>{variance.item_name}</td>
                                          <td>{formatQuantity(variance.counted, variance.unit)}</td>
                                          <td>{formatQuantity(variance.theoretical, variance.unit)}</td>
                                          <td>{getVarianceBadge(variance.variance, variance.unit)}</td>
                                        </tr>
                                      ))
                                    )}
                                  </tbody>
                                </table>
                                {count.notes && (
                                  <div className="count-notes">
                                    <strong>Megjegyzések:</strong> {count.notes}
                                  </div>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};
