/**
 * EmployeeEditor - Munkatárs létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új munkatárs létrehozása (POST /api/employees)
 *   - Meglévő munkatárs szerkesztése (PUT /api/employees/{id})
 *   - Validáció (teljes név, username, email, jelszó kötelező új munkatársnál)
 *   - Szerepkör választás (dropdown)
 *   - Modal overlay (háttérre kattintva bezárás)
 */

import { useState } from 'react';
import { createEmployee, updateEmployee } from '@/services/employeeService';
import type { Employee, Role, EmployeeCreate, EmployeeUpdate } from '@/types/employee';
<<<<<<< HEAD
import { notify } from '@/utils/notifications';
=======
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
import './EmployeeEditor.css';

interface EmployeeEditorProps {
  employee: Employee | null; // null = új munkatárs, Employee = szerkesztés
  roles: Role[];
  onClose: (shouldRefresh: boolean) => void;
}

export const EmployeeEditor = ({
  employee,
  roles,
  onClose,
}: EmployeeEditorProps) => {
  const isEditing = !!employee; // true = szerkesztés, false = új létrehozás
  const { showToast } = useToast();
  const { showConfirm } = useConfirm();

  // Form állapot
  const [formData, setFormData] = useState({
    full_name: employee?.full_name || '',
    username: employee?.username || '',
    email: employee?.email || '',
    password: '', // Új jelszó (csak új munkatársnál kötelező)
    role_id: employee?.role_id || undefined,
    is_active: employee?.is_active ?? true,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    // Checkbox kezelés
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    // Role ID (opcionális)
    if (name === 'role_id') {
      setFormData((prev) => ({
        ...prev,
        [name]: value ? parseInt(value, 10) : undefined,
      }));
      return;
    }

    // String mezők
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Form submit (létrehozás / frissítés)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (!formData.full_name.trim()) {
<<<<<<< HEAD
      notify.warning('A teljes név kötelező!');
=======
      showToast('A teljes név kötelező!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      return;
    }

    if (!formData.username.trim()) {
<<<<<<< HEAD
      notify.warning('A felhasználónév kötelező!');
=======
      showToast('A felhasználónév kötelező!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      return;
    }

    if (!formData.email.trim()) {
<<<<<<< HEAD
      notify.warning('Az email cím kötelező!');
=======
      showToast('Az email cím kötelező!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      return;
    }

    // Email formátum validáció (egyszerű)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
<<<<<<< HEAD
      notify.warning('Érvénytelen email formátum!');
=======
      showToast('Érvénytelen email formátum!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      return;
    }

    // Jelszó validáció (csak új munkatársnál kötelező)
    if (!isEditing && !formData.password) {
<<<<<<< HEAD
      notify.warning('A jelszó (PIN kód) kötelező új munkatársnál!');
=======
      showToast('A jelszó (PIN kód) kötelező új munkatársnál!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      return;
    }

    if (formData.password && formData.password.length < 4) {
<<<<<<< HEAD
      notify.warning('A jelszó (PIN kód) legalább 4 karakter hosszú legyen!');
=======
      showToast('A jelszó (PIN kód) legalább 4 karakter hosszú legyen!', 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing && employee) {
        // Frissítés
        const updateData: EmployeeUpdate = {
          full_name: formData.full_name,
          username: formData.username,
          email: formData.email,
          role_id: formData.role_id,
          is_active: formData.is_active,
        };

        // Csak ha új jelszót adtak meg
        if (formData.password) {
          updateData.password = formData.password;
        }

        await updateEmployee(employee.id, updateData);
<<<<<<< HEAD
        notify.success('Munkatárs sikeresen frissítve!');
=======
        showToast('Munkatárs sikeresen frissítve!', 'success');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      } else {
        // Létrehozás
        const createData: EmployeeCreate = {
          full_name: formData.full_name,
          username: formData.username,
          email: formData.email,
          password: formData.password,
          role_id: formData.role_id,
          is_active: formData.is_active,
        };

        await createEmployee(createData);
<<<<<<< HEAD
        notify.success('Munkatárs sikeresen létrehozva!');
=======
        showToast('Munkatárs sikeresen létrehozva!', 'success');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
      }

      onClose(true); // Bezárás + lista frissítése
    } catch (error: any) {
      console.error('Hiba a munkatárs mentésekor:', error);
      const errorMessage =
        error.response?.data?.detail || 'Nem sikerült menteni a munkatársat!';
<<<<<<< HEAD
      notify.error(errorMessage);
=======
      showToast(errorMessage, 'error');
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
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

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <header className="modal-header">
          <h2>{isEditing ? '✏️ Munkatárs szerkesztése' : '➕ Új munkatárs'}</h2>
          <button onClick={() => onClose(false)} className="close-btn">
            ✕
          </button>
        </header>

        <form onSubmit={handleSubmit} className="employee-form">
          {/* Teljes név */}
          <div className="form-group">
            <label htmlFor="full_name">
              Teljes név <span className="required">*</span>
            </label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="pl. Kovács János"
              required
              maxLength={255}
            />
          </div>

          {/* Felhasználónév */}
          <div className="form-group">
            <label htmlFor="username">
              Felhasználónév <span className="required">*</span>
            </label>
            <input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              placeholder="pl. jkovacs"
              required
              maxLength={50}
              pattern="^[a-zA-Z0-9_-]+$"
              title="Csak betűk, számok, kötőjel és alulvonás használható"
            />
            <small className="field-hint">
              Csak betűk, számok, kötőjel (-) és alulvonás (_) használható
            </small>
          </div>

          {/* Email */}
          <div className="form-group">
            <label htmlFor="email">
              Email cím <span className="required">*</span>
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="pl. janos.kovacs@example.com"
              required
              maxLength={255}
            />
          </div>

          {/* Jelszó (PIN kód) */}
          <div className="form-group">
            <label htmlFor="password">
              Jelszó (PIN kód) {!isEditing && <span className="required">*</span>}
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder={
                isEditing
                  ? 'Hagyd üresen, ha nem szeretnéd megváltoztatni'
                  : 'pl. 1234 vagy SecurePin123'
              }
              required={!isEditing}
              minLength={4}
              maxLength={255}
            />
            <small className="field-hint">
              {isEditing
                ? 'Hagyd üresen, ha nem szeretnéd megváltoztatni'
                : 'Minimum 4 karakter hosszú'}
            </small>
          </div>

          {/* Szerepkör */}
          <div className="form-group">
            <label htmlFor="role_id">Szerepkör</label>
            <select
              id="role_id"
              name="role_id"
              value={formData.role_id || ''}
              onChange={handleChange}
            >
              <option value="">-- Nincs szerepkör --</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name} - {role.description}
                </option>
              ))}
            </select>
            <small className="field-hint">
              A szerepkör határozza meg a munkatárs jogosultságait
            </small>
          </div>

          {/* Aktív */}
          <div className="form-group checkbox-group">
            <label>
              <input
                name="is_active"
                type="checkbox"
                checked={formData.is_active}
                onChange={handleChange}
              />
              Aktív (bejelentkezhet a rendszerbe)
            </label>
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
