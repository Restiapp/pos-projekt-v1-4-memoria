/**
 * Table Status Color Utility
 *
 * Provides color mapping for table statuses in the POS system.
 *
 * Status definitions:
 * - free: Table is available and has no active orders
 * - active: Table has an active order (NYITOTT or FELDOLGOZVA)
 * - preparing: Order items are being prepared in the kitchen
 * - paying: Payment is in progress
 * - reserved: Table is reserved for a future booking
 */

export type TableStatus = 'free' | 'active' | 'preparing' | 'paying' | 'reserved';

export interface TableStatusColors {
  primary: string;      // Main background color
  hover: string;        // Hover state color
  border: string;       // Border color
  text: string;         // Text color
}

/**
 * Get color scheme for a given table status
 * @param status - The current status of the table
 * @returns Color scheme object with primary, hover, border, and text colors
 */
export function getTableStatusColor(status: TableStatus): TableStatusColors {
  switch (status) {
    case 'free':
      return {
        primary: '#10B981',    // green-500
        hover: '#059669',      // green-600
        border: '#047857',     // green-700
        text: '#FFFFFF',
      };
    case 'active':
      return {
        primary: '#3B82F6',    // blue-500
        hover: '#2563EB',      // blue-600
        border: '#1D4ED8',     // blue-700
        text: '#FFFFFF',
      };
    case 'preparing':
      return {
        primary: '#F59E0B',    // amber-500 (yellow)
        hover: '#D97706',      // amber-600
        border: '#B45309',     // amber-700
        text: '#FFFFFF',
      };
    case 'paying':
      return {
        primary: '#EF4444',    // red-500
        hover: '#DC2626',      // red-600
        border: '#B91C1C',     // red-700
        text: '#FFFFFF',
      };
    case 'reserved':
      return {
        primary: '#6B7280',    // gray-500
        hover: '#4B5563',      // gray-600
        border: '#374151',     // gray-700
        text: '#FFFFFF',
      };
    default:
      // Fallback to free status
      return {
        primary: '#10B981',
        hover: '#059669',
        border: '#047857',
        text: '#FFFFFF',
      };
  }
}

/**
 * Get status label in Hungarian
 * @param status - The current status of the table
 * @returns Human-readable status label
 */
export function getTableStatusLabel(status: TableStatus): string {
  switch (status) {
    case 'free':
      return 'Szabad';
    case 'active':
      return 'Aktív';
    case 'preparing':
      return 'Készül';
    case 'paying':
      return 'Fizet';
    case 'reserved':
      return 'Foglalt';
    default:
      return 'Ismeretlen';
  }
}

/**
 * Determine table status based on order and reservation data
 * This is a helper function that can be used to compute status from backend data
 *
 * @param hasActiveOrder - Whether the table has an active order
 * @param isPreparing - Whether items are being prepared
 * @param isPaying - Whether payment is in progress
 * @param isReserved - Whether the table is reserved
 * @returns Computed table status
 */
export function computeTableStatus(
  hasActiveOrder: boolean,
  isPreparing: boolean,
  isPaying: boolean,
  isReserved: boolean
): TableStatus {
  // Priority order: paying > preparing > active > reserved > free
  if (isPaying) return 'paying';
  if (isPreparing) return 'preparing';
  if (hasActiveOrder) return 'active';
  if (isReserved) return 'reserved';
  return 'free';
}
