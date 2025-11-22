/**
 * AssetGroupList - Eszközcsoportok listázása és kezelése
 *
 * Funkciók:
 *   - Eszközcsoportok listázása táblázatban
 *   - Új eszközcsoport létrehozása (modal nyitás)
 *   - Eszközcsoport szerkesztése (modal nyitás)
 *   - Eszközcsoport törlése (megerősítéssel)
 *   - Frissítés gomb
 *   - Szűrés (aktív/inaktív eszközcsoportok)
 */

import { useState, useEffect } from 'react';
import { getAssetGroups, deleteAssetGroup } from '@/services/assetService';
import { AssetGroupEditor } from './AssetGroupEditor';
import type { AssetGroup } from '@/types/asset';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './AssetGroupList.css';

export const AssetGroupList = () => {
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();
  const [assetGroups, setAssetGroups] = useState<AssetGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingAssetGroup, setEditingAssetGroup] = useState<AssetGroup | null>(null);

  // Szűrő állapot
  const [showOnlyActive, setShowOnlyActive] = useState(true);

  // Eszközcsoportok betöltése
  const fetchAssetGroups = async () => {
    try {
      setIsLoading(true);
      const data = await getAssetGroups({
        is_active: showOnlyActive ? true : undefined,
        limit: 500,
        offset: 0,
      });
      setAssetGroups(data);
    } catch (error) {
      console.error('Hiba az eszközcsoportok betöltésekor:', error);
      showToast('Nem sikerült betölteni az eszközcsoportokat!', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    fetchAssetGroups();
  }, [showOnlyActive]);

  // Új eszközcsoport létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingAssetGroup(null);
    setIsEditorOpen(true);
  };

  // Eszközcsoport szerkesztése (modal nyitás)
  const handleEdit = (group: AssetGroup) => {
    setEditingAssetGroup(group);
    setIsEditorOpen(true);
  };

  // Eszközcsoport törlése (megerősítéssel)
  const handleDelete = async (group: AssetGroup) => {
    const confirmed = await showConfirm(
      `Biztosan törölni szeretnéd ezt az eszközcsoportot?\n\n${group.name}`
    );

    if (!confirmed) return;

    try {
      await deleteAssetGroup(group.id);
      showToast('Eszközcsoport sikeresen törölve!', 'success');
      fetchAssetGroups(); // Lista frissítése
    } catch (error) {
      console.error('Hiba az eszközcsoport törlésekor:', error);
      showToast('Nem sikerült törölni az eszközcsoportot!', 'error');
    }
  };

  // Editor bezárása (frissítéssel vagy anélkül)
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingAssetGroup(null);

    if (shouldRefresh) {
      fetchAssetGroups();
    }
  };

  return (
    <div className="asset-group-list">
      {/* Fejléc és vezérlők */}
      <div className="list-header">
        <h2>📁 Eszközcsoportok</h2>
        <div className="list-controls">
          {/* Szűrő kapcsoló */}
          <label className="filter-toggle">
            <input
              type="checkbox"
              checked={showOnlyActive}
              onChange={(e) => setShowOnlyActive(e.target.checked)}
            />
            <span>Csak aktívak</span>
          </label>

          {/* Frissítés gomb */}
          <button onClick={fetchAssetGroups} className="btn-refresh">
            🔄 Frissítés
          </button>

          {/* Új eszközcsoport gomb */}
          <button onClick={handleCreate} className="btn-create">
            ➕ Új eszközcsoport
          </button>
        </div>
      </div>

      {/* Táblázat */}
      {isLoading ? (
        <div className="loading">Betöltés...</div>
      ) : assetGroups.length === 0 ? (
        <div className="empty-state">Nincs megjeleníthető eszközcsoport</div>
      ) : (
        <table className="asset-group-table">
          <thead>
            <tr>
              <th>Név</th>
              <th>Leírás</th>
              <th>Amortizáció (%/év)</th>
              <th>Várható élettartam (év)</th>
              <th>Státusz</th>
              <th>Műveletek</th>
            </tr>
          </thead>
          <tbody>
            {assetGroups.map((group) => (
              <tr key={group.id}>
                <td className="group-name">{group.name}</td>
                <td className="group-description">
                  {group.description || '-'}
                </td>
                <td className="group-depreciation">
                  {group.depreciation_rate !== null
                    ? `${group.depreciation_rate}%`
                    : '-'}
                </td>
                <td className="group-lifetime">
                  {group.expected_lifetime_years !== null
                    ? `${group.expected_lifetime_years} év`
                    : '-'}
                </td>
                <td>
                  <span
                    className={`status-badge ${
                      group.is_active ? 'active' : 'inactive'
                    }`}
                  >
                    {group.is_active ? 'Aktív' : 'Inaktív'}
                  </span>
                </td>
                <td className="actions">
                  <button
                    onClick={() => handleEdit(group)}
                    className="btn-edit"
                    title="Szerkesztés"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() => handleDelete(group)}
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
      )}

      {/* Editor modal */}
      {isEditorOpen && (
        <AssetGroupEditor
          assetGroup={editingAssetGroup}
          onClose={handleEditorClose}
        />
      )}
    </div>
  );
};
