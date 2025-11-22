/**
 * VehicleMaintenanceList - Jármű karbantartások listázása és kezelése
 *
 * Funkciók:
 *   - Karbantartások listázása táblázatban
 *   - Új karbantartás létrehozása
 *   - Karbantartás törlése
 *   - Szűrés jármű és típus szerint
 */

import { useState, useEffect } from 'react';
import {
  getVehicleMaintenances,
  deleteVehicleMaintenance,
  getVehicles,
} from '@/services/vehicleService';
import type { VehicleMaintenance, Vehicle } from '@/types/vehicle';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './VehicleMaintenanceList.css';

export const VehicleMaintenanceList = () => {
  // TODO-S0-STUB: Replace with proper useAuth hook
  const isAuthenticated = true;

  const { showToast } = useToast();
  const { showConfirm } = useConfirm();
  const [maintenances, setMaintenances] = useState<VehicleMaintenance[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Szűrők
  const [selectedVehicleId, setSelectedVehicleId] = useState<
    number | undefined
  >(undefined);
  const [selectedType, setSelectedType] = useState<string | undefined>(
    undefined
  );

  // Járművek betöltése (dropdown-hoz)
  const fetchVehicles = async () => {
    try {
      const data = await getVehicles({ is_active: true, limit: 500 });
      setVehicles(data);
    } catch (error) {
      console.error('Hiba a járművek betöltésekor:', error);
    }
  };

  // Karbantartások betöltése
  const fetchMaintenances = async () => {
    try {
      setIsLoading(true);
      const data = await getVehicleMaintenances({
        vehicle_id: selectedVehicleId,
        maintenance_type: selectedType,
        limit: 500,
        offset: 0,
      });
      setMaintenances(data);
    } catch (error) {
      console.error('Hiba a karbantartások betöltésekor:', error);
      showToast('Nem sikerült betölteni a karbantartásokat!', 'error');
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
      fetchMaintenances();
    }
  }, [selectedVehicleId, selectedType, isAuthenticated]);

  // Karbantartás törlése
  const handleDelete = async (maintenance: VehicleMaintenance) => {
    const confirmed = await showConfirm(
      `Biztosan törölni szeretnéd ezt a karbantartást?\n\n${maintenance.description} (${new Date(
        maintenance.maintenance_date
      ).toLocaleDateString('hu-HU')})`
    );

    if (!confirmed) return;

    try {
      await deleteVehicleMaintenance(maintenance.id);
      showToast('Karbantartás sikeresen törölve!', 'success');
      fetchMaintenances();
    } catch (error) {
      console.error('Hiba a karbantartás törlésekor:', error);
      showToast('Nem sikerült törölni a karbantartást!', 'error');
    }
  };

  // Típus fordítás
  const getMaintenanceTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      REGULAR_SERVICE: 'Rendszeres szerviz',
      REPAIR: 'Javítás',
      TIRE_CHANGE: 'Gumiabroncs csere',
      OIL_CHANGE: 'Olajcsere',
      BRAKE_SERVICE: 'Fékszerviz',
      MOT: 'Műszaki vizsga',
      OTHER: 'Egyéb',
    };
    return labels[type] || type;
  };

  // Jármű neve ID alapján
  const getVehicleName = (vehicleId: number) => {
    const vehicle = vehicles.find((v) => v.id === vehicleId);
    return vehicle
      ? `${vehicle.brand} ${vehicle.model} (${vehicle.license_plate})`
      : `Jármű #${vehicleId}`;
  };

  return (
    <div className="maintenance-list">
      {/* Fejléc */}
      <div className="list-header">
        <h2>Karbantartások ({maintenances.length})</h2>
        <div className="header-actions">
          <button onClick={fetchMaintenances} className="btn-refresh">
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

          <label>
            Típus:
            <select
              value={selectedType || ''}
              onChange={(e) =>
                setSelectedType(e.target.value || undefined)
              }
            >
              <option value="">Összes típus</option>
              <option value="REGULAR_SERVICE">Rendszeres szerviz</option>
              <option value="REPAIR">Javítás</option>
              <option value="TIRE_CHANGE">Gumiabroncs csere</option>
              <option value="OIL_CHANGE">Olajcsere</option>
              <option value="BRAKE_SERVICE">Fékszerviz</option>
              <option value="MOT">Műszaki vizsga</option>
              <option value="OTHER">Egyéb</option>
            </select>
          </label>
        </div>
      </div>

      {/* Betöltés állapot */}
      {isLoading && <div className="loading-state">Betöltés...</div>}

      {/* Üres állapot */}
      {!isLoading && maintenances.length === 0 && (
        <div className="empty-state">
          <p>Nincs megjeleníthető karbantartás.</p>
        </div>
      )}

      {/* Táblázat */}
      {!isLoading && maintenances.length > 0 && (
        <div className="table-wrapper">
          <table className="maintenance-table">
            <thead>
              <tr>
                <th>Jármű</th>
                <th>Típus</th>
                <th>Dátum</th>
                <th>Km óra</th>
                <th>Leírás</th>
                <th>Költség</th>
                <th>Szerviz</th>
                <th>Műveletek</th>
              </tr>
            </thead>
            <tbody>
              {maintenances.map((maintenance) => (
                <tr key={maintenance.id}>
                  <td>{getVehicleName(maintenance.vehicle_id)}</td>
                  <td>
                    <span className="type-badge">
                      {getMaintenanceTypeLabel(maintenance.maintenance_type)}
                    </span>
                  </td>
                  <td>
                    {new Date(
                      maintenance.maintenance_date
                    ).toLocaleDateString('hu-HU')}
                  </td>
                  <td>
                    {maintenance.mileage?.toLocaleString() || '-'} km
                  </td>
                  <td className="cell-description">
                    {maintenance.description}
                  </td>
                  <td>
                    {maintenance.cost
                      ? `${maintenance.cost.toLocaleString()} Ft`
                      : '-'}
                  </td>
                  <td>{maintenance.service_provider || '-'}</td>
                  <td className="cell-actions">
                    <button
                      onClick={() => handleDelete(maintenance)}
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
