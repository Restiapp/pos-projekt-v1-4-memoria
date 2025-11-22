/**
 * VehicleRefuelingList - Tankolások listázása és kezelése
 *
 * Funkciók:
 *   - Tankolások listázása táblázatban
 *   - Új tankolás létrehozása
 *   - Tankolás törlése
 *   - Szűrés jármű szerint
 */

import { useState, useEffect } from 'react';
import {
  getVehicleRefuelings,
  deleteVehicleRefueling,
  getVehicles,
} from '@/services/vehicleService';
import type { VehicleRefueling, Vehicle } from '@/types/vehicle';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './VehicleRefuelingList.css';

export const VehicleRefuelingList = () => {
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();
  const [refuelings, setRefuelings] = useState<VehicleRefueling[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Szűrők
  const [selectedVehicleId, setSelectedVehicleId] = useState<
    number | undefined
  >(undefined);

  // Járművek betöltése (dropdown-hoz)
  const fetchVehicles = async () => {
    try {
      const data = await getVehicles({ is_active: true, limit: 500 });
      setVehicles(data);
    } catch (error) {
      console.error('Hiba a járművek betöltésekor:', error);
    }
  };

  // Tankolások betöltése
  const fetchRefuelings = async () => {
    try {
      setIsLoading(true);
      const data = await getVehicleRefuelings({
        vehicle_id: selectedVehicleId,
        limit: 500,
        offset: 0,
      });
      setRefuelings(data);
    } catch (error) {
      console.error('Hiba a tankolások betöltésekor:', error);
      showToast('Nem sikerült betölteni a tankolásokat!', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    if (isAuthenticated) {
      fetchVehicles();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchRefuelings();
    }
  }, [selectedVehicleId, isAuthenticated]);

  // Tankolás törlése
  const handleDelete = async (refueling: VehicleRefueling) => {
    const confirmed = await showConfirm(
      `Biztosan törölni szeretnéd ezt a tankolást?\n\n${new Date(
        refueling.refueling_date
      ).toLocaleDateString('hu-HU')} - ${refueling.quantity_liters.toLocaleString()} L`
    );

    if (!confirmed) return;

    try {
      await deleteVehicleRefueling(refueling.id);
      showToast('Tankolás sikeresen törölve!', 'success');
      fetchRefuelings();
    } catch (error) {
      console.error('Hiba a tankolás törlésekor:', error);
      showToast('Nem sikerült törölni a tankolást!', 'error');
    }
  };

  // Jármű neve ID alapján
  const getVehicleName = (vehicleId: number) => {
    const vehicle = vehicles.find((v) => v.id === vehicleId);
    return vehicle
      ? `${vehicle.brand} ${vehicle.model} (${vehicle.license_plate})`
      : `Jármű #${vehicleId}`;
  };

  // Üzemanyag típus fordítás
  const getFuelTypeLabel = (fuelType: string) => {
    const labels: Record<string, string> = {
      PETROL_95: '95-ös benzin',
      PETROL_98: '98-as benzin',
      DIESEL: 'Dízel',
      ELECTRIC: 'Elektromos',
      LPG: 'LPG',
      CNG: 'CNG',
    };
    return labels[fuelType] || fuelType;
  };

  return (
    <div className="refueling-list">
      {/* Fejléc */}
      <div className="list-header">
        <h2>Tankolások ({refuelings.length})</h2>
        <div className="header-actions">
          <button onClick={fetchRefuelings} className="btn-refresh">
            🔄 Frissítés
          </button>
        </div>
      </div>

      {/* Szűrők */}
      <div className="list-filters">
        <div className="filter-select-group">
          <label>
            Jármű:
            <select
              value={selectedVehicleId || ''}
              onChange={(e) =>
                setSelectedVehicleId(
                  e.target.value ? parseInt(e.target.value) : undefined
                )
              }
            >
              <option value="">Összes jármű</option>
              {vehicles.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.brand} {v.model} ({v.license_plate})
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {/* Betöltés állapot */}
      {isLoading && <div className="loading-state">Betöltés...</div>}

      {/* Üres állapot */}
      {!isLoading && refuelings.length === 0 && (
        <div className="empty-state">
          <p>Nincs megjeleníthető tankolás.</p>
        </div>
      )}

      {/* Táblázat */}
      {!isLoading && refuelings.length > 0 && (
        <div className="table-wrapper">
          <table className="refueling-table">
            <thead>
              <tr>
                <th>Jármű</th>
                <th>Dátum</th>
                <th>Km óra</th>
                <th>Üzemanyag</th>
                <th>Mennyiség (L)</th>
                <th>Egységár (Ft/L)</th>
                <th>Összesen (Ft)</th>
                <th>Teljes tank</th>
                <th>Helyszín</th>
                <th>Műveletek</th>
              </tr>
            </thead>
            <tbody>
              {refuelings.map((refueling) => (
                <tr key={refueling.id}>
                  <td>{getVehicleName(refueling.vehicle_id)}</td>
                  <td>
                    {new Date(refueling.refueling_date).toLocaleDateString(
                      'hu-HU'
                    )}
                  </td>
                  <td>
                    {refueling.mileage?.toLocaleString() || '-'} km
                  </td>
                  <td>{getFuelTypeLabel(refueling.fuel_type)}</td>
                  <td>{refueling.quantity_liters.toLocaleString()} L</td>
                  <td>
                    {refueling.price_per_liter.toLocaleString()} Ft
                  </td>
                  <td>
                    <strong>
                      {refueling.total_cost.toLocaleString()} Ft
                    </strong>
                  </td>
                  <td>{refueling.full_tank ? '✓ Igen' : '✗ Nem'}</td>
                  <td>{refueling.location || '-'}</td>
                  <td className="cell-actions">
                    <button
                      onClick={() => handleDelete(refueling)}
                      className="btn-delete"
                      title="Törlés"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
