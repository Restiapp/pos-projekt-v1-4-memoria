/**
 * Toast - Individual toast notification component
 * Supports success, error, warning, and info variants
 * Auto-dismiss after 4 seconds with smooth animations
 */

import { useEffect, useState } from 'react';
import './Toast.css';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface ToastProps {
  id: string;
  message: string;
  variant: ToastVariant;
  duration?: number;
  onClose: (id: string) => void;
}

/**
 * Icon components for each toast variant
 */
const ToastIcon = ({ variant }: { variant: ToastVariant }) => {
  switch (variant) {
    case 'success':
      return (
        <svg className="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      );
    case 'error':
      return (
        <svg className="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      );
    case 'warning':
      return (
        <svg className="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      );
    case 'info':
      return (
        <svg className="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
  }
};

/**
 * Close button component
 */
const CloseButton = ({ onClick }: { onClick: () => void }) => (
  <button className="toast-close" onClick={onClick} aria-label="Close toast">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  </button>
);

/**
 * Toast component - Displays a single notification
 */
export const Toast = ({ id, message, variant, duration = 4000, onClose }: ToastProps) => {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    // Auto-dismiss timer
    const timer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, id]);

  const handleClose = () => {
    setIsExiting(true);
    // Wait for exit animation to complete before removing from DOM
    setTimeout(() => {
      onClose(id);
    }, 300); // Match animation duration
  };

  return (
    <div className={`toast toast-${variant} ${isExiting ? 'toast-exit' : 'toast-enter'}`} role="alert">
      <div className="toast-icon-wrapper">
        <ToastIcon variant={variant} />
      </div>
      <div className="toast-content">
        <p className="toast-message">{message}</p>
      </div>
      <CloseButton onClick={handleClose} />
    </div>
  );
};
