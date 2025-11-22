/**
 * VehicleList - Járművek listázása és kezelése
 *
 * Funkciók:
 *   - Járművek listázása táblázatban
 *   - Új jármű létrehozása (modal nyitás)
 *   - Jármű szerkesztése (modal nyitás)
 *   - Jármű törlése (megerősítéssel)
 *   - Szűrés státusz és üzemanyag típus szerint
 *   - Frissítés gomb
 *   - Figyelmeztetés lejáró biztosításra/műszakira
 */

import { useState, useEffect } from 'react';
import { getVehicles, deleteVehicle } from '@/services/vehicleService';
import { VehicleEditor } from './VehicleEditor';
import type { Vehicle } from '@/types/vehicle';
<<<<<<< HEAD
import { notify } from '@/utils/notifications';
import { useAuthStore } from '@/stores/authStore';
import './VehicleList.css';

export const VehicleList = () => {
  const { isAuthenticated } = useAuthStore();
=======
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './VehicleList.css';

export const VehicleList = () => {
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
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
<<<<<<< HEAD
      notify.error('Nem sikerült betölteni a járműveket!');
=======
      showToast('Nem sikerült betölteni a járműveket!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    if (isAuthenticated) {
      fetchVehicles();
    }
  }, [selectedStatus, selectedFuelType, showOnlyActive, isAuthenticated]);

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
    const confirmed = await showConfirm(
      `Biztosan törölni szeretnéd ezt a járművet?\n\n${vehicle.brand} ${vehicle.model} (${vehicle.license_plate})`
    );

    if (!confirmed) return;

    try {
      await deleteVehicle(vehicle.id);
<<<<<<< HEAD
      notify.success('Jármű sikeresen törölve!');
      fetchVehicles();
    } catch (error) {
      console.error('Hiba a jármű törlésekor:', error);
      notify.error('Nem sikerült törölni a járművet!');
=======
      showToast('Jármű sikeresen törölve!', 'success');
      fetchVehicles();
    } catch (error) {
      console.error('Hiba a jármű törlésekor:', error);
      showToast('Nem sikerült törölni a járművet!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
    }
  };

  // Editor bezárása
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingVehicle(null);

    if (shouldRefresh) {
      fetchVehicles();
    }
  };

  // Státusz szín helper
  const getStatusClass = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'status-active';
      case 'MAINTENANCE':
        return 'status-maintenance';
      case 'OUT_OF_SERVICE':
        return 'status-out-of-service';
      case 'SOLD':
        return 'status-sold';
      case 'RETIRED':
        return 'status-retired';
      default:
        return '';
    }
  };

  // Státusz fordítás
  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      ACTIVE: 'Aktív',
      MAINTENANCE: 'Karbantartás alatt',
      OUT_OF_SERVICE: 'Üzemen kívül',
      SOLD: 'Eladva',
      RETIRED: 'Kivonva',
    };
    return labels[status] || status;
  };

  // Üzemanyag típus fordítás
  const getFuelTypeLabel = (fuelType: string) => {
    const labels: Record<string, string> = {
      PETROL_95: '95-ös benzin',
      PETROL_98: '98-as benzin',
      DIESEL: 'Dízel',
      ELECTRIC: 'Elektromos',
      HYBRID: 'Hibrid',
      LPG: 'LPG',
      CNG: 'CNG',
    };
    return labels[fuelType] || fuelType;
  };

  // Lejárat figyelmeztetés
  const getExpiryWarning = (vehicle: Vehicle) => {
    const today = new Date();
    const warnings: string[] = [];

    if (vehicle.insurance_expiry_date) {
      const expiryDate = new Date(vehicle.insurance_expiry_date);
      const daysUntilExpiry = Math.floor(
        (expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
      );

      if (daysUntilExpiry < 0) {
        warnings.push('Biztosítás lejárt!');
      } else if (daysUntilExpiry <= 30) {
        warnings.push(`Biztosítás lejár ${daysUntilExpiry} napon belül`);
      }
    }

    if (vehicle.mot_expiry_date) {
      const expiryDate = new Date(vehicle.mot_expiry_date);
      const daysUntilExpiry = Math.floor(
        (expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
      );

      if (daysUntilExpiry < 0) {
        warnings.push('Műszaki lejárt!');
      } else if (daysUntilExpiry <= 30) {
        warnings.push(`Műszaki lejár ${daysUntilExpiry} napon belül`);
      }
    }

    return warnings.length > 0 ? warnings.join(' | ') : null;
  };

  return (
    <div className="vehicle-list">
      {/* Fejléc */}
      <div className="list-header">
        <h2>Járművek ({vehicles.length})</h2>
        <div className="header-actions">
          <button onClick={fetchVehicles} className="btn-refresh">
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="btn-create">
            ➕ Új jármű
          </button>
        </div>
      </div>

      {/* Szűrők */}
      <div className="list-filters">
        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={showOnlyActive}
            onChange={(e) => setShowOnlyActive(e.target.checked)}
          />
          <span>Csak aktív járművek</span>
        </label>

        <div className="filter-select-group">
          <label>
            Státusz:
            <select
              value={selectedStatus || ''}
              onChange={(e) =>
                setSelectedStatus(e.target.value || undefined)
              }
            >
              <option value="">Összes</option>
              <option value="ACTIVE">Aktív</option>
              <option value="MAINTENANCE">Karbantartás alatt</option>
              <option value="OUT_OF_SERVICE">Üzemen kívül</option>
              <option value="SOLD">Eladva</option>
              <option value="RETIRED">Kivonva</option>
            </select>
          </label>

          <label>
            Üzemanyag:
            <select
              value={selectedFuelType || ''}
              onChange={(e) =>
                setSelectedFuelType(e.target.value || undefined)
              }
            >
              <option value="">Összes</option>
              <option value="PETROL_95">95-ös benzin</option>
              <option value="PETROL_98">98-as benzin</option>
              <option value="DIESEL">Dízel</option>
              <option value="ELECTRIC">Elektromos</option>
              <option value="HYBRID">Hibrid</option>
              <option value="LPG">LPG</option>
              <option value="CNG">CNG</option>
            </select>
          </label>
        </div>
      </div>

      {/* Betöltés állapot */}
      {isLoading && (
        <div className="loading-state">Betöltés...</div>
      )}

      {/* Üres állapot */}
      {!isLoading && vehicles.length === 0 && (
        <div className="empty-state">
          <p>Nincs megjeleníthető jármű.</p>
          <button onClick={handleCreate} className="btn-create-large">
            ➕ Új jármű létrehozása
          </button>
        </div>
      )}

      {/* Táblázat */}
      {!isLoading && vehicles.length > 0 && (
        <div className="table-wrapper">
          <table className="vehicle-table">
            <thead>
              <tr>
                <th>Rendszám</th>
                <th>Márka</th>
                <th>Modell</th>
                <th>Évjárat</th>
                <th>Üzemanyag</th>
                <th>Km óra</th>
                <th>Státusz</th>
                <th>Biztosítás lejár</th>
                <th>Műszaki lejár</th>
                <th>Műveletek</th>
              </tr>
            </thead>
            <tbody>
              {vehicles.map((vehicle) => {
                const warning = getExpiryWarning(vehicle);
                return (
                  <tr key={vehicle.id} className={warning ? 'row-warning' : ''}>
                    <td className="cell-license-plate">
                      <strong>{vehicle.license_plate}</strong>
                    </td>
                    <td>{vehicle.brand}</td>
                    <td>{vehicle.model}</td>
                    <td>{vehicle.year || '-'}</td>
                    <td>{getFuelTypeLabel(vehicle.fuel_type)}</td>
                    <td>{vehicle.current_mileage?.toLocaleString() || '-'} km</td>
                    <td>
                      <span
                        className={`status-badge ${getStatusClass(
                          vehicle.status
                        )}`}
                      >
                        {getStatusLabel(vehicle.status)}
                      </span>
                    </td>
                    <td>
                      {vehicle.insurance_expiry_date
                        ? new Date(
                            vehicle.insurance_expiry_date
                          ).toLocaleDateString('hu-HU')
                        : '-'}
                    </td>
                    <td>
                      {vehicle.mot_expiry_date
                        ? new Date(
                            vehicle.mot_expiry_date
                          ).toLocaleDateString('hu-HU')
                        : '-'}
                    </td>
                    <td className="cell-actions">
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
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Editor Modal */}
      {isEditorOpen && (
        <VehicleEditor
          vehicle={editingVehicle}
          onClose={handleEditorClose}
        />
      )}
    </div>
  );
};
