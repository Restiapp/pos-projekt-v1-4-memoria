/**
 * ToastProvider - Manages toast notification queue and display
 * Provides context for useToast hook
 * Displays toasts at top-right with auto-dismiss
 */

import { createContext, useState, useCallback, ReactNode } from 'react';
import { Toast, ToastVariant } from './Toast';
import './ToastProvider.css';

export interface ToastData {
  id: string;
  message: string;
  variant: ToastVariant;
  duration?: number;
}

export interface ToastContextValue {
  addToast: (message: string, variant: ToastVariant, duration?: number) => void;
  removeToast: (id: string) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}

// Create context with undefined default (will be provided by ToastProvider)
export const ToastContext = createContext<ToastContextValue | undefined>(undefined);

interface ToastProviderProps {
  children: ReactNode;
}

/**
 * ToastProvider - Wraps the application to provide toast functionality
 */
export const ToastProvider = ({ children }: ToastProviderProps) => {
  const [toasts, setToasts] = useState<ToastData[]>([]);

  /**
   * Add a new toast to the queue
   */
  const addToast = useCallback((message: string, variant: ToastVariant, duration = 4000) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newToast: ToastData = {
      id,
      message,
      variant,
      duration,
    };

    setToasts((prev) => [...prev, newToast]);
  }, []);

  /**
   * Remove a toast from the queue
   */
  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  /**
   * Convenience methods for each variant
   */
  const success = useCallback(
    (message: string, duration?: number) => {
      addToast(message, 'success', duration);
    },
    [addToast]
  );

  const error = useCallback(
    (message: string, duration?: number) => {
      addToast(message, 'error', duration);
    },
    [addToast]
  );

  const warning = useCallback(
    (message: string, duration?: number) => {
      addToast(message, 'warning', duration);
    },
    [addToast]
  );

  const info = useCallback(
    (message: string, duration?: number) => {
      addToast(message, 'info', duration);
    },
    [addToast]
  );

  const value: ToastContextValue = {
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}

      {/* Toast container - positioned at top-right */}
      <div className="toast-container">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            id={toast.id}
            message={toast.message}
            variant={toast.variant}
            duration={toast.duration}
            onClose={removeToast}
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
};
