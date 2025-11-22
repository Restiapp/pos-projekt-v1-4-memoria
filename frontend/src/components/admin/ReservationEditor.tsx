// TODO-S0-STUB: TypeScript checking disabled - fix dependency issues
// @ts-nocheck
/**
 * ReservationEditor Component
 * Modal for creating and editing reservations
 */

import React, { useState, useEffect } from 'react';
import type { Reservation, ReservationCreate, ReservationUpdate, ReservationStatus } from '../../types/reservation';
import { createReservation, updateReservation } from '../../services/reservationService';
import { getTables } from '../../services/tableService';
import type { Table } from '../../types/table';
import './ReservationEditor.css';

interface ReservationEditorProps {
  reservation: Reservation | null;
  onClose: () => void;
  onSave: () => void;
  onDelete?: (id: number) => void;
}

const STATUSES: ReservationStatus[] = ['PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'NO_SHOW'];

const ReservationEditor: React.FC<ReservationEditorProps> = ({
  reservation,
  onClose,
  onSave,
  onDelete
}) => {
  const isEditMode = !!reservation;

  // Form state
  const [formData, setFormData] = useState({
    table_id: reservation?.table_id || 0,
    guest_name: reservation?.guest_name || '',
    guest_phone: reservation?.guest_phone || '',
    guest_email: reservation?.guest_email || '',
    reservation_date: reservation?.reservation_date || new Date().toISOString().split('T')[0],
    reservation_time: reservation?.reservation_time?.substring(0, 5) || '18:00',
    guest_count: reservation?.guest_count || 2,
    duration_minutes: reservation?.duration_minutes || 120,
    status: (reservation?.status as ReservationStatus) || 'PENDING',
    special_requests: reservation?.special_requests || ''
  });

  const [tables, setTables] = useState<Table[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch tables on mount
  useEffect(() => {
    const fetchTables = async () => {
      try {
        const response = await getTables();
        setTables(response.items);
      } catch (err) {
        console.error('Failed to fetch tables:', err);
        setError('Failed to load tables');
      }
    };
    fetchTables();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'table_id' || name === 'guest_count' || name === 'duration_minutes'
        ? parseInt(value)
        : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validation
      if (!formData.guest_name.trim()) {
        throw new Error('Guest name is required');
      }
      if (formData.table_id === 0) {
        throw new Error('Please select a table');
      }
      if (formData.guest_count < 1) {
        throw new Error('Guest count must be at least 1');
      }

      // Format time to HH:MM:SS
      const timeWithSeconds = formData.reservation_time.includes(':')
        ? `${formData.reservation_time}:00`
        : formData.reservation_time;

      if (isEditMode && reservation) {
        // Update existing reservation
        const updateData: ReservationUpdate = {
          table_id: formData.table_id,
          guest_name: formData.guest_name,
          guest_phone: formData.guest_phone || null,
          guest_email: formData.guest_email || null,
          reservation_date: formData.reservation_date,
          reservation_time: timeWithSeconds,
          guest_count: formData.guest_count,
          duration_minutes: formData.duration_minutes,
          status: formData.status,
          special_requests: formData.special_requests || null
        };
        await updateReservation(reservation.id, updateData);
      } else {
        // Create new reservation
        const createData: ReservationCreate = {
          table_id: formData.table_id,
          guest_name: formData.guest_name,
          guest_phone: formData.guest_phone || null,
          guest_email: formData.guest_email || null,
          reservation_date: formData.reservation_date,
          reservation_time: timeWithSeconds,
          guest_count: formData.guest_count,
          duration_minutes: formData.duration_minutes,
          status: formData.status,
          special_requests: formData.special_requests || null
        };
        await createReservation(createData);
      }

      onSave();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to save reservation');
      }
      console.error('Failed to save reservation:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = () => {
    if (reservation && onDelete) {
      onDelete(reservation.id);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditMode ? 'Edit Reservation' : 'New Reservation'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="reservation-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="table_id">Table *</label>
              <select
                id="table_id"
                name="table_id"
                value={formData.table_id}
                onChange={handleChange}
                required
              >
                <option value={0}>Select a table</option>
                {tables.map(table => (
                  <option key={table.id} value={table.id}>
                    Table {table.table_number} {table.capacity ? `(Capacity: ${table.capacity})` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="status">Status</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
              >
                {STATUSES.map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="guest_name">Guest Name *</label>
            <input
              type="text"
              id="guest_name"
              name="guest_name"
              value={formData.guest_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="guest_phone">Phone</label>
              <input
                type="tel"
                id="guest_phone"
                name="guest_phone"
                value={formData.guest_phone}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="guest_email">Email</label>
              <input
                type="email"
                id="guest_email"
                name="guest_email"
                value={formData.guest_email}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="reservation_date">Date *</label>
              <input
                type="date"
                id="reservation_date"
                name="reservation_date"
                value={formData.reservation_date}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="reservation_time">Time *</label>
              <input
                type="time"
                id="reservation_time"
                name="reservation_time"
                value={formData.reservation_time}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="guest_count">Guests *</label>
              <input
                type="number"
                id="guest_count"
                name="guest_count"
                value={formData.guest_count}
                onChange={handleChange}
                min={1}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="duration_minutes">Duration (minutes)</label>
              <input
                type="number"
                id="duration_minutes"
                name="duration_minutes"
                value={formData.duration_minutes}
                onChange={handleChange}
                min={30}
                step={15}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="special_requests">Special Requests</label>
            <textarea
              id="special_requests"
              name="special_requests"
              value={formData.special_requests}
              onChange={handleChange}
              rows={3}
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            {isEditMode && onDelete && (
              <button
                type="button"
                className="btn-danger"
                onClick={handleDelete}
              >
                Delete
              </button>
            )}
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Saving...' : isEditMode ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReservationEditor;
