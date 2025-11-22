/**
 * StartOrderModal - Modal for starting a new order
 *
 * Features:
 * - Manual sequence number input
 * - Auto-generate sequence number via API
 * - Continue to create order
 * - Cancel action
 */

import { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { useToast } from '@/hooks/useToast';
import { getNextOrderSequence } from '@/services/orderService';
import './StartOrderModal.css';

export interface StartOrderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStart: (orderData: { sequence_number: number }) => void;
}

export const StartOrderModal = ({
  isOpen,
  onClose,
  onStart,
}: StartOrderModalProps) => {
  const toast = useToast();
  const [sequenceNumber, setSequenceNumber] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Generate new sequence number from API
   */
  const handleGenerateNew = async () => {
    try {
      setIsGenerating(true);
      const response = await getNextOrderSequence();
      setSequenceNumber(response.sequence_number.toString());
      toast.success('Új sorszám generálva!');
    } catch (error: any) {
      console.error('Failed to generate sequence number:', error);
      const errorMsg =
        error.response?.data?.detail || 'Hiba történt a sorszám generálása közben!';
      toast.error(errorMsg);
    } finally {
      setIsGenerating(false);
    }
  };

  /**
   * Handle Continue button click
   */
  const handleContinue = () => {
    // Validate sequence number
    const sequenceNum = parseInt(sequenceNumber, 10);
    if (!sequenceNumber || isNaN(sequenceNum) || sequenceNum <= 0) {
      toast.error('Kérjük, adjon meg egy érvényes sorszámot vagy generáljon újat!');
      return;
    }

    setIsSubmitting(true);
    try {
      // Call onStart with the order data
      onStart({ sequence_number: sequenceNum });
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle Cancel button click
   */
  const handleCancel = () => {
    setSequenceNumber('');
    onClose();
  };

  /**
   * Handle Enter key press
   */
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && sequenceNumber) {
      handleContinue();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleCancel}
      title="Új rendelés indítása"
      maxWidth="500px"
      closeOnOverlayClick={!isSubmitting && !isGenerating}
      showCloseButton={!isSubmitting && !isGenerating}
    >
      <div className="start-order-modal">
        <div className="start-order-modal-body">
          {/* Sequence Number Input */}
          <div className="form-group">
            <label htmlFor="sequence-number">
              Rendelés sorszáma:
            </label>
            <div className="input-with-button">
              <input
                id="sequence-number"
                type="number"
                value={sequenceNumber}
                onChange={(e) => setSequenceNumber(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Adja meg a sorszámot"
                disabled={isGenerating || isSubmitting}
                min="1"
                step="1"
                className="sequence-input"
              />
              <button
                onClick={handleGenerateNew}
                disabled={isGenerating || isSubmitting}
                className="generate-btn"
                type="button"
              >
                {isGenerating ? 'Generálás...' : 'Új sorszám'}
              </button>
            </div>
          </div>

          {/* Info Text */}
          <p className="info-text">
            Adjon meg egy sorszámot manuálisan, vagy kattintson az "Új sorszám" gombra
            egy automatikusan generált sorszámhoz.
          </p>
        </div>

        {/* Footer Buttons */}
        <div className="start-order-modal-footer">
          <button
            onClick={handleCancel}
            disabled={isSubmitting || isGenerating}
            className="cancel-btn"
            type="button"
          >
            Mégse
          </button>
          <button
            onClick={handleContinue}
            disabled={!sequenceNumber || isSubmitting || isGenerating}
            className="continue-btn"
            type="button"
          >
            {isSubmitting ? 'Folytatás...' : 'Folytatás'}
          </button>
        </div>
      </div>
    </Modal>
  );
};
