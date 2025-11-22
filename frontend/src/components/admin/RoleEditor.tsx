/**
 * RoleEditor - Szerepkör létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új szerepkör létrehozása (POST /api/roles)
 *   - Meglévő szerepkör szerkesztése (PUT /api/roles/{id})
 *   - Validáció (név, leírás kötelező)
 *   - Jogosultságok kiválasztása (multi-select checkbox lista)
 *   - Modal overlay (háttérre kattintva bezárás)
 */

import { useState } from 'react';
import { createRole, updateRole } from '@/services/roleService';
import type { RoleWithPermissions, Permission, RoleCreate, RoleUpdate } from '@/types/role';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './RoleEditor.css';

interface RoleEditorProps {
  role: RoleWithPermissions | null; // null = új szerepkör, RoleWithPermissions = szerkesztés
  permissions: Permission[];
  onClose: (shouldRefresh: boolean) => void;
}

export const RoleEditor = ({ role, permissions, onClose }: RoleEditorProps) => {
  const isEditing = !!role; // true = szerkesztés, false = új létrehozás
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();

  // Form állapot
  const [formData, setFormData] = useState({
    name: role?.name || '',
    description: role?.description || '',
  });

  // Kiválasztott jogosultságok ID-i
  const [selectedPermissionIds, setSelectedPermissionIds] = useState<number[]>(
    role?.permissions.map((p) => p.id) || []
  );

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Jogosultság checkbox változás
  const handlePermissionToggle = (permissionId: number) => {
    setSelectedPermissionIds((prev) =>
      prev.includes(permissionId)
        ? prev.filter((id) => id !== permissionId) // Eltávolítás
        : [...prev, permissionId] // Hozzáadás
    );
  };

  // Összes jogosultság kiválasztása/eltávolítása
  const handleSelectAll = () => {
    if (selectedPermissionIds.length === permissions.length) {
      // Ha mind ki van választva, akkor töröljük
      setSelectedPermissionIds([]);
    } else {
      // Különben kiválasztjuk mindet
      setSelectedPermissionIds(permissions.map((p) => p.id));
    }
  };

  // Form submit (létrehozás / frissítés)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (!formData.name.trim()) {
      showToast('A szerepkör neve kötelező!', 'error');
      return;
    }

    if (!formData.description.trim()) {
      showToast('A leírás kötelező!', 'error');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing && role) {
        // Frissítés
        const updateData: RoleUpdate = {
          name: formData.name,
          description: formData.description,
          permission_ids: selectedPermissionIds,
        };

        await updateRole(role.id, updateData);
        showToast('Szerepkör sikeresen frissítve!', 'success');
      } else {
        // Létrehozás
        const createData: RoleCreate = {
          name: formData.name,
          description: formData.description,
          permission_ids: selectedPermissionIds,
        };

        await createRole(createData);
        showToast('Szerepkör sikeresen létrehozva!', 'success');
      }

      onClose(true); // Bezárás + lista frissítése
    } catch (error: any) {
      console.error('Hiba a szerepkör mentésekor:', error);
      const errorMessage =
        error.response?.data?.detail || 'Nem sikerült menteni a szerepkört!';
      showToast(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Modal overlay kattintás (háttérre kattintva bezárás)
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose(false);
    }
  };

  // Jogosultságok csoportosítása resource alapján
  const groupedPermissions = permissions.reduce((acc, permission) => {
    if (!acc[permission.resource]) {
      acc[permission.resource] = [];
    }
    acc[permission.resource].push(permission);
    return acc;
  }, {} as Record<string, Permission[]>);

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content role-editor-modal">
        <header className="modal-header">
          <h2>{isEditing ? '✏️ Szerepkör szerkesztése' : '➕ Új szerepkör'}</h2>
          <button onClick={() => onClose(false)} className="close-btn">
            ✕
          </button>
        </header>

        <form onSubmit={handleSubmit} className="role-form">
          {/* Név */}
          <div className="form-group">
            <label htmlFor="name">
              Név <span className="required">*</span>
            </label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="pl. Admin, Manager, Waiter"
              required
              maxLength={100}
            />
          </div>

          {/* Leírás */}
          <div className="form-group">
            <label htmlFor="description">
              Leírás <span className="required">*</span>
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="pl. Rendszergazda - teljes hozzáférés"
              required
              maxLength={255}
              rows={3}
            />
          </div>

          {/* Jogosultságok */}
          <div className="form-group permissions-group">
            <div className="permissions-header">
              <label>Jogosultságok</label>
              <button
                type="button"
                onClick={handleSelectAll}
                className="select-all-btn"
              >
                {selectedPermissionIds.length === permissions.length
                  ? '❌ Összes törlése'
                  : '✅ Összes kiválasztása'}
              </button>
            </div>

            <div className="permissions-container">
              {Object.keys(groupedPermissions).length === 0 ? (
                <p className="no-permissions">Nincsenek elérhető jogosultságok</p>
              ) : (
                Object.entries(groupedPermissions).map(([resource, perms]) => (
                  <div key={resource} className="permission-group">
                    <h4 className="resource-title">{resource}</h4>
                    <div className="permission-checkboxes">
                      {perms.map((permission) => (
                        <label
                          key={permission.id}
                          className="permission-checkbox"
                        >
                          <input
                            type="checkbox"
                            checked={selectedPermissionIds.includes(permission.id)}
                            onChange={() => handlePermissionToggle(permission.id)}
                          />
                          <div className="permission-info">
                            <span className="permission-name">{permission.name}</span>
                            <span className="permission-description">
                              {permission.description}
                            </span>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>

            <small className="field-hint">
              Kiválasztva: {selectedPermissionIds.length} / {permissions.length} jogosultság
            </small>
          </div>

          {/* Gombok */}
          <footer className="modal-footer">
            <button
              type="button"
              onClick={() => onClose(false)}
              className="cancel-btn"
              disabled={isSubmitting}
            >
              Mégse
            </button>
            <button type="submit" className="save-btn" disabled={isSubmitting}>
              {isSubmitting
                ? 'Mentés...'
                : isEditing
                ? '💾 Mentés'
                : '➕ Létrehozás'}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
};
