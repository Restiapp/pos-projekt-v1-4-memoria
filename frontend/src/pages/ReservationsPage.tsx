/**
 * ReservationsPage Component
 * Displays a calendar view of all reservations with create/edit/delete capabilities
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, momentLocalizer, View } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import {
  getReservationsByDateRange,
  deleteReservation
} from '../services/reservationService';
import { Reservation, CalendarReservation, ReservationStatus } from '../types/reservation';
import ReservationEditor from '../components/admin/ReservationEditor';
import './ReservationsPage.css';

const localizer = momentLocalizer(moment);

const ReservationsPage: React.FC = () => {
  const [reservations, setReservations] = useState<CalendarReservation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<View>('week');
  const [date, setDate] = useState(new Date());

  // Editor modal state
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState<Reservation | null>(null);

  // Convert Reservation to CalendarReservation
  const convertToCalendarEvent = (reservation: Reservation): CalendarReservation => {
    const dateStr = reservation.reservation_date;
    const timeStr = reservation.reservation_time;

    // Parse date and time
    const start = moment(`${dateStr} ${timeStr}`, 'YYYY-MM-DD HH:mm:ss').toDate();
    const end = moment(start).add(reservation.duration_minutes, 'minutes').toDate();

    return {
      ...reservation,
      start,
      end,
      title: `${reservation.guest_name} (${reservation.guest_count} guests) - Table ${reservation.table_id}`
    };
  };

  // Fetch reservations for the current view
  const fetchReservations = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Calculate date range based on current view
      let startDate: moment.Moment;
      let endDate: moment.Moment;

      if (view === 'month') {
        startDate = moment(date).startOf('month').subtract(7, 'days');
        endDate = moment(date).endOf('month').add(7, 'days');
      } else if (view === 'week') {
        startDate = moment(date).startOf('week');
        endDate = moment(date).endOf('week');
      } else { // day
        startDate = moment(date).startOf('day');
        endDate = moment(date).endOf('day');
      }

      const data = await getReservationsByDateRange(
        startDate.format('YYYY-MM-DD'),
        endDate.format('YYYY-MM-DD')
      );

      const calendarEvents = data.map(convertToCalendarEvent);
      setReservations(calendarEvents);
    } catch (err: unknown) {
      console.error('Failed to fetch reservations:', err);
      setError('Failed to load reservations');
    } finally {
      setLoading(false);
    }
  }, [date, view]);

  useEffect(() => {
    fetchReservations();
  }, [fetchReservations]);

  // Handle creating new reservation
  const handleSelectSlot = (slotInfo: { start: Date; end: Date }) => {
    setSelectedReservation(null);
    setIsEditorOpen(true);
  };

  // Handle clicking on existing reservation
  const handleSelectEvent = (event: CalendarReservation) => {
    setSelectedReservation(event);
    setIsEditorOpen(true);
  };

  // Handle editor close
  const handleEditorClose = () => {
    setIsEditorOpen(false);
    setSelectedReservation(null);
  };

  // Handle reservation save (create or update)
  const handleReservationSaved = () => {
    handleEditorClose();
    fetchReservations();
  };

  // Handle reservation delete
  const handleReservationDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this reservation?')) {
      try {
        await deleteReservation(id);
        handleEditorClose();
        fetchReservations();
      } catch (err) {
        console.error('Failed to delete reservation:', err);
        alert('Failed to delete reservation');
      }
    }
  };

  // Event style based on status
  const eventStyleGetter = (event: CalendarReservation) => {
    let backgroundColor = '#667eea'; // default purple

    switch (event.status) {
      case 'CONFIRMED':
        backgroundColor = '#4caf50'; // green
        break;
      case 'PENDING':
        backgroundColor = '#ff9800'; // orange/yellow
        break;
      case 'CANCELLED':
        backgroundColor = '#f44336'; // red
        break;
      case 'COMPLETED':
        backgroundColor = '#9e9e9e'; // gray
        break;
      case 'NO_SHOW':
        backgroundColor = '#795548'; // brown
        break;
    }

    return {
      style: {
        backgroundColor,
        borderRadius: '5px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block'
      }
    };
  };

  return (
    <div className="reservations-page">
      <div className="page-header">
        <h1>Reservations Calendar</h1>
        <div className="header-controls">
          <button
            className="btn-primary"
            onClick={() => {
              setSelectedReservation(null);
              setIsEditorOpen(true);
            }}
          >
            + New Reservation
          </button>
          <button
            className="btn-secondary"
            onClick={fetchReservations}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="calendar-legend">
        <div className="legend-item">
          <span className="legend-color status-confirmed"></span>
          <span>Confirmed</span>
        </div>
        <div className="legend-item">
          <span className="legend-color status-pending"></span>
          <span>Pending</span>
        </div>
        <div className="legend-item">
          <span className="legend-color status-cancelled"></span>
          <span>Cancelled</span>
        </div>
        <div className="legend-item">
          <span className="legend-color status-completed"></span>
          <span>Completed</span>
        </div>
        <div className="legend-item">
          <span className="legend-color status-no-show"></span>
          <span>No Show</span>
        </div>
      </div>

      <div className="calendar-container">
        <Calendar
          localizer={localizer}
          events={reservations}
          startAccessor="start"
          endAccessor="end"
          style={{ height: 'calc(100vh - 300px)', minHeight: '500px' }}
          view={view}
          onView={setView}
          date={date}
          onNavigate={setDate}
          onSelectSlot={handleSelectSlot}
          onSelectEvent={handleSelectEvent}
          selectable
          eventPropGetter={eventStyleGetter}
          views={['month', 'week', 'day']}
          step={30}
          showMultiDayTimes
          defaultDate={new Date()}
          popup
        />
      </div>

      {isEditorOpen && (
        <ReservationEditor
          reservation={selectedReservation}
          onClose={handleEditorClose}
          onSave={handleReservationSaved}
          onDelete={selectedReservation ? handleReservationDelete : undefined}
        />
      )}
    </div>
  );
};

export default ReservationsPage;
