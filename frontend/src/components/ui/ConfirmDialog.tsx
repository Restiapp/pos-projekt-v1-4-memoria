/**
 * ConfirmDialog - Accessible Confirmation Dialog
 *
 * Features:
 * - Title, description, confirm, cancel buttons
 * - Uses Modal component for accessibility
 * - Customizable button labels and variants
 * - Prevents accidental confirmations
 * - Non-blocking (replaces window.confirm)
 */

import { Modal } from './Modal';
import './ConfirmDialog.css';

export interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmVariant?: 'danger' | 'primary' | 'success';
  isProcessing?: boolean;
}

export const ConfirmDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  confirmVariant = 'primary',
  isProcessing = false,
}: ConfirmDialogProps) => {
  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="480px"
      closeOnOverlayClick={!isProcessing}
      closeOnEsc={!isProcessing}
      showCloseButton={false}
      ariaLabelledBy="confirm-dialog-title"
      ariaDescribedBy="confirm-dialog-description"
    >
      <div className="confirm-dialog">
        <h2 id="confirm-dialog-title" className="confirm-dialog-title">
          {title}
        </h2>
        <p id="confirm-dialog-description" className="confirm-dialog-description">
          {description}
        </p>
        <div className="confirm-dialog-actions">
          <button
            onClick={onClose}
            className="confirm-dialog-btn cancel"
            disabled={isProcessing}
            type="button"
          >
            {cancelLabel}
          </button>
          <button
            onClick={handleConfirm}
            className={`confirm-dialog-btn confirm ${confirmVariant}`}
            disabled={isProcessing}
            type="button"
            autoFocus
          >
            {isProcessing ? 'Processing...' : confirmLabel}
          </button>
        </div>
      </div>
    </Modal>
  );
};
