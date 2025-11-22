/**
 * AssetServiceList - Szerviz bejegyzések listázása és kezelése
 *
 * Funkciók:
 *   - Szerviz bejegyzések listázása táblázatban
 *   - Új szerviz bejegyzés létrehozása (modal nyitás)
 *   - Szerviz bejegyzés szerkesztése (modal nyitás)
 *   - Szerviz bejegyzés törlése (megerősítéssel)
 *   - Szűrés eszköz és szerviz típus szerint
 *   - Frissítés gomb
 */

import { useState, useEffect } from 'react';
import {
  getAssetServices,
  deleteAssetService,
  getAssets,
} from '@/services/assetService';
import { AssetServiceEditor } from './AssetServiceEditor';
import type { AssetService, Asset } from '@/types/asset';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './AssetServiceList.css';

export const AssetServiceList = () => {
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();
  const [services, setServices] = useState<AssetService[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal állapot
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingService, setEditingService] = useState<AssetService | null>(null);

  // Szűrők
  const [selectedAssetId, setSelectedAssetId] = useState<number | undefined>(
    undefined
  );
  const [selectedServiceType, setSelectedServiceType] = useState<
    string | undefined
  >(undefined);

  // Eszközök betöltése (dropdown-hoz)
  const fetchAssets = async () => {
    try {
      const data = await getAssets({ is_active: true, limit: 500 });
      setAssets(data);
    } catch (error) {
      console.error('Hiba az eszközök betöltésekor:', error);
    }
  };

  // Szerviz bejegyzések betöltése
  const fetchServices = async () => {
    try {
      setIsLoading(true);
      const data = await getAssetServices({
        asset_id: selectedAssetId,
        service_type: selectedServiceType,
        limit: 500,
        offset: 0,
      });
      setServices(data);
    } catch (error) {
      console.error('Hiba a szerviz bejegyzések betöltésekor:', error);
      showToast('Nem sikerült betölteni a szerviz bejegyzéseket!', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    if (isAuthenticated) {
      fetchAssets();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchServices();
    }
  }, [selectedAssetId, selectedServiceType, isAuthenticated]);

  // Új szerviz bejegyzés létrehozása
  const handleCreate = () => {
    setEditingService(null);
    setIsEditorOpen(true);
  };

  // Szerviz bejegyzés szerkesztése
  const handleEdit = (service: AssetService) => {
    setEditingService(service);
    setIsEditorOpen(true);
  };

  // Szerviz bejegyzés törlése
  const handleDelete = async (service: AssetService) => {
    const asset = assets.find((a) => a.id === service.asset_id);
    const confirmed = await showConfirm(
      `Biztosan törölni szeretnéd ezt a szerviz bejegyzést?\n\nEszköz: ${asset?.name || 'Ismeretlen'}\nTípus: ${getServiceTypeLabel(service.service_type)}\nDátum: ${new Date(service.service_date).toLocaleDateString('hu-HU')}`
    );

    if (!confirmed) return;

    try {
      await deleteAssetService(service.id);
      showToast('Szerviz bejegyzés sikeresen törölve!', 'success');
      fetchServices();
    } catch (error) {
      console.error('Hiba a szerviz bejegyzés törlésekor:', error);
      showToast('Nem sikerült törölni a szerviz bejegyzést!', 'error');
    }
  };

  // Editor bezárása
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingService(null);

    if (shouldRefresh) {
      fetchServices();
    }
  };

  // Szerviz típus fordítás
  const getServiceTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      MAINTENANCE: 'Karbantartás',
      REPAIR: 'Javítás',
      INSPECTION: 'Felülvizsgálat',
      CALIBRATION: 'Kalibrálás',
      CLEANING: 'Tisztítás',
    };
    return labels[type] || type;
  };

  return (
    <div className="asset-service-list">
      {/* Fejléc és vezérlők */}
      <div className="list-header">
        <h2>🔧 Szerviz történet</h2>
        <div className="list-controls">
          {/* Eszköz szűrő */}
          <select
            value={selectedAssetId || ''}
            onChange={(e) =>
              setSelectedAssetId(e.target.value ? parseInt(e.target.value) : undefined)
            }
            className="filter-select"
          >
            <option value="">Minden eszköz</option>
            {assets.map((asset) => (
              <option key={asset.id} value={asset.id}>
                {asset.name} ({asset.inventory_number || 'Nincs leltári szám'})
              </option>
            ))}
          </select>

          {/* Szerviz típus szűrő */}
          <select
            value={selectedServiceType || ''}
            onChange={(e) => setSelectedServiceType(e.target.value || undefined)}
            className="filter-select"
          >
            <option value="">Minden típus</option>
            <option value="MAINTENANCE">Karbantartás</option>
            <option value="REPAIR">Javítás</option>
            <option value="INSPECTION">Felülvizsgálat</option>
            <option value="CALIBRATION">Kalibrálás</option>
            <option value="CLEANING">Tisztítás</option>
          </select>

          {/* Frissítés */}
          <button onClick={fetchServices} className="btn-refresh">
            🔄 Frissítés
          </button>

          {/* Új szerviz bejegyzés */}
          <button onClick={handleCreate} className="btn-create">
            ➕ Új szerviz bejegyzés
          </button>
        </div>
      </div>

      {/* Táblázat */}
      {isLoading ? (
        <div className="loading">Betöltés...</div>
      ) : services.length === 0 ? (
        <div className="empty-state">Nincs megjeleníthető szerviz bejegyzés</div>
      ) : (
        <table className="service-table">
          <thead>
            <tr>
              <th>Dátum</th>
              <th>Eszköz</th>
              <th>Típus</th>
              <th>Leírás</th>
              <th>Költség</th>
              <th>Szervizes</th>
              <th>Következő szerviz</th>
              <th>Műveletek</th>
            </tr>
          </thead>
          <tbody>
            {services.map((service) => {
              const asset = assets.find((a) => a.id === service.asset_id);
              return (
                <tr key={service.id}>
                  <td className="service-date">
                    {new Date(service.service_date).toLocaleDateString('hu-HU')}
                  </td>
                  <td className="service-asset">
                    {asset?.name || `Eszköz #${service.asset_id}`}
                  </td>
                  <td className="service-type">
                    <span className="type-badge">
                      {getServiceTypeLabel(service.service_type)}
                    </span>
                  </td>
                  <td className="service-description">{service.description}</td>
                  <td className="service-cost">
                    {service.cost !== null
                      ? `${service.cost.toLocaleString('hu-HU')} Ft`
                      : '-'}
                  </td>
                  <td className="service-provider">
                    {service.service_provider || '-'}
                  </td>
                  <td className="service-next-date">
                    {service.next_service_date
                      ? new Date(service.next_service_date).toLocaleDateString(
                          'hu-HU'
                        )
                      : '-'}
                  </td>
                  <td className="actions">
                    <button
                      onClick={() => handleEdit(service)}
                      className="btn-edit"
                      title="Szerkesztés"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDelete(service)}
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
      )}

      {/* Editor modal */}
      {isEditorOpen && (
        <AssetServiceEditor
          service={editingService}
          assets={assets}
          onClose={handleEditorClose}
        />
      )}
    </div>
  );
};
