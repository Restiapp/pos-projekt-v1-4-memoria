/**
 * useToast - Hook to access toast notification system
 * Provides methods to show success, error, warning, and info toasts
 */

import { useContext } from 'react';
import { ToastContext, ToastContextValue } from '@/components/ui/ToastProvider';

/**
 * useToast hook - Access toast notification methods
 *
 * @throws Error if used outside of ToastProvider
 * @returns ToastContextValue with methods to trigger toasts
 *
 * @example
 * ```tsx
 * const toast = useToast();
 *
 * // Show success toast
 * toast.success('Operation completed successfully!');
 *
 * // Show error toast
 * toast.error('Something went wrong!');
 *
 * // Show warning toast
 * toast.warning('Please check your input');
 *
 * // Show info toast
 * toast.info('New features available');
 *
 * // Custom duration (default is 4000ms)
 * toast.success('Saved!', 2000);
 * ```
 */
export const useToast = (): ToastContextValue => {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }

  return context;
};
