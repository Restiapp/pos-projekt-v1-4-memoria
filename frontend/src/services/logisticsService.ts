/**
 * Logistics Service - Logistics API hívások (Zones, Couriers, Deliveries)
 *
 * Backend endpoints (service_logistics:8006):
 *   - GET /api/v1/zones
 *   - POST /api/v1/zones
 *   - PUT /api/v1/zones/{id}
 *   - DELETE /api/v1/zones/{id}
 *   - GET /api/v1/couriers
 *   - POST /api/v1/couriers
 *   - PUT /api/v1/couriers/{id}
 *   - DELETE /api/v1/couriers/{id}
 *   - PATCH /api/v1/couriers/{id}/status
 *
 * Frontend hívások:
 *   - GET /api/logistics/zones → Vite proxy → http://localhost:8006/api/v1/zones
 *   - POST /api/logistics/zones → Vite proxy → http://localhost:8006/api/v1/zones
 */

import apiClient from './api';
import type {
  Courier,
  CourierCreate,
  CourierUpdate,
  CourierListResponse,
  CourierStatus,
  DeliveryZone,
  DeliveryZoneCreate,
  DeliveryZoneUpdate,
  DeliveryZoneListResponse,
  GetByZipCodeRequest,
  GetByZipCodeResponse,
  GetByAddressRequest,
  GetByAddressResponse,
} from '@/types/logistics';

// =====================================================
// DELIVERY ZONES
// =====================================================

/**
 * GET /api/logistics/zones - Kiszállítási zónák listája (lapozással)
 * Proxy Target: http://localhost:8006/api/v1/zones
 */
export const getDeliveryZones = async (
  page: number = 1,
  page_size: number = 20,
  active_only?: boolean
): Promise<DeliveryZoneListResponse> => {
  const params: Record<string, any> = { page, page_size };
  if (active_only !== undefined) {
    params.active_only = active_only;
  }

  const response = await apiClient.get<DeliveryZoneListResponse>('/api/logistics/zones', {
    params,
  });
  return response.data;
};

/**
 * GET /api/logistics/zones/{id} - Zóna részletei
 * Proxy Target: http://localhost:8006/api/v1/zones/{id}
 */
export const getDeliveryZoneById = async (id: number): Promise<DeliveryZone> => {
  const response = await apiClient.get<DeliveryZone>(`/api/logistics/zones/${id}`);
  return response.data;
};

/**
 * POST /api/logistics/zones - Új zóna létrehozása
 * Proxy Target: http://localhost:8006/api/v1/zones
 */
export const createDeliveryZone = async (
  zoneData: DeliveryZoneCreate
): Promise<DeliveryZone> => {
  const response = await apiClient.post<DeliveryZone>('/api/logistics/zones', zoneData);
  return response.data;
};

/**
 * PUT /api/logistics/zones/{id} - Zóna frissítése
 * Proxy Target: http://localhost:8006/api/v1/zones/{id}
 */
export const updateDeliveryZone = async (
  id: number,
  zoneData: DeliveryZoneUpdate
): Promise<DeliveryZone> => {
  const response = await apiClient.put<DeliveryZone>(
    `/api/logistics/zones/${id}`,
    zoneData
  );
  return response.data;
};

/**
 * DELETE /api/logistics/zones/{id} - Zóna törlése
 * Proxy Target: http://localhost:8006/api/v1/zones/{id}
 */
