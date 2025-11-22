// TODO-S0-STUB: TypeScript checking disabled - fix inventory types
// @ts-nocheck
/**
 * IncomingInvoices - Bevételezés Management
 *
 * Features:
 * - List supplier invoices (Draft, Finalized, etc.)
 * - Create new invoice (manual or OCR upload)
 * - Finalize invoice to update stock
 * - View invoice details
 */

import { useState, useEffect } from 'react';
import {
  getSupplierInvoices,
  finalizeInvoice,
  deleteSupplierInvoice,
  type SupplierInvoice,
} from '@/services/inventoryService';
import { InvoiceEditor } from './InvoiceEditor';
import './IncomingInvoices.css';

export const IncomingInvoices = () => {
  const [invoices, setInvoices] = useState<SupplierInvoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Editor modal state
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingInvoice, setEditingInvoice] = useState<SupplierInvoice | null>(null);

  // Fetch invoices
  const fetchInvoices = async () => {
    try {
      setIsLoading(true);
      const response = await getSupplierInvoices(page, pageSize);
      setInvoices(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Error fetching invoices:', error);
      alert('Nem sikerült betölteni a számlákat!');
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchInvoices();
  }, [page]);

  // Create new invoice
  const handleCreate = () => {
    setEditingInvoice(null);
    setIsEditorOpen(true);
  };

  // View/Edit invoice
  const handleView = (invoice: SupplierInvoice) => {
    setEditingInvoice(invoice);
    setIsEditorOpen(true);
  };

  // Finalize invoice
  const handleFinalize = async (invoice: SupplierInvoice) => {
    const confirmed = window.confirm(
      `Véglegesíteni szeretnéd ezt a számlát?\n\nSzállító: ${
        invoice.supplier_name || 'Ismeretlen'
      }\nÖsszeg: ${invoice.total_amount || 0} Ft\n\nEz növelni fogja a készletet!`
    );

    if (!confirmed) return;

    try {
      await finalizeInvoice(invoice.id);
      alert('Számla sikeresen véglegesítve! A készlet frissítve.');
      fetchInvoices();
    } catch (error) {
      console.error('Error finalizing invoice:', error);
      alert('Nem sikerült véglegesíteni a számlát!');
    }
  };

  // Delete invoice
  const handleDelete = async (invoice: SupplierInvoice) => {
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt a számlát?\n\nSzállító: ${
        invoice.supplier_name || 'Ismeretlen'
      }`
    );

    if (!confirmed) return;

    try {
      await deleteSupplierInvoice(invoice.id);
      alert('Számla sikeresen törölve!');
      fetchInvoices();
    } catch (error) {
      console.error('Error deleting invoice:', error);
      alert('Nem sikerült törölni a számlát!');
    }
  };

  // Editor close handler
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingInvoice(null);
    if (shouldRefresh) {
      fetchInvoices();
    }
  };

  // Pagination
  const totalPages = Math.ceil(total / pageSize);

  // Status badge helper
  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; class: string }> = {
      'FELDOLGOZÁSRA VÁR': { label: 'Vár', class: 'status-pending' },
      VÉGLEGESÍTVE: { label: 'Véglegesítve', class: 'status-finalized' },
      DRAFT: { label: 'Piszkozat', class: 'status-draft' },
      JÓVÁHAGYVA: { label: 'Jóváhagyva', class: 'status-approved' },
    };

    const statusInfo = statusMap[status] || { label: status, class: 'status-default' };

    return <span className={`status-badge ${statusInfo.class}`}>{statusInfo.label}</span>;
  };

  return (
    <div className="incoming-invoices">
      {/* Header with actions */}
      <div className="invoices-header">
        <div>
          <h3>📋 Beszállítói számlák</h3>
          <p className="subtitle">Összes számla: {total}</p>
        </div>

        <div className="invoices-actions">
          <button onClick={fetchInvoices} className="btn btn-secondary">
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="btn btn-primary">
            ➕ Új bevételezés
          </button>
        </div>
      </div>

      {/* Invoices table */}
      {isLoading ? (
        <div className="loading">Betöltés...</div>
      ) : (
        <>
          <table className="invoices-table">
            <thead>
              <tr>
                <th>Szállító</th>
                <th>Dátum</th>
                <th>Összeg</th>
                <th>Státusz</th>
                <th>Műveletek</th>
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={5} className="no-data">
                    Nincs megjeleníthető számla
                  </td>
                </tr>
              ) : (
                invoices.map((invoice) => (
                  <tr key={invoice.id}>
                    <td>
                      <strong>{invoice.supplier_name || 'Ismeretlen szállító'}</strong>
                    </td>
                    <td>
                      {invoice.invoice_date
                        ? new Date(invoice.invoice_date).toLocaleDateString('hu-HU')
                        : '-'}
                    </td>
                    <td className="numeric">
                      {invoice.total_amount
                        ? `${invoice.total_amount.toLocaleString('hu-HU')} Ft`
                        : '-'}
                    </td>
                    <td>{getStatusBadge(invoice.status)}</td>
                    <td className="actions">
                      <button
                        onClick={() => handleView(invoice)}
                        className="btn-icon"
                        title="Megtekintés"
                      >
                        👁️
                      </button>
                      {invoice.status !== 'VÉGLEGESÍTVE' && (
                        <button
                          onClick={() => handleFinalize(invoice)}
                          className="btn-icon success"
                          title="Véglegesítés"
                        >
                          ✅
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(invoice)}
                        className="btn-icon danger"
                        title="Törlés"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="btn btn-secondary"
              >
                ‹ Előző
              </button>
              <span className="page-info">
                {page}. oldal / {totalPages}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="btn btn-secondary"
              >
                Következő ›
              </button>
            </div>
          )}
        </>
      )}

      {/* Editor Modal */}
      {isEditorOpen && (
        <InvoiceEditor invoice={editingInvoice} onClose={handleEditorClose} />
      )}
    </div>
  );
};
