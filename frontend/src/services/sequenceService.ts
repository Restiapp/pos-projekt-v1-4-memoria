/**
 * Sequence Service
 * Handles order sequence number generation
 */

import api from './api';

/**
 * Response from the sequence number endpoint
 */
export interface SequenceNumberResponse {
  order_number: string;
}

/**
 * Get the next available order sequence number
 *
 * This fetches the next sequence number that will be assigned to an order
 * when it's created. Used for preview in the order creation modal.
 *
 * @returns Promise<string> The next order number (e.g., "ORD-0042")
 * @throws Error if the request fails
 */
export const getNextSequenceNumber = async (): Promise<string> => {
  const response = await api.get<SequenceNumberResponse>('/orders/sequence/next');
  return response.data.order_number;
};
