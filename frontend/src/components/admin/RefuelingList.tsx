/**
 * RefuelingList - Tankolások listázása és kezelése
 *
 * Funkciók:
 *   - Tankolások listázása táblázatban
 *   - Új tankolás rögzítése (modal nyitás)
 *   - Tankolás szerkesztése (modal nyitás)
 *   - Tankolás törlése (megerősítéssel)
 *   - Szűrés jármű szerint
 *   - Frissítés gomb
 */

import { useState, useEffect } from 'react';
import {
  getRefuelings,
  deleteRefueling,
  getVehicles,
} from '@/services/vehicleService';
import { RefuelingEditor } from './RefuelingEditor';
import type { VehicleRefueling, Vehicle } from '@/types/vehicle';
import './RefuelingList.css';

export const RefuelingList = () => {
  const [refuelings, setRefuelings] = useState<VehicleRefueling[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal állapot
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingRefueling, setEditingRefueling] = useState<VehicleRefueling | null>(null);

  // Szűrők
  const [selectedVehicleId, setSelectedVehicleId] = useState<number | undefined>(
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

  // Tankolások betöltése
  const fetchRefuelings = async () => {
    try {
      setIsLoading(true);
      const data = await getRefuelings({
        vehicle_id: selectedVehicleId,
        limit: 500,
        offset: 0,
      });
      setRefuelings(data);
    } catch (error) {
      console.error('Hiba a tankolások betöltésekor:', error);
      alert('Nem sikerült betölteni a tankolásokat!');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    fetchVehicles();
  }, []);

  useEffect(() => {
    fetchRefuelings();
  }, [selectedVehicleId]);

  // Új tankolás létrehozása
  const handleCreate = () => {
    setEditingRefueling(null);
    setIsEditorOpen(true);
  };

  // Tankolás szerkesztése
  const handleEdit = (refueling: VehicleRefueling) => {
    setEditingRefueling(refueling);
    setIsEditorOpen(true);
  };

  // Tankolás törlése
  const handleDelete = async (refueling: VehicleRefueling) => {
    const vehicle = vehicles.find(v => v.id === refueling.vehicle_id);
    const vehicleName = vehicle ? `${vehicle.brand} ${vehicle.model} (${vehicle.license_plate})` : `Jármű #${refueling.vehicle_id}`;

    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt a tankolást?\n\n${vehicleName}\nDátum: ${refueling.refueling_date}\nÖsszeg: ${refueling.total_cost} Ft`
    );

    if (!confirmed) return;

    try {
      await deleteRefueling(refueling.id);
      alert('Tankolás sikeresen törölve!');
      fetchRefuelings();
    } catch (error) {
      console.error('Hiba a tankolás törlésekor:', error);
      alert('Nem sikerült törölni a tankolást!');
    }
  };

  // Modal bezárása
  const handleCloseEditor = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingRefueling(null);
    if (shouldRefresh) {
      fetchRefuelings();
    }
  };

  // Jármű neve
  const getVehicleName = (vehicleId: number): string => {
    const vehicle = vehicles.find(v => v.id === vehicleId);
    return vehicle ? `${vehicle.brand} ${vehicle.model} (${vehicle.license_plate})` : `Jármű #${vehicleId}`;
  };

  // Üzemanyag típus fordítás
  const translateFuelType = (fuelType: string): string => {
    switch (fuelType) {
      case 'PETROL_95':
        return '95-ös benzin';
      case 'PETROL_98':
        return '98-as benzin';
      case 'DIESEL':
        return 'Dízel';
      case 'ELECTRIC':
        return 'Elektromos';
      case 'HYBRID':
        return 'Hibrid';
      case 'LPG':
        return 'Gázolaj (LPG)';
      default:
        return fuelType;
    }
  };

  return (
    <div className="refueling-list-container">
      {/* Felső toolbar */}
      <div className="refueling-list-toolbar">
        <div className="toolbar-left">
          <button onClick={handleCreate} className="btn-create">
            + Új tankolás
          </button>
          <button onClick={fetchRefuelings} className="btn-refresh">
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
        </div>
      </div>

      {/* Táblázat */}
      {isLoading ? (
        <div className="loading-state">Betöltés...</div>
      ) : refuelings.length === 0 ? (
        <div className="empty-state">
          Nincs megjeleníthető tankolás. Rögzíts egyet!
        </div>
      ) : (
        <div className="table-container">
          <table className="refueling-table">
            <thead>
              <tr>
                <th>Dátum</th>
                <th>Jármű</th>
                <th>Üzemanyag</th>
                <th>Mennyiség (L)</th>
                <th>Ár/L (Ft)</th>
                <th>Összesen (Ft)</th>
                <th>Km állás</th>
                <th>Helyszín</th>
                <th>Műveletek</th>
              </tr>
            </thead>
            <tbody>
              {refuelings.map((refueling) => (
                <tr key={refueling.id}>
                  <td>{refueling.refueling_date}</td>
                  <td>{getVehicleName(refueling.vehicle_id)}</td>
                  <td>{translateFuelType(refueling.fuel_type)}</td>
                  <td>{refueling.quantity_liters.toLocaleString()} L</td>
                  <td>{refueling.price_per_liter.toLocaleString()} Ft</td>
                  <td>
                    <strong>{refueling.total_cost.toLocaleString()} Ft</strong>
                  </td>
                  <td>{refueling.mileage ? `${refueling.mileage.toLocaleString()} km` : '-'}</td>
                  <td>{refueling.location || '-'}</td>
                  <td>
                    <div className="action-buttons">
                      <button
                        onClick={() => handleEdit(refueling)}
                        className="btn-edit"
                        title="Szerkesztés"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDelete(refueling)}
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
        <RefuelingEditor
          refueling={editingRefueling}
          vehicles={vehicles}
          onClose={handleCloseEditor}
        />
      )}
    </div>
  );
};
