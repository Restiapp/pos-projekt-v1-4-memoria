/**
 * ConfirmDialog Component - Confirmation Dialog System
 *
 * Usage:
 * const { showConfirm } = useConfirm();
 * const result = await showConfirm('Are you sure?');
 * if (result) { ... }
 */

import { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import './ConfirmDialog.css';

interface ConfirmOptions {
  message: string;
  title?: string;
  confirmText?: string;
  cancelText?: string;
}

interface ConfirmDialogState extends ConfirmOptions {
  isOpen: boolean;
  resolve: (value: boolean) => void;
}

interface ConfirmContextType {
  showConfirm: (message: string, options?: Partial<ConfirmOptions>) => Promise<boolean>;
}

const ConfirmContext = createContext<ConfirmContextType | undefined>(undefined);

export const useConfirm = () => {
  const context = useContext(ConfirmContext);
  if (!context) {
    throw new Error('useConfirm must be used within ConfirmProvider');
  }
  return context;
};

export const ConfirmProvider = ({ children }: { children: ReactNode }) => {
  const [dialogState, setDialogState] = useState<ConfirmDialogState>({
    isOpen: false,
    message: '',
    title: 'Megerősítés',
    confirmText: 'OK',
    cancelText: 'Mégse',
    resolve: () => {},
  });

  const showConfirm = useCallback((message: string, options: Partial<ConfirmOptions> = {}) => {
    return new Promise<boolean>((resolve) => {
      setDialogState({
        isOpen: true,
        message,
        title: options.title || 'Megerősítés',
        confirmText: options.confirmText || 'OK',
        cancelText: options.cancelText || 'Mégse',
        resolve,
      });
    });
  }, []);

  const handleConfirm = () => {
    dialogState.resolve(true);
    setDialogState((prev) => ({ ...prev, isOpen: false }));
  };

  const handleCancel = () => {
    dialogState.resolve(false);
    setDialogState((prev) => ({ ...prev, isOpen: false }));
  };

  return (
    <ConfirmContext.Provider value={{ showConfirm }}>
      {children}
      {dialogState.isOpen && (
        <div className="confirm-overlay" onClick={handleCancel}>
          <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="confirm-header">
              <h3>{dialogState.title}</h3>
            </div>
            <div className="confirm-body">
              <p>{dialogState.message}</p>
            </div>
            <div className="confirm-footer">
              <button className="confirm-btn-cancel" onClick={handleCancel}>
                {dialogState.cancelText}
              </button>
              <button className="confirm-btn-confirm" onClick={handleConfirm}>
                {dialogState.confirmText}
              </button>
            </div>
          </div>
        </div>
      )}
    </ConfirmContext.Provider>
  );
};
