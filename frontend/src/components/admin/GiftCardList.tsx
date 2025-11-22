/**
 * GiftCardList - Ajándékkártyák listázása és kezelése
 *
 * Funkciók:
 *   - Ajándékkártyák listázása táblázatban (lapozással)
 *   - Új ajándékkártya létrehozása (modal nyitás)
 *   - Ajándékkártya szerkesztése (modal nyitás)
 *   - Ajándékkártya törlése (megerősítéssel)
 *   - Frissítés gomb
 *   - Szűrés (aktív/inaktív kártyák)
 */

import { useState, useEffect } from 'react';
import { getGiftCards, deleteGiftCard } from '@/services/crmService';
import { GiftCardEditor } from './GiftCardEditor';
import type { GiftCard } from '@/types/giftCard';
import { useAuthStore } from '@/stores/authStore';
import './GiftCardList.css';
import { notifications } from '@mantine/notifications';

export const GiftCardList = () => {
  const { isAuthenticated } = useAuthStore();
  const [giftCards, setGiftCards] = useState<GiftCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingGiftCard, setEditingGiftCard] = useState<GiftCard | null>(null);

  // Szűrő állapot
  const [showOnlyActive, setShowOnlyActive] = useState(true);

  // Ajándékkártyák betöltése
  const fetchGiftCards = async () => {
    try {
      setIsLoading(true);
      const response = await getGiftCards(
        page,
        pageSize,
        showOnlyActive ? true : undefined
      );
      setGiftCards(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Hiba az ajándékkártyák betöltésekor:', error);
      notifications.show({
        title: 'Hiba',
        message: 'Nem sikerült betölteni az ajándékkártyákat!',
        color: 'red',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Első betöltés
  useEffect(() => {
    if (isAuthenticated) {
      fetchGiftCards();
    }
  }, [page, showOnlyActive, isAuthenticated]);

  // Új ajándékkártya létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingGiftCard(null);
    setIsEditorOpen(true);
  };

  // Ajándékkártya szerkesztése (modal nyitás)
  const handleEdit = (giftCard: GiftCard) => {
    setEditingGiftCard(giftCard);
    setIsEditorOpen(true);
  };

  // Ajándékkártya törlése (megerősítéssel)
  const handleDelete = async (giftCard: GiftCard) => {
    const confirmed = await showConfirm(
      `Biztosan törölni szeretnéd ezt az ajándékkártyát?\n\n${giftCard.card_code}`
    );

    if (!confirmed) return;

    try {
      await deleteGiftCard(giftCard.id);
      notifications.show({
        title: 'Siker',
        message: 'Ajándékkártya sikeresen törölve!',
        color: 'green',
      });
      fetchGiftCards(); // Lista frissítése
    } catch (error) {
      console.error('Hiba az ajándékkártya törlésekor:', error);
      notifications.show({
        title: 'Hiba',
        message: 'Nem sikerült törölni az ajándékkártyát!',
        color: 'red',
      });
    }
  };

  // Editor bezárása és lista frissítése
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingGiftCard(null);
    if (shouldRefresh) {
      fetchGiftCards();
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
    <div className="gift-card-list">
      {/* Fejléc */}
      <header className="list-header">
        <h1>🎁 Ajándékkártyák</h1>
        <div className="header-controls">
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={showOnlyActive}
              onChange={(e) => setShowOnlyActive(e.target.checked)}
            />
            Csak aktív kártyák
          </label>
          <button onClick={fetchGiftCards} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="create-btn">
            ➕ Új ajándékkártya
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && giftCards.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="gift-cards-table">
              <thead>
                <tr>
                  <th>Kártyakód</th>
                  <th>Kezdeti érték</th>
                  <th>Jelenlegi egyenleg</th>
                  <th>Felhasználás</th>
                  <th>Érvényesség</th>
                  <th>Kibocsátás</th>
                  <th>Állapot</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {giftCards.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="empty-state">
                      Nincsenek ajándékkártyák
                    </td>
                  </tr>
                ) : (
                  giftCards.map((giftCard) => (
                    <tr key={giftCard.id}>
                      <td>
                        <strong className="card-code">{giftCard.card_code}</strong>
                        {giftCard.is_assigned && (
                          <div className="assigned-badge">Hozzárendelve</div>
                        )}
                      </td>
                      <td>{formatPrice(giftCard.initial_balance)}</td>
                      <td>
                        <span
                          className={`balance ${
                            giftCard.current_balance === 0 ? 'depleted' : ''
                          }`}
                        >
                          {formatPrice(giftCard.current_balance)}
                        </span>
                      </td>
                      <td>
                        <div className="usage-bar-container">
                          <div
                            className="usage-bar"
                            style={{ width: `${giftCard.usage_percentage}%` }}
                          />
                          <span className="usage-text">
                            {giftCard.usage_percentage.toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td>{formatDate(giftCard.valid_until)}</td>
                      <td>{formatDate(giftCard.issued_at)}</td>
                      <td>
                        <span
                          className={`status-badge ${
                            giftCard.is_valid ? 'active' : 'inactive'
                          }`}
                        >
                          {giftCard.is_valid ? '✅ Érvényes' : '❌ Érvénytelen'}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(giftCard)}
                            className="edit-btn"
                            title="Szerkesztés"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDelete(giftCard)}
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
              Összesen: {total} ajándékkártya | Oldal: {page}
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
                disabled={giftCards.length < pageSize}
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
        <GiftCardEditor giftCard={editingGiftCard} onClose={handleEditorClose} />
      )}
    </div>
  );
};
