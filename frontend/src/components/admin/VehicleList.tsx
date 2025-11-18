/**
 * VehicleList - Járművek listázása és kezelése
 *
 * Funkciók:
 *   - Járművek listázása táblázatban
 *   - Új jármű létrehozása (modal nyitás)
 *   - Jármű szerkesztése (modal nyitás)
 *   - Jármű törlése (megerősítéssel)
 *   - Szűrés státusz és üzemanyag típus szerint
 *   - Figyelmeztetések (lejáró biztosítás, műszaki)
 *   - Frissítés gomb
 */

import { useState, useEffect } from 'react';
import { getVehicles, deleteVehicle } from '@/services/vehicleService';
import { VehicleEditor } from './VehicleEditor';
import type { Vehicle } from '@/types/vehicle';
import './VehicleList.css';

export const VehicleList = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal állapot
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);

  // Szűrők
  const [showOnlyActive, setShowOnlyActive] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>(
    undefined
  );
  const [selectedFuelType, setSelectedFuelType] = useState<string | undefined>(
    undefined
  );

  // Járművek betöltése
  const fetchVehicles = async () => {
    try {
      setIsLoading(true);
      const data = await getVehicles({
        status: selectedStatus,
        fuel_type: selectedFuelType,
        is_active: showOnlyActive ? true : undefined,
        limit: 500,
        offset: 0,
      });
      setVehicles(data);
    } catch (error) {
      console.error('Hiba a járművek betöltésekor:', error);
      alert('Nem sikerült betölteni a járműveket!');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVehicles();
  }, [selectedStatus, selectedFuelType, showOnlyActive]);

  // Új jármű létrehozása
  const handleCreate = () => {
    setEditingVehicle(null);
    setIsEditorOpen(true);
  };

  // Jármű szerkesztése
  const handleEdit = (vehicle: Vehicle) => {
    setEditingVehicle(vehicle);
    setIsEditorOpen(true);
  };

  // Jármű törlése
  const handleDelete = async (vehicle: Vehicle) => {
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt a járművet?\n\n${vehicle.brand} ${vehicle.model} (${vehicle.license_plate})`
    );

    if (!confirmed) return;

    try {
      await deleteVehicle(vehicle.id);
      alert('Jármű sikeresen törölve!');
      fetchVehicles();
    } catch (error) {
      console.error('Hiba a jármű törlésekor:', error);
      alert('Nem sikerült törölni a járművet!');
    }
  };

  // Modal bezárása
  const handleCloseEditor = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingVehicle(null);
    if (shouldRefresh) {
      fetchVehicles();
    }
  };

  // Státusz badge szín
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'ACTIVE':
        return 'green';
      case 'MAINTENANCE':
        return 'orange';
      case 'OUT_OF_SERVICE':
        return 'red';
      case 'SOLD':
        return 'gray';
      case 'RETIRED':
        return 'gray';
      default:
        return 'gray';
    }
  };

  // Státusz fordítás
  const translateStatus = (status: string): string => {
    switch (status) {
      case 'ACTIVE':
        return 'Használatban';
      case 'MAINTENANCE':
        return 'Karbantartás alatt';
      case 'OUT_OF_SERVICE':
        return 'Nem üzemképes';
      case 'SOLD':
        return 'Eladva';
      case 'RETIRED':
        return 'Kivonva';
      default:
        return status;
    }
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

  // Lejárati figyelmeztetés ellenőrzése
  const checkExpiry = (expiryDate: string | null): boolean => {
    if (!expiryDate) return false;
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffDays = Math.floor(
      (expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
    );
    return diffDays <= 30 && diffDays >= 0; // 30 napon belül lejár
  };

  return (
    <div className="vehicle-list-container">
      {/* Felső toolbar */}
      <div className="vehicle-list-toolbar">
        <div className="toolbar-left">
          <button onClick={handleCreate} className="btn-create">
            + Új jármű
          </button>
          <button onClick={fetchVehicles} className="btn-refresh">
            Frissítés
          </button>
        </div>

        <div className="toolbar-right">
          {/* Státusz szűrő */}
          <select
            value={selectedStatus || ''}
            onChange={(e) =>
              setSelectedStatus(e.target.value || undefined)
            }
            className="filter-select"
          >
            <option value="">Összes státusz</option>
            <option value="ACTIVE">Használatban</option>
            <option value="MAINTENANCE">Karbantartás alatt</option>
            <option value="OUT_OF_SERVICE">Nem üzemképes</option>
            <option value="SOLD">Eladva</option>
            <option value="RETIRED">Kivonva</option>
          </select>

          {/* Üzemanyag típus szűrő */}
          <select
            value={selectedFuelType || ''}
            onChange={(e) =>
              setSelectedFuelType(e.target.value || undefined)
            }
            className="filter-select"
          >
            <option value="">Összes üzemanyag</option>
            <option value="PETROL_95">95-ös benzin</option>
            <option value="PETROL_98">98-as benzin</option>
            <option value="DIESEL">Dízel</option>
            <option value="ELECTRIC">Elektromos</option>
            <option value="HYBRID">Hibrid</option>
            <option value="LPG">Gázolaj (LPG)</option>
          </select>

          {/* Csak aktív */}
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={showOnlyActive}
              onChange={(e) => setShowOnlyActive(e.target.checked)}
            />
            Csak aktív
          </label>
        </div>
      </div>

      {/* Táblázat */}
      {isLoading ? (
        <div className="loading-state">Betöltés...</div>
      ) : vehicles.length === 0 ? (
        <div className="empty-state">
          Nincs megjeleníthető jármű. Hozz létre egyet!
        </div>
      ) : (
        <div className="table-container">
          <table className="vehicle-table">
            <thead>
              <tr>
                <th>Rendszám</th>
                <th>Márka & Modell</th>
                <th>Év</th>
                <th>Üzemanyag</th>
                <th>Km állás</th>
                <th>Státusz</th>
                <th>Biztosítás</th>
                <th>Műszaki</th>
                <th>Műveletek</th>
              </tr>
            </thead>
            <tbody>
              {vehicles.map((vehicle) => (
                <tr key={vehicle.id}>
                  <td>
                    <strong>{vehicle.license_plate}</strong>
                  </td>
                  <td>
                    {vehicle.brand} {vehicle.model}
                  </td>
                  <td>{vehicle.year || '-'}</td>
                  <td>{translateFuelType(vehicle.fuel_type)}</td>
                  <td>
                    {vehicle.current_mileage
                      ? `${vehicle.current_mileage.toLocaleString()} km`
                      : '-'}
                  </td>
                  <td>
                    <span
                      className="status-badge"
                      style={{
                        backgroundColor: getStatusColor(vehicle.status),
                      }}
                    >
                      {translateStatus(vehicle.status)}
                    </span>
                  </td>
                  <td>
                    {vehicle.insurance_expiry_date ? (
                      <span
                        className={
                          checkExpiry(vehicle.insurance_expiry_date)
                            ? 'expiry-warning'
                            : ''
                        }
                      >
                        {vehicle.insurance_expiry_date}
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>
                    {vehicle.mot_expiry_date ? (
                      <span
                        className={
                          checkExpiry(vehicle.mot_expiry_date)
                            ? 'expiry-warning'
                            : ''
                        }
                      >
                        {vehicle.mot_expiry_date}
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        onClick={() => handleEdit(vehicle)}
                        className="btn-edit"
                        title="Szerkesztés"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDelete(vehicle)}
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
        <VehicleEditor
          vehicle={editingVehicle}
          onClose={handleCloseEditor}
        />
      )}
    </div>
  );
};
