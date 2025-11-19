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
import { getCustomers, deleteCustomer } from '@/services/crmService';
import { CustomerEditor } from './CustomerEditor';
import type { Customer } from '@/types/customer';
import { notify } from '@/utils/notifications';
import { useAuthStore } from '@/stores/authStore';
import './CustomerList.css';

export const CustomerList = () => {
  const { isAuthenticated } = useAuthStore();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);

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
      notify.error('Nem sikerült betölteni a vendégeket!');
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
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt a vendéget?\n\n${customer.first_name} ${customer.last_name} (${customer.email})`
    );

    if (!confirmed) return;

    try {
      await deleteCustomer(customer.id);
      notify.success('Vendég sikeresen törölve!');
      fetchCustomers(); // Lista frissítése
    } catch (error) {
      console.error('Hiba a vendég törlésekor:', error);
      notify.error('Nem sikerült törölni a vendéget!');
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
                    <td colSpan={9} className="empty-state">
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
    </div>
  );
};
