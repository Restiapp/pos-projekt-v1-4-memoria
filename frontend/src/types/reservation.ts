/**
 * Reservation Types
 * TypeScript interfaces for reservation management
 */

export type ReservationStatus = 'PENDING' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW';

export interface Reservation {
  id: number;
  table_id: number;
  customer_id?: number | null;
  guest_name: string;
  guest_phone?: string | null;
  guest_email?: string | null;
  reservation_date: string; // ISO date string (YYYY-MM-DD)
  reservation_time: string; // ISO time string (HH:MM:SS)
  guest_count: number;
  duration_minutes: number;
  status: ReservationStatus;
  special_requests?: string | null;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface ReservationCreate {
  table_id: number;
  customer_id?: number | null;
  guest_name: string;
  guest_phone?: string | null;
  guest_email?: string | null;
  reservation_date: string; // YYYY-MM-DD
  reservation_time: string; // HH:MM:SS
  guest_count: number;
  duration_minutes?: number;
  status?: ReservationStatus;
  special_requests?: string | null;
}

export interface ReservationUpdate {
  table_id?: number;
  customer_id?: number | null;
  guest_name?: string;
  guest_phone?: string | null;
  guest_email?: string | null;
  reservation_date?: string;
  reservation_time?: string;
  guest_count?: number;
  duration_minutes?: number;
  status?: ReservationStatus;
  special_requests?: string | null;
}

export interface ReservationListResponse {
  items: Reservation[];
  total: number;
  page: number;
  page_size: number;
}

// Calendar Event type for react-big-calendar
export interface CalendarReservation extends Reservation {
  start: Date;
  end: Date;
  title: string;
}