export const deleteDeliveryZone = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/logistics/zones/${id}`);
};

/**
 * POST /api/logistics/zones/get-by-zip-code - Zóna keresése irányítószám alapján
 * Proxy Target: http://localhost:8006/api/v1/zones/get-by-zip-code
 */
export const getZoneByZipCode = async (
  zipCode: string
): Promise<GetByZipCodeResponse> => {
  const response = await apiClient.post<GetByZipCodeResponse>(
    '/api/logistics/zones/get-by-zip-code',
    { zip_code: zipCode } as GetByZipCodeRequest
  );
  return response.data;
};

/**
 * POST /api/logistics/zones/get-by-address - Zóna keresése cím alapján (MOCK)
 * Proxy Target: http://localhost:8006/api/v1/zones/get-by-address
 */
export const getZoneByAddress = async (
  address: string
): Promise<GetByAddressResponse> => {
  const response = await apiClient.post<GetByAddressResponse>(
    '/api/logistics/zones/get-by-address',
    { address } as GetByAddressRequest
  );
  return response.data;
};

// =====================================================
// COURIERS
// =====================================================

/**
 * GET /api/logistics/couriers - Futárok listája (lapozással)
 * Proxy Target: http://localhost:8006/api/v1/couriers
 */
export const getCouriers = async (
  page: number = 1,
  page_size: number = 20,
  status?: CourierStatus,
  active_only?: boolean
): Promise<CourierListResponse> => {
  const params: Record<string, any> = { page, page_size };
  if (status) {
    params.status = status;
  }
  if (active_only !== undefined) {
    params.active_only = active_only;
  }

  const response = await apiClient.get<CourierListResponse>('/api/logistics/couriers', {
    params,
  });
  return response.data;
};

/**
 * GET /api/logistics/couriers/available - Elérhető futárok listája
 * Proxy Target: http://localhost:8006/api/v1/couriers/available
 */
export const getAvailableCouriers = async (): Promise<Courier[]> => {
  const response = await apiClient.get<Courier[]>('/api/logistics/couriers/available');
  return response.data;
};

/**
 * GET /api/logistics/couriers/{id} - Futár részletei
 * Proxy Target: http://localhost:8006/api/v1/couriers/{id}
 */
export const getCourierById = async (id: number): Promise<Courier> => {
  const response = await apiClient.get<Courier>(`/api/logistics/couriers/${id}`);
  return response.data;
};

/**
 * POST /api/logistics/couriers - Új futár létrehozása
 * Proxy Target: http://localhost:8006/api/v1/couriers
 */
export const createCourier = async (courierData: CourierCreate): Promise<Courier> => {
  const response = await apiClient.post<Courier>('/api/logistics/couriers', courierData);
  return response.data;
};

/**
 * PUT /api/logistics/couriers/{id} - Futár frissítése
 * Proxy Target: http://localhost:8006/api/v1/couriers/{id}
 */
export const updateCourier = async (
  id: number,
  courierData: CourierUpdate
): Promise<Courier> => {
  const response = await apiClient.put<Courier>(
    `/api/logistics/couriers/${id}`,
    courierData
  );
  return response.data;
};

/**
 * DELETE /api/logistics/couriers/{id} - Futár törlése
 * Proxy Target: http://localhost:8006/api/v1/couriers/{id}
 */
export const deleteCourier = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/logistics/couriers/${id}`);
};

/**
 * PATCH /api/logistics/couriers/{id}/status - Futár státusz módosítása
 * Proxy Target: http://localhost:8006/api/v1/couriers/{id}/status
 */
export const updateCourierStatus = async (
  id: number,
  newStatus: CourierStatus
): Promise<Courier> => {
  const response = await apiClient.patch<Courier>(
    `/api/logistics/couriers/${id}/status`,
    null,
    {
      params: { new_status: newStatus },
    }
  );
  return response.data;
};

/**
 * POST /api/logistics/couriers/{id}/assign-order - Rendelés hozzárendelése futárhoz
 * Proxy Target: http://localhost:8006/api/v1/couriers/{id}/assign-order
 */
export const assignCourierToOrder = async (
  courierId: number,
  orderId: number
): Promise<{ message: string; courier: Courier }> => {
  const response = await apiClient.post<{ message: string; courier: Courier }>(
    `/api/logistics/couriers/${courierId}/assign-order`,
    null,
    {
      params: { order_id: orderId },
    }
  );
  return response.data;
};
