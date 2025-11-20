/**
 * InvoicesList - Szállítói számlák listázása és véglegesítése
 *
 * Funkciók:
 *   - Számlák táblázatos megjelenítése
 *   - OCR státusz jelzése
 *   - Számla feltöltése OCR feldolgozásra
 *   - **VÉGLEGESÍTÉS GOMB** - Számla véglegesítése
 *   - Szűrés OCR státusz és véglegesítés szerint
 */

import { useState, useEffect } from 'react';
import { getInvoices, uploadInvoice, finalizeInvoice } from '@/services/inventoryService';
import type { SupplierInvoice } from '@/types/inventory';
import './Inventory.css';

export const InvoicesList = () => {
  const [invoices, setInvoices] = useState<SupplierInvoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [ocrStatusFilter, setOcrStatusFilter] = useState<string>('');
  const [finalizedFilter, setFinalizedFilter] = useState<string>('');
  const [uploadingFile, setUploadingFile] = useState(false);

  // Számlák betöltése
  const fetchInvoices = async () => {
    try {
      setIsLoading(true);
      const data = await getInvoices({
        ocr_status: ocrStatusFilter || undefined,
        finalized: finalizedFilter ? finalizedFilter === 'true' : undefined,
        limit: 100,
      });
      setInvoices(data);
    } catch (error) {
      console.error('Hiba a számlák betöltésekor:', error);
      alert('Nem sikerült betölteni a számlákat!');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, [ocrStatusFilter, finalizedFilter]);

  // Számla feltöltése
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setUploadingFile(true);
      await uploadInvoice(file);
      alert('Számla sikeresen feltöltve! OCR feldolgozás folyamatban...');
      fetchInvoices();
      // Reset file input
      event.target.value = '';
    } catch (error) {
      console.error('Hiba a számla feltöltésekor:', error);
      alert('Nem sikerült feltölteni a számlát!');
    } finally {
      setUploadingFile(false);
    }
  };

  // **VÉGLEGESÍTÉS GOMB FUNKCIÓ**
  const handleFinalize = async (invoiceId: number) => {
    if (!confirm('Biztosan véglegesíted ezt a számlát? Ez a művelet nem visszavonható!')) return;

    try {
      await finalizeInvoice(invoiceId);
      alert('Számla sikeresen véglegesítve!');
      fetchInvoices();
    } catch (error) {
      console.error('Hiba a számla véglegesítésekor:', error);
      alert('Nem sikerült véglegesíteni a számlát!');
    }
  };

  // Dátum formázás
  const formatDate = (dateStr?: string | null): string => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('hu-HU');
  };

  // Ár formázás
  const formatPrice = (price?: number | null, currency?: string | null): string => {
    if (price === undefined || price === null) return '-';
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: currency || 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  // OCR státusz badge
  const getOcrStatusBadge = (status: string): JSX.Element => {
    const statusMap: Record<string, { label: string; className: string }> = {
      pending: { label: 'Várakozik', className: 'ocr-pending' },
      processing: { label: 'Feldolgozás...', className: 'ocr-processing' },
      completed: { label: 'Kész', className: 'ocr-completed' },
      failed: { label: 'Hiba', className: 'ocr-failed' },
    };

    const { label, className } = statusMap[status] || { label: status, className: '' };

    return <span className={`ocr-badge ${className}`}>{label}</span>;
  };

  // Véglegesítés státusz badge
  const getFinalizedBadge = (finalized: boolean): JSX.Element => {
    return finalized ? (
      <span className="finalized-badge finalized-yes">✅ Véglegesítve</span>
    ) : (
      <span className="finalized-badge finalized-no">⏳ Nem véglegesített</span>
    );
  };

  return (
    <div className="invoices-list">
      {/* Fejléc */}
      <header className="list-header">
        <h2>📄 Szállítói számlák (OCR)</h2>
        <div className="header-controls">
          <select
            value={ocrStatusFilter}
            onChange={(e) => setOcrStatusFilter(e.target.value)}
            className="status-filter"
          >
            <option value="">Összes OCR státusz</option>
            <option value="pending">Várakozik</option>
            <option value="processing">Feldolgozás...</option>
            <option value="completed">Kész</option>
            <option value="failed">Hiba</option>
          </select>
          <select
            value={finalizedFilter}
            onChange={(e) => setFinalizedFilter(e.target.value)}
            className="status-filter"
          >
            <option value="">Összes véglegesítés</option>
            <option value="true">Véglegesített</option>
            <option value="false">Nem véglegesített</option>
          </select>
          <button onClick={fetchInvoices} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <label htmlFor="file-upload" className="upload-btn">
            {uploadingFile ? '⏳ Feltöltés...' : '📤 Számla feltöltése'}
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={handleFileUpload}
            disabled={uploadingFile}
            style={{ display: 'none' }}
          />
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && invoices.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="invoices-table">
              <thead>
                <tr>
                  <th>Azonosító</th>
                  <th>Számlaszám</th>
                  <th>Szállító</th>
                  <th>Számla dátuma</th>
                  <th>Összeg</th>
                  <th>OCR státusz</th>
                  <th>Véglegesítés</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {invoices.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="empty-state">
                      Nincsenek számlák
                    </td>
                  </tr>
                ) : (
                  invoices.map((invoice) => (
                    <tr key={invoice.id}>
                      <td>#{invoice.id}</td>
                      <td>{invoice.invoice_number || '-'}</td>
                      <td>{invoice.supplier_name || '-'}</td>
                      <td>{formatDate(invoice.invoice_date)}</td>
                      <td>{formatPrice(invoice.total_amount, invoice.currency)}</td>
                      <td>{getOcrStatusBadge(invoice.ocr_status)}</td>
                      <td>{getFinalizedBadge(invoice.finalized)}</td>
                      <td>
                        {!invoice.finalized && invoice.ocr_status === 'completed' && (
                          <button
                            onClick={() => handleFinalize(invoice.id)}
                            className="action-btn finalize-btn"
                            title="Véglegesítés"
                          >
                            ✅ Véglegesítés
                          </button>
                        )}
                        {invoice.finalized && (
                          <span className="finalized-marker" title={`Véglegesítve: ${formatDate(invoice.finalized_at)}`}>
                            🔒
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};
