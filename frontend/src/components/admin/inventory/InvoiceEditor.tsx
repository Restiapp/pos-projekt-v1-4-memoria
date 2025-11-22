// TODO-S0-STUB: TypeScript checking disabled - fix inventory types
// @ts-nocheck
/**
 * InvoiceEditor - Modal for creating/editing supplier invoices
 *
 * Features:
 * - Manual invoice entry (supplier, date, amount)
 * - OCR upload support (future enhancement)
 * - View existing invoice details
 */

import { useState, useEffect } from 'react';
import {
  createSupplierInvoice,
  uploadInvoice,
  type SupplierInvoice,
  type SupplierInvoiceCreate,
} from '@/services/inventoryService';
import './InvoiceEditor.css';

interface InvoiceEditorProps {
  invoice: SupplierInvoice | null;
  onClose: (shouldRefresh: boolean) => void;
}

export const InvoiceEditor = ({ invoice, onClose }: InvoiceEditorProps) => {
  const isViewMode = !!invoice;

  const [formData, setFormData] = useState({
    supplier_name: invoice?.supplier_name || '',
    invoice_date: invoice?.invoice_date || new Date().toISOString().split('T')[0],
    total_amount: invoice?.total_amount || 0,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadMode, setUploadMode] = useState(false);

  // Handle form field changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'total_amount' ? parseFloat(value) || 0 : value,
    }));
  };

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadFile(e.target.files[0]);
    }
  };

  // Handle manual form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.supplier_name.trim()) {
      alert('A szállító neve kötelező!');
      return;
    }

    try {
      setIsSubmitting(true);

      const createData: SupplierInvoiceCreate = {
        supplier_name: formData.supplier_name,
        invoice_date: formData.invoice_date,
        total_amount: formData.total_amount,
        status: 'DRAFT',
      };

      await createSupplierInvoice(createData);
      alert('Számla sikeresen létrehozva!');
      onClose(true);
    } catch (error: any) {
      console.error('Error creating invoice:', error);
      alert(
        error.response?.data?.detail || 'Nem sikerült létrehozni a számlát!'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle OCR upload
  const handleUpload = async () => {
    if (!uploadFile) {
      alert('Válassz ki egy fájlt!');
      return;
    }

    try {
      setIsSubmitting(true);
      await uploadInvoice(uploadFile);
      alert('Számla sikeresen feltöltve és feldolgozva OCR-rel!');
      onClose(true);
    } catch (error: any) {
      console.error('Error uploading invoice:', error);
      alert(
        error.response?.data?.detail || 'Nem sikerült feltölteni a számlát!'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Close on ESC key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose(false);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  return (
    <div className="modal-overlay" onClick={() => onClose(false)}>
      <div className="modal-content invoice-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            {isViewMode
              ? '👁️ Számla részletei'
              : uploadMode
              ? '📤 Számla feltöltés (OCR)'
              : '➕ Új bevételezés'}
          </h2>
          <button onClick={() => onClose(false)} className="close-btn">
            ✕
          </button>
        </div>

        {isViewMode ? (
          // View Mode: Display invoice details
          <div className="modal-form">
            <div className="detail-group">
              <label>Szállító:</label>
              <div className="detail-value">
                {invoice.supplier_name || 'Ismeretlen'}
              </div>
            </div>

            <div className="detail-group">
              <label>Dátum:</label>
              <div className="detail-value">
                {invoice.invoice_date
                  ? new Date(invoice.invoice_date).toLocaleDateString('hu-HU')
                  : '-'}
              </div>
            </div>

            <div className="detail-group">
              <label>Összeg:</label>
              <div className="detail-value">
                {invoice.total_amount
                  ? `${invoice.total_amount.toLocaleString('hu-HU')} Ft`
                  : '-'}
              </div>
            </div>

            <div className="detail-group">
              <label>Státusz:</label>
              <div className="detail-value">
                <strong>{invoice.status}</strong>
              </div>
            </div>

            {invoice.ocr_data && (
              <div className="detail-group">
                <label>OCR adatok:</label>
                <div className="detail-value ocr-data">
                  <pre>{JSON.stringify(invoice.ocr_data, null, 2)}</pre>
                </div>
              </div>
            )}

            <div className="modal-actions">
              <button
                onClick={() => onClose(false)}
                className="btn btn-secondary"
              >
                Bezárás
              </button>
            </div>
          </div>
        ) : uploadMode ? (
          // Upload Mode: OCR file upload
          <div className="modal-form">
            <div className="form-group">
              <label htmlFor="file">
                Számla fájl (PDF, JPG, PNG) <span className="required">*</span>
              </label>
              <input
                type="file"
                id="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileChange}
                className="file-input"
              />
              {uploadFile && (
                <div className="file-info">
                  Kiválasztott fájl: <strong>{uploadFile.name}</strong>
                </div>
              )}
            </div>

            <div className="info-box">
              ℹ️ A feltöltött számla automatikusan feldolgozásra kerül OCR
              technológiával, és kinyeri a szállító adatokat és tételeket.
            </div>

            <div className="modal-actions">
              <button
                onClick={() => setUploadMode(false)}
                className="btn btn-secondary"
                disabled={isSubmitting}
              >
                ‹ Vissza
              </button>
              <button
                onClick={handleUpload}
                className="btn btn-primary"
                disabled={isSubmitting || !uploadFile}
              >
                {isSubmitting ? 'Feltöltés...' : '📤 Feltöltés'}
              </button>
            </div>
          </div>
        ) : (
          // Create Mode: Manual entry form
          <form onSubmit={handleSubmit} className="modal-form">
            <div className="mode-selector">
              <button
                type="button"
                onClick={() => setUploadMode(true)}
                className="btn btn-secondary"
              >
                📤 Számla feltöltés (OCR)
              </button>
            </div>

            <div className="form-group">
              <label htmlFor="supplier_name">
                Szállító neve <span className="required">*</span>
              </label>
              <input
                type="text"
                id="supplier_name"
                name="supplier_name"
                value={formData.supplier_name}
                onChange={handleChange}
                placeholder="pl. Metro Cash & Carry"
                required
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="invoice_date">
                Számla dátuma <span className="required">*</span>
              </label>
              <input
                type="date"
                id="invoice_date"
                name="invoice_date"
                value={formData.invoice_date}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="total_amount">
                Végösszeg (Ft) <span className="required">*</span>
              </label>
              <input
                type="number"
                id="total_amount"
                name="total_amount"
                value={formData.total_amount}
                onChange={handleChange}
                step="0.01"
                min="0"
                required
              />
            </div>

            <div className="info-box">
              ℹ️ A számla piszkozatként kerül mentésre. A véglegesítés után
              frissül a készlet.
            </div>

            <div className="modal-actions">
              <button
                type="button"
                onClick={() => onClose(false)}
                className="btn btn-secondary"
                disabled={isSubmitting}
              >
                Mégse
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Mentés...' : 'Létrehozás'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
