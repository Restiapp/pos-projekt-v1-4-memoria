/**
 * Reservation Service
 * API service for managing reservations
 */

import api from './api';
import type {
  Reservation,
  ReservationCreate,
  ReservationUpdate,
  ReservationListResponse
} from '../types/reservation';

const RESERVATIONS_BASE_URL = '/api/reservations';

/**
 * Get all reservations with pagination
 */
export const getReservations = async (
  page: number = 1,
  pageSize: number = 20
): Promise<ReservationListResponse> => {
  const response = await api.get<ReservationListResponse>(RESERVATIONS_BASE_URL, {
    params: { page, page_size: pageSize }
  });
  return response.data;
};

/**
 * Get a single reservation by ID
 */
export const getReservation = async (id: number): Promise<Reservation> => {
  const response = await api.get<Reservation>(`${RESERVATIONS_BASE_URL}/${id}`);
  return response.data;
};

/**
 * Get reservations by date
 */
export const getReservationsByDate = async (date: string): Promise<Reservation[]> => {
  const response = await api.get<Reservation[]>(`${RESERVATIONS_BASE_URL}/by-date/${date}`);
  return response.data;
};

/**
 * Get reservations by date range
 */
export const getReservationsByDateRange = async (
  startDate: string,
  endDate: string
): Promise<Reservation[]> => {
  const response = await api.get<Reservation[]>(`${RESERVATIONS_BASE_URL}/by-date-range`, {
    params: { start_date: startDate, end_date: endDate }
  });
  return response.data;
};

/**
 * Get reservations by table
 */
export const getReservationsByTable = async (tableId: number): Promise<Reservation[]> => {
  const response = await api.get<Reservation[]>(`${RESERVATIONS_BASE_URL}/by-table/${tableId}`);
  return response.data;
};

/**
 * Get reservations by status
 */
export const getReservationsByStatus = async (status: string): Promise<Reservation[]> => {
  const response = await api.get<Reservation[]>(`${RESERVATIONS_BASE_URL}/by-status/${status}`);
  return response.data;
};

/**
 * Create a new reservation
 */
export const createReservation = async (data: ReservationCreate): Promise<Reservation> => {
  const response = await api.post<Reservation>(RESERVATIONS_BASE_URL, data);
  return response.data;
};

/**
 * Update an existing reservation
 */
export const updateReservation = async (
  id: number,
  data: ReservationUpdate
): Promise<Reservation> => {
  const response = await api.put<Reservation>(`${RESERVATIONS_BASE_URL}/${id}`, data);
  return response.data;
};

/**
 * Update reservation status
 */
export const updateReservationStatus = async (
  id: number,
  status: string
): Promise<Reservation> => {
  const response = await api.patch<Reservation>(
    `${RESERVATIONS_BASE_URL}/${id}/status`,
    null,
    { params: { status } }
  );
  return response.data;
};

/**
 * Delete a reservation
 */
export const deleteReservation = async (id: number): Promise<void> => {
  await api.delete(`${RESERVATIONS_BASE_URL}/${id}`);
};
