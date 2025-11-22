/**
 * CustomerList - Vendégek listázása és kezelése
 *
 * Funkciók:
 *   - Vendégek listázása táblázatban (lapozással)
 *   - Új vendég létrehozása (modal nyitás)
 *   - Vendég szerkesztése (modal nyitás)
 *   - Vendég törlése (megerősítéssel)
 *   - Frissítés gomb
 *   - Szűrés (aktív/inaktív vendégek)
 *   - Keresés (név, email)
 */

import { useState, useEffect } from 'react';
import { getCustomers, deleteCustomer, updateLoyaltyPoints } from '@/services/crmService';
import { CustomerEditor } from './CustomerEditor';
import type { Customer } from '@/types/customer';
import { useToast } from '@/components/common/Toast';
import { useConfirm } from '@/components/common/ConfirmDialog';
import './CustomerList.css';

export const CustomerList = () => {
  // TODO-S0-STUB: Replace with proper useAuth hook
  const isAuthenticated = true;

  const { showToast } = useToast();
  const { showConfirm } = useConfirm();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);

  // Loyalty points modal állapot
  const [isLoyaltyModalOpen, setIsLoyaltyModalOpen] = useState(false);
  const [loyaltyCustomer, setLoyaltyCustomer] = useState<Customer | null>(null);
  const [loyaltyPoints, setLoyaltyPoints] = useState<number>(0);
  const [loyaltyReason, setLoyaltyReason] = useState<string>('');

  // Szűrő állapot
  const [showOnlyActive, setShowOnlyActive] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  // Vendégek betöltése
  const fetchCustomers = async () => {
    try {
      setIsLoading(true);
      const response = await getCustomers(
        page,
        pageSize,
        showOnlyActive ? true : undefined,
        searchTerm || undefined
      );
      setCustomers(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Hiba a vendégek betöltésekor:', error);
      showToast('Nem sikerült betölteni a vendégeket!', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés és frissítés szűrő/keresés változásakor
  useEffect(() => {
    if (isAuthenticated) {
      fetchCustomers();
    }
  }, [page, showOnlyActive, searchTerm, isAuthenticated]);

  // Új vendég létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingCustomer(null);
    setIsEditorOpen(true);
  };

  // Vendég szerkesztése (modal nyitás)
  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setIsEditorOpen(true);
  };

  // Vendég törlése (megerősítéssel)
  const handleDelete = async (customer: Customer) => {
    const confirmed = await showConfirm(
      `Biztosan törölni szeretnéd ezt a vendéget?\n\n${customer.first_name} ${customer.last_name} (${customer.email})`
    );

    if (!confirmed) return;

    try {
      await deleteCustomer(customer.id);
      showToast('Vendég sikeresen törölve!', 'success');
      fetchCustomers(); // Lista frissítése
    } catch (error) {
      console.error('Hiba a vendég törlésekor:', error);
      showToast('Nem sikerült törölni a vendéget!', 'error');
    }
  };

  // Editor bezárása és lista frissítése
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingCustomer(null);
    if (shouldRefresh) {
      fetchCustomers();
    }
  };

  // Pontjóváírás modal megnyitása
  const handleOpenLoyaltyModal = (customer: Customer) => {
    setLoyaltyCustomer(customer);
    setLoyaltyPoints(0);
    setLoyaltyReason('');
    setIsLoyaltyModalOpen(true);
  };

  // Pontjóváírás mentése
  const handleSaveLoyaltyPoints = async () => {
    if (!loyaltyCustomer) return;

    if (loyaltyPoints === 0) {
      alert('A pontok értéke nem lehet 0!');
      return;
    }

    try {
      await updateLoyaltyPoints(loyaltyCustomer.id, {
        points: loyaltyPoints,
        reason: loyaltyReason || undefined,
      });
      alert('Hűségpontok sikeresen frissítve!');
      setIsLoyaltyModalOpen(false);
      setLoyaltyCustomer(null);
      fetchCustomers(); // Lista frissítése
    } catch (error: any) {
      console.error('Hiba a pontok frissítésekor:', error);
      const errorMessage =
        error.response?.data?.detail || 'Nem sikerült frissíteni a pontokat!';
      alert(errorMessage);
    }
  };

  // Ár formázása
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  // Dátum formázása
  const formatDate = (dateStr?: string): string => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('hu-HU');
  };

  return (
    <div className="customer-list">
      {/* Fejléc */}
      <header className="list-header">
        <h1>👥 Vendégek</h1>
        <div className="header-controls">
          <input
            type="text"
            placeholder="Keresés (név, email)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={showOnlyActive}
              onChange={(e) => setShowOnlyActive(e.target.checked)}
            />
            Csak aktív vendégek
          </label>
          <button onClick={fetchCustomers} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="create-btn">
            ➕ Új vendég
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && customers.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="customers-table">
              <thead>
                <tr>
                  <th>Vendégszám</th>
                  <th>Név</th>
                  <th>Email</th>
                  <th>Telefon</th>
                  <th>Tag-ek</th>
                  <th>Utolsó látogatás</th>
                  <th>Hűségpontok</th>
                  <th>Össz. költés</th>
                  <th>Rendelések</th>
                  <th>Aktív</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {customers.length === 0 ? (
                  <tr>
                    <td colSpan={11} className="empty-state">
                      Nincsenek vendégek
                    </td>
                  </tr>
                ) : (
                  customers.map((customer) => (
                    <tr key={customer.id}>
                      <td>
                        <span className="customer-uid">{customer.customer_uid}</span>
                      </td>
                      <td>
                        <strong>
                          {customer.first_name} {customer.last_name}
                        </strong>
                        {customer.birth_date && (
                          <div className="customer-birth-date">
                            🎂 {formatDate(customer.birth_date)}
                          </div>
                        )}
                      </td>
                      <td>{customer.email}</td>
                      <td>{customer.phone || '-'}</td>
                      <td>
                        {customer.tags && customer.tags.length > 0 ? (
                          <div className="customer-tags">
                            {customer.tags.map((tag, idx) => (
                              <span key={idx} className="tag-badge">
                                {tag}
                              </span>
                            ))}
                          </div>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td>{formatDate(customer.last_visit)}</td>
                      <td>
                        <span className="loyalty-points">{customer.loyalty_points} pt</span>
                      </td>
                      <td>{formatPrice(customer.total_spent)}</td>
                      <td>{customer.total_orders}</td>
                      <td>
                        <span
                          className={`status-badge ${
                            customer.is_active ? 'active' : 'inactive'
                          }`}
                        >
                          {customer.is_active ? '✅ Aktív' : '❌ Inaktív'}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleOpenLoyaltyModal(customer)}
                            className="loyalty-btn"
                            title="Pontjóváírás"
                          >
                            💎
                          </button>
                          <button
                            onClick={() => handleEdit(customer)}
                            className="edit-btn"
                            title="Szerkesztés"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDelete(customer)}
                            className="delete-btn"
                            title="Törlés"
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Lapozás */}
          <footer className="list-footer">
            <div className="pagination-info">
              Összesen: {total} vendég | Oldal: {page}
            </div>
            <div className="pagination-controls">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="page-btn"
              >
                ◀ Előző
              </button>
              <span className="page-number">Oldal {page}</span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={customers.length < pageSize}
                className="page-btn"
              >
                Következő ▶
              </button>
            </div>
          </footer>
        </>
      )}

      {/* Editor Modal */}
      {isEditorOpen && (
        <CustomerEditor customer={editingCustomer} onClose={handleEditorClose} />
      )}

      {/* Loyalty Points Modal */}
      {isLoyaltyModalOpen && loyaltyCustomer && (
        <div
          className="modal-overlay"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setIsLoyaltyModalOpen(false);
              setLoyaltyCustomer(null);
            }
          }}
        >
          <div className="modal-content">
            <header className="modal-header">
              <h2>💎 Pontjóváírás</h2>
              <button
                onClick={() => {
                  setIsLoyaltyModalOpen(false);
                  setLoyaltyCustomer(null);
                }}
                className="close-btn"
              >
                ✕
              </button>
            </header>

            <div className="loyalty-modal-body">
              <div className="customer-info">
                <p>
                  <strong>Vendég:</strong> {loyaltyCustomer.first_name}{' '}
                  {loyaltyCustomer.last_name}
                </p>
                <p>
                  <strong>Jelenlegi pontok:</strong>{' '}
                  <span className="loyalty-points">{loyaltyCustomer.loyalty_points} pt</span>
                </p>
              </div>

              <div className="form-group">
                <label htmlFor="loyalty-points">
                  Pontok <span className="required">*</span>
                </label>
                <input
                  id="loyalty-points"
                  type="number"
                  value={loyaltyPoints}
                  onChange={(e) => setLoyaltyPoints(parseFloat(e.target.value) || 0)}
                  placeholder="Pozitív érték hozzáadáshoz, negatív kivonáshoz"
                  step="0.01"
                />
                <small>
                  Új egyenleg:{' '}
                  <strong>
                    {(loyaltyCustomer.loyalty_points + loyaltyPoints).toFixed(2)} pt
                  </strong>
                </small>
              </div>

              <div className="form-group">
                <label htmlFor="loyalty-reason">Indoklás (opcionális)</label>
                <textarea
                  id="loyalty-reason"
                  value={loyaltyReason}
                  onChange={(e) => setLoyaltyReason(e.target.value)}
                  placeholder="pl. Panaszkezelés, ajándék pontok, stb."
                  rows={3}
                />
              </div>
            </div>

            <footer className="modal-footer">
              <button
                type="button"
                onClick={() => {
                  setIsLoyaltyModalOpen(false);
                  setLoyaltyCustomer(null);
                }}
                className="cancel-btn"
              >
                Mégse
              </button>
              <button onClick={handleSaveLoyaltyPoints} className="save-btn">
                💾 Mentés
              </button>
            </footer>
          </div>
        </div>
      )}
    </div>
  );
};
