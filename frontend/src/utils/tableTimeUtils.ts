/**
 * Table Time Utilities
 *
 * Utilities for calculating elapsed time and determining table colors
 * based on how long a table has been occupied (order age).
 *
 * Time-based color logic for dining room tables:
 * - 0-24 minutes: Normal (blue) - service is on track
 * - 25-34 minutes: Warning (yellow) - attention needed
 * - 35+ minutes: Urgent (red) - immediate attention required
 */

export interface TableTimeMetrics {
  elapsedMinutes: number;
  hasActiveOrder: boolean;
  orderCreatedAt?: string;
}

export interface TimeBasedColors {
  bg: string;
  text: string;
  border: string;
}

/**
 * Calculate elapsed minutes since a given timestamp
 *
 * @param timestamp - ISO datetime string (e.g., "2025-11-23T10:30:00Z")
 * @returns Number of minutes elapsed (rounded down)
 */
export const calculateElapsedMinutes = (timestamp: string): number => {
  const startTime = new Date(timestamp).getTime();
  const now = Date.now();
  const elapsedMs = now - startTime;
  return Math.floor(elapsedMs / 60000); // Convert ms to minutes
};

/**
 * Get time-based color palette for a table based on elapsed minutes
 *
 * Color logic:
 * - 0-24 minutes: Blue (normal service)
 * - 25-34 minutes: Yellow (attention needed)
 * - 35+ minutes: Red (urgent)
 *
 * @param elapsedMinutes - Number of minutes since order was created
 * @returns Color palette object with bg, text, and border colors
 */
export const getTimeBasedColors = (elapsedMinutes: number): TimeBasedColors => {
  if (elapsedMinutes < 25) {
    // 0-24 minutes: Normal - Blue
    return {
      bg: '#228be6',
      text: '#eef7ff',
      border: '#3b9aff',
    };
  } else if (elapsedMinutes < 35) {
    // 25-34 minutes: Warning - Yellow/Orange
    return {
      bg: '#f08c00',
      text: '#fff8e1',
      border: '#f7a400',
    };
  } else {
    // 35+ minutes: Urgent - Red
    return {
      bg: '#e03131',
      text: '#ffecec',
      border: '#ff4d4f',
    };
  }
};

/**
 * Get table time metrics from order data
 *
 * @param orderCreatedAt - ISO datetime string of order creation (optional)
 * @returns TableTimeMetrics object with elapsed time and order status
 */
export const getTableTimeMetrics = (orderCreatedAt?: string): TableTimeMetrics => {
  if (!orderCreatedAt) {
    return {
      elapsedMinutes: 0,
      hasActiveOrder: false,
    };
  }

  return {
    elapsedMinutes: calculateElapsedMinutes(orderCreatedAt),
    hasActiveOrder: true,
    orderCreatedAt,
  };
};

/**
 * Format elapsed time for display in Hungarian
 *
 * @param elapsedMinutes - Number of minutes elapsed
 * @returns Formatted string (e.g., "28 perc", "5 perc")
 */
export const formatElapsedMinutes = (elapsedMinutes: number): string => {
  return `${elapsedMinutes} perc`;
};
