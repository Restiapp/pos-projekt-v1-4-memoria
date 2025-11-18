/**
 * MaintenanceList - Karbantartások listázása és kezelése
 *
 * Funkciók:
 *   - Karbantartások listázása táblázatban
 *   - Új karbantartás rögzítése (modal nyitás)
 *   - Karbantartás szerkesztése (modal nyitás)
 *   - Karbantartás törlése (megerősítéssel)
 *   - Szűrés jármű és típus szerint
 *   - Frissítés gomb
 */

import { useState, useEffect } from 'react';
import {
  getMaintenances,
  deleteMaintenance,
  getVehicles,
} from '@/services/vehicleService';
import { MaintenanceEditor } from './MaintenanceEditor';
import type { VehicleMaintenance, Vehicle } from '@/types/vehicle';
import './MaintenanceList.css';

export const MaintenanceList = () => {
  const [maintenances, setMaintenances] = useState<VehicleMaintenance[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal állapot
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingMaintenance, setEditingMaintenance] = useState<VehicleMaintenance | null>(null);

  // Szűrők
  const [selectedVehicleId, setSelectedVehicleId] = useState<number | undefined>(
    undefined
  );
  const [selectedMaintenanceType, setSelectedMaintenanceType] = useState<string | undefined>(
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
      const data = await getMaintenances({
        vehicle_id: selectedVehicleId,
        maintenance_type: selectedMaintenanceType,
        limit: 500,
        offset: 0,
      });
      setMaintenances(data);
    } catch (error) {
      console.error('Hiba a karbantartások betöltésekor:', error);
      alert('Nem sikerült betölteni a karbantartásokat!');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    fetchVehicles();
  }, []);

  useEffect(() => {
    fetchMaintenances();
  }, [selectedVehicleId, selectedMaintenanceType]);

  // Új karbantartás létrehozása
  const handleCreate = () => {
    setEditingMaintenance(null);
    setIsEditorOpen(true);
  };

  // Karbantartás szerkesztése
  const handleEdit = (maintenance: VehicleMaintenance) => {
    setEditingMaintenance(maintenance);
    setIsEditorOpen(true);
  };

  // Karbantartás törlése
  const handleDelete = async (maintenance: VehicleMaintenance) => {
    const vehicle = vehicles.find(v => v.id === maintenance.vehicle_id);
    const vehicleName = vehicle ? `${vehicle.brand} ${vehicle.model} (${vehicle.license_plate})` : `Jármű #${maintenance.vehicle_id}`;

    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt a karbantartást?\n\n${vehicleName}\nDátum: ${maintenance.maintenance_date}\nTípus: ${translateMaintenanceType(maintenance.maintenance_type)}`
    );

    if (!confirmed) return;

    try {
      await deleteMaintenance(maintenance.id);
      alert('Karbantartás sikeresen törölve!');
      fetchMaintenances();
    } catch (error) {
      console.error('Hiba a karbantartás törlésekor:', error);
      alert('Nem sikerült törölni a karbantartást!');
    }
  };

  // Modal bezárása
  const handleCloseEditor = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingMaintenance(null);
    if (shouldRefresh) {
      fetchMaintenances();
    }
  };

  // Jármű neve
  const getVehicleName = (vehicleId: number): string => {
    const vehicle = vehicles.find(v => v.id === vehicleId);
    return vehicle ? `${vehicle.brand} ${vehicle.model} (${vehicle.license_plate})` : `Jármű #${vehicleId}`;
  };

  // Karbantartás típus fordítás
  const translateMaintenanceType = (type: string): string => {
    switch (type) {
      case 'REGULAR_SERVICE':
        return 'Rendszeres szerviz';
      case 'REPAIR':
        return 'Javítás';
      case 'TIRE_CHANGE':
        return 'Gumicsere';
      case 'OIL_CHANGE':
        return 'Olajcsere';
      case 'BRAKE_SERVICE':
        return 'Fékszerviz';
      case 'MOT':
        return 'Műszaki vizsga';
      case 'OTHER':
        return 'Egyéb';
      default:
        return type;
    }
  };

  return (
    <div className="maintenance-list-container">
      {/* Felső toolbar */}
      <div className="maintenance-list-toolbar">
        <div className="toolbar-left">
          <button onClick={handleCreate} className="btn-create">
            + Új karbantartás
          </button>
          <button onClick={fetchMaintenances} className="btn-refresh">
            Frissítés
          </button>
        </div>

        <div className="toolbar-right">
          {/* Jármű szűrő */}
          <select
            value={selectedVehicleId || ''}
            onChange={(e) =>
              setSelectedVehicleId(e.target.value ? parseInt(e.target.value) : undefined)
            }
            className="filter-select"
          >
            <option value="">Összes jármű</option>
            {vehicles.map((vehicle) => (
              <option key={vehicle.id} value={vehicle.id}>
                {vehicle.brand} {vehicle.model} ({vehicle.license_plate})
              </option>
            ))}
          </select>

          {/* Típus szűrő */}
          <select
            value={selectedMaintenanceType || ''}
            onChange={(e) =>
              setSelectedMaintenanceType(e.target.value || undefined)
            }
            className="filter-select"
          >
            <option value="">Összes típus</option>
            <option value="REGULAR_SERVICE">Rendszeres szerviz</option>
            <option value="REPAIR">Javítás</option>
            <option value="TIRE_CHANGE">Gumicsere</option>
            <option value="OIL_CHANGE">Olajcsere</option>
            <option value="BRAKE_SERVICE">Fékszerviz</option>
            <option value="MOT">Műszaki vizsga</option>
            <option value="OTHER">Egyéb</option>
          </select>
        </div>
      </div>

      {/* Táblázat */}
      {isLoading ? (
        <div className="loading-state">Betöltés...</div>
      ) : maintenances.length === 0 ? (
        <div className="empty-state">
          Nincs megjeleníthető karbantartás. Rögzíts egyet!
        </div>
      ) : (
        <div className="table-container">
          <table className="maintenance-table">
            <thead>
              <tr>
                <th>Dátum</th>
                <th>Jármű</th>
                <th>Típus</th>
                <th>Leírás</th>
                <th>Költség (Ft)</th>
                <th>Km állás</th>
                <th>Szerviz</th>
                <th>Következő szerviz</th>
                <th>Műveletek</th>
              </tr>
            </thead>
            <tbody>
              {maintenances.map((maintenance) => (
                <tr key={maintenance.id}>
                  <td>{maintenance.maintenance_date}</td>
                  <td>{getVehicleName(maintenance.vehicle_id)}</td>
                  <td>{translateMaintenanceType(maintenance.maintenance_type)}</td>
                  <td>{maintenance.description}</td>
                  <td>
                    {maintenance.cost ? (
                      <strong>{maintenance.cost.toLocaleString()} Ft</strong>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>{maintenance.mileage ? `${maintenance.mileage.toLocaleString()} km` : '-'}</td>
                  <td>{maintenance.service_provider || '-'}</td>
                  <td>
                    {maintenance.next_maintenance_date ? (
                      <>
                        {maintenance.next_maintenance_date}
                        {maintenance.next_maintenance_mileage && (
                          <> ({maintenance.next_maintenance_mileage.toLocaleString()} km)</>
                        )}
                      </>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        onClick={() => handleEdit(maintenance)}
                        className="btn-edit"
                        title="Szerkesztés"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDelete(maintenance)}
                        className="btn-delete"
                        title="Törlés"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {isEditorOpen && (
        <MaintenanceEditor
          maintenance={editingMaintenance}
          vehicles={vehicles}
          onClose={handleCloseEditor}
        />
      )}
    </div>
  );
};
