/**
 * CouponList - Kuponok listázása és kezelése
 *
 * Funkciók:
 *   - Kuponok listázása táblázatban (lapozással)
 *   - Új kupon létrehozása (modal nyitás)
 *   - Kupon szerkesztése (modal nyitás)
 *   - Kupon törlése (megerősítéssel)
 *   - Frissítés gomb
 *   - Szűrés (aktív/inaktív kuponok)
 */

import { useState, useEffect } from 'react';
import { getCoupons, deleteCoupon } from '@/services/crmService';
import { CouponEditor } from './CouponEditor';
import type { Coupon } from '@/types/coupon';
import { DiscountTypeEnum } from '@/types/coupon';
import { notify } from '@/utils/notifications';
import { useAuthStore } from '@/stores/authStore';
import './CouponList.css';

export const CouponList = () => {
  const { isAuthenticated } = useAuthStore();
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingCoupon, setEditingCoupon] = useState<Coupon | null>(null);

  // Szűrő állapot
  const [showOnlyActive, setShowOnlyActive] = useState(true);

  // Kuponok betöltése
  const fetchCoupons = async () => {
    try {
      setIsLoading(true);
      const response = await getCoupons(
        page,
        pageSize,
        showOnlyActive ? true : undefined
      );
      setCoupons(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Hiba a kuponok betöltésekor:', error);
      notify.error('Nem sikerült betölteni a kuponokat!');
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    if (isAuthenticated) {
      fetchCoupons();
    }
  }, [page, showOnlyActive, isAuthenticated]);

  // Új kupon létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingCoupon(null);
    setIsEditorOpen(true);
  };

  // Kupon szerkesztése (modal nyitás)
  const handleEdit = (coupon: Coupon) => {
    setEditingCoupon(coupon);
    setIsEditorOpen(true);
  };

  // Kupon törlése (megerősítéssel)
  const handleDelete = async (coupon: Coupon) => {
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt a kupont?\n\n${coupon.code}`
    );

    if (!confirmed) return;

    try {
      await deleteCoupon(coupon.id);
      notify.success('Kupon sikeresen törölve!');
      fetchCoupons(); // Lista frissítése
    } catch (error) {
      console.error('Hiba a kupon törlésekor:', error);
      notify.error('Nem sikerült törölni a kupont!');
    }
  };

  // Editor bezárása és lista frissítése
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingCoupon(null);
    if (shouldRefresh) {
      fetchCoupons();
    }
  };

  // Kedvezmény formázása
  const formatDiscount = (coupon: Coupon): string => {
    if (coupon.discount_type === DiscountTypeEnum.PERCENTAGE) {
      return `${coupon.discount_value}%`;
    } else {
      return new Intl.NumberFormat('hu-HU', {
        style: 'currency',
        currency: 'HUF',
        minimumFractionDigits: 0,
      }).format(coupon.discount_value);
    }
  };

  // Dátum formázása
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('hu-HU');
  };

  // Érvényesség ellenőrzése
  const isExpired = (coupon: Coupon): boolean => {
    if (!coupon.valid_until) return false;
    return new Date(coupon.valid_until) < new Date();
  };

  return (
    <div className="coupon-list">
      {/* Fejléc */}
      <header className="list-header">
        <h1>🎫 Kuponok</h1>
        <div className="header-controls">
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={showOnlyActive}
              onChange={(e) => setShowOnlyActive(e.target.checked)}
            />
            Csak aktív kuponok
          </label>
          <button onClick={fetchCoupons} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="create-btn">
            ➕ Új kupon
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && coupons.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="coupons-table">
              <thead>
                <tr>
                  <th>Kód</th>
                  <th>Leírás</th>
                  <th>Kedvezmény</th>
                  <th>Min. vásárlás</th>
                  <th>Használat</th>
                  <th>Érvényesség</th>
                  <th>Állapot</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {coupons.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="empty-state">
                      Nincsenek kuponok
                    </td>
                  </tr>
                ) : (
                  coupons.map((coupon) => (
                    <tr key={coupon.id}>
                      <td>
                        <strong className="coupon-code">{coupon.code}</strong>
                      </td>
                      <td>{coupon.description || '-'}</td>
                      <td>
                        <span className="discount-badge">
                          {formatDiscount(coupon)}
                        </span>
                      </td>
                      <td>
                        {coupon.min_purchase_amount
                          ? new Intl.NumberFormat('hu-HU', {
                              style: 'currency',
                              currency: 'HUF',
                              minimumFractionDigits: 0,
                            }).format(coupon.min_purchase_amount)
                          : '-'}
                      </td>
                      <td>
                        <span className="usage-info">
                          {coupon.usage_count}
                          {coupon.max_uses ? ` / ${coupon.max_uses}` : ' / ∞'}
                        </span>
                      </td>
                      <td>
                        <div className="validity-info">
                          <div>{formatDate(coupon.valid_from)}</div>
                          {coupon.valid_until && (
                            <div className={isExpired(coupon) ? 'expired' : ''}>
                              → {formatDate(coupon.valid_until)}
                            </div>
                          )}
                        </div>
                      </td>
                      <td>
                        <span
                          className={`status-badge ${
                            coupon.is_active && !isExpired(coupon)
                              ? 'active'
                              : 'inactive'
                          }`}
                        >
                          {coupon.is_active && !isExpired(coupon)
                            ? '✅ Aktív'
                            : '❌ Inaktív'}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(coupon)}
                            className="edit-btn"
                            title="Szerkesztés"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDelete(coupon)}
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
              Összesen: {total} kupon | Oldal: {page}
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
                disabled={coupons.length < pageSize}
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
        <CouponEditor coupon={editingCoupon} onClose={handleEditorClose} />
      )}
    </div>
  );
};
