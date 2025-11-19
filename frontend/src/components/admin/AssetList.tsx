/**
 * AssetList - Eszközök listázása és kezelése
 *
 * Funkciók:
 *   - Eszközök listázása táblázatban
 *   - Új eszköz létrehozása (modal nyitás)
 *   - Eszköz szerkesztése (modal nyitás)
 *   - Eszköz törlése (megerősítéssel)
 *   - Szűrés eszközcsoport és státusz szerint
 *   - Frissítés gomb
 */

import { useState, useEffect } from 'react';
import {
  getAssets,
  deleteAsset,
  getAssetGroups,
} from '@/services/assetService';
import { AssetEditor } from './AssetEditor';
import type { Asset, AssetGroup } from '@/types/asset';
import { notify } from '@/utils/notifications';
import { useAuthStore } from '@/stores/authStore';
import './AssetList.css';

export const AssetList = () => {
  const { isAuthenticated } = useAuthStore();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [assetGroups, setAssetGroups] = useState<AssetGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal állapot
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);

  // Szűrők
  const [showOnlyActive, setShowOnlyActive] = useState(true);
  const [selectedGroupId, setSelectedGroupId] = useState<number | undefined>(
    undefined
  );
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>(
    undefined
  );

  // Eszközcsoportok betöltése (dropdown-hoz)
  const fetchAssetGroups = async () => {
    try {
      const data = await getAssetGroups({ is_active: true, limit: 500 });
      setAssetGroups(data);
    } catch (error) {
      console.error('Hiba az eszközcsoportok betöltésekor:', error);
    }
  };

  // Eszközök betöltése
  const fetchAssets = async () => {
    try {
      setIsLoading(true);
      const data = await getAssets({
        asset_group_id: selectedGroupId,
        status: selectedStatus,
        is_active: showOnlyActive ? true : undefined,
        limit: 500,
        offset: 0,
      });
      setAssets(data);
    } catch (error) {
      console.error('Hiba az eszközök betöltésekor:', error);
      notify.error('Nem sikerült betölteni az eszközöket!');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    if (isAuthenticated) {
      fetchAssetGroups();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchAssets();
    }
  }, [selectedGroupId, selectedStatus, showOnlyActive, isAuthenticated]);

  // Új eszköz létrehozása
  const handleCreate = () => {
    setEditingAsset(null);
    setIsEditorOpen(true);
  };

  // Eszköz szerkesztése
  const handleEdit = (asset: Asset) => {
    setEditingAsset(asset);
    setIsEditorOpen(true);
  };

  // Eszköz törlése
  const handleDelete = async (asset: Asset) => {
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt az eszközt?\n\n${asset.name} (${asset.inventory_number || 'Nincs leltári szám'})`
    );

    if (!confirmed) return;

    try {
      await deleteAsset(asset.id);
      notify.success('Eszköz sikeresen törölve!');
      fetchAssets();
    } catch (error) {
      console.error('Hiba az eszköz törlésekor:', error);
      notify.error('Nem sikerült törölni az eszközt!');
    }
  };

  // Editor bezárása
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingAsset(null);

    if (shouldRefresh) {
      fetchAssets();
    }
  };

  // Státusz szín helper
  const getStatusClass = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'status-active';
      case 'MAINTENANCE':
        return 'status-maintenance';
      case 'RETIRED':
        return 'status-retired';
      case 'SOLD':
        return 'status-sold';
      case 'DAMAGED':
        return 'status-damaged';
      default:
        return '';
    }
  };

  // Státusz fordítás
  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      ACTIVE: 'Aktív',
      MAINTENANCE: 'Karbantartás',
      RETIRED: 'Kivonva',
      SOLD: 'Eladva',
      DAMAGED: 'Sérült',
    };
    return labels[status] || status;
  };

  return (
    <div className="asset-list">
      {/* Fejléc és vezérlők */}
      <div className="list-header">
        <h2>📦 Eszközök</h2>
        <div className="list-controls">
          {/* Eszközcsoport szűrő */}
          <select
            value={selectedGroupId || ''}
            onChange={(e) =>
              setSelectedGroupId(e.target.value ? parseInt(e.target.value) : undefined)
            }
            className="filter-select"
          >
            <option value="">Minden eszközcsoport</option>
            {assetGroups.map((group) => (
              <option key={group.id} value={group.id}>
                {group.name}
              </option>
            ))}
          </select>

          {/* Státusz szűrő */}
          <select
            value={selectedStatus || ''}
            onChange={(e) => setSelectedStatus(e.target.value || undefined)}
            className="filter-select"
          >
            <option value="">Minden státusz</option>
            <option value="ACTIVE">Aktív</option>
            <option value="MAINTENANCE">Karbantartás</option>
            <option value="RETIRED">Kivonva</option>
            <option value="SOLD">Eladva</option>
            <option value="DAMAGED">Sérült</option>
          </select>

          {/* Aktív/inaktív kapcsoló */}
          <label className="filter-toggle">
            <input
              type="checkbox"
              checked={showOnlyActive}
              onChange={(e) => setShowOnlyActive(e.target.checked)}
            />
            <span>Csak aktívak</span>
          </label>

          {/* Frissítés */}
          <button onClick={fetchAssets} className="btn-refresh">
            🔄 Frissítés
          </button>

          {/* Új eszköz */}
          <button onClick={handleCreate} className="btn-create">
            ➕ Új eszköz
          </button>
        </div>
      </div>

      {/* Táblázat */}
      {isLoading ? (
        <div className="loading">Betöltés...</div>
      ) : assets.length === 0 ? (
        <div className="empty-state">Nincs megjeleníthető eszköz</div>
      ) : (
        <table className="asset-table">
          <thead>
            <tr>
              <th>Leltári szám</th>
              <th>Név</th>
              <th>Eszközcsoport</th>
              <th>Gyártó/Modell</th>
              <th>Helyszín</th>
              <th>Beszerzési dátum</th>
              <th>Beszerzési ár</th>
              <th>Jelenlegi érték</th>
              <th>Státusz</th>
              <th>Műveletek</th>
            </tr>
          </thead>
          <tbody>
            {assets.map((asset) => {
              const group = assetGroups.find((g) => g.id === asset.asset_group_id);
              return (
                <tr key={asset.id}>
                  <td className="asset-inventory">
                    {asset.inventory_number || '-'}
                  </td>
                  <td className="asset-name">{asset.name}</td>
                  <td className="asset-group">{group?.name || '-'}</td>
                  <td className="asset-manufacturer">
                    {asset.manufacturer || '-'}
                    {asset.model && ` / ${asset.model}`}
                  </td>
                  <td className="asset-location">{asset.location || '-'}</td>
                  <td className="asset-purchase-date">
                    {asset.purchase_date
                      ? new Date(asset.purchase_date).toLocaleDateString('hu-HU')
                      : '-'}
                  </td>
                  <td className="asset-purchase-price">
                    {asset.purchase_price !== null
                      ? `${asset.purchase_price.toLocaleString('hu-HU')} Ft`
                      : '-'}
                  </td>
                  <td className="asset-current-value">
                    {asset.current_value !== null
                      ? `${asset.current_value.toLocaleString('hu-HU')} Ft`
                      : '-'}
                  </td>
                  <td>
                    <span className={`status-badge ${getStatusClass(asset.status)}`}>
                      {getStatusLabel(asset.status)}
                    </span>
                  </td>
                  <td className="actions">
                    <button
                      onClick={() => handleEdit(asset)}
                      className="btn-edit"
                      title="Szerkesztés"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDelete(asset)}
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
        <AssetEditor
          asset={editingAsset}
          assetGroups={assetGroups}
          onClose={handleEditorClose}
        />
      )}
    </div>
  );
};
