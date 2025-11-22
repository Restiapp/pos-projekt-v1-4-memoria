/**
 * ProductList - Termékek listázása és kezelése
 *
 * Funkciók:
 *   - Termékek listázása táblázatban (lapozással)
 *   - Új termék létrehozása (modal nyitás)
 *   - Termék szerkesztése (modal nyitás)
 *   - Termék törlése (megerősítéssel)
 *   - Frissítés gomb
 *   - Szűrés (aktív/inaktív termékek)
 *   - Keresés (név, SKU) - 300ms debounce-szal
 */

import { useState, useEffect } from 'react';
import { getProducts, deleteProduct, getCategories } from '@/services/menuService';
import { ProductEditor } from './ProductEditor';
import { useDebounce } from '@/hooks/useDebounce';
import type { Product, Category } from '@/types/menu';
import './ProductList.css';

export const ProductList = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Modal állapot (editor)
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  // Szűrő állapot
  const [showOnlyActive, setShowOnlyActive] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  // Termékek betöltése
  const fetchProducts = async () => {
    try {
      setIsLoading(true);
      const response = await getProducts(
        page,
        pageSize,
        showOnlyActive ? true : undefined,
        debouncedSearchQuery || undefined
      );
      setProducts(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Hiba a termékek betöltésekor:', error);
      alert('Nem sikerült betölteni a termékeket!');
    } finally {
      setIsLoading(false);
    }
  };

  // Kategóriák betöltése (select dropdown-hoz)
  const fetchCategories = async () => {
    try {
      const response = await getCategories(1, 100);
      setCategories(response.items);
    } catch (error) {
      console.error('Hiba a kategóriák betöltésekor:', error);
    }
  };

  // Első betöltés
  useEffect(() => {
    fetchProducts();
  }, [page, showOnlyActive, debouncedSearchQuery]);

  useEffect(() => {
    fetchCategories();
  }, []);

  // Új termék létrehozása (modal nyitás)
  const handleCreate = () => {
    setEditingProduct(null);
    setIsEditorOpen(true);
  };

  // Termék szerkesztése (modal nyitás)
  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setIsEditorOpen(true);
  };

  // Termék törlése (megerősítéssel)
  const handleDelete = async (product: Product) => {
    const confirmed = window.confirm(
      `Biztosan törölni szeretnéd ezt a terméket?\n\n${product.name}`
    );

    if (!confirmed) return;

    try {
      await deleteProduct(product.id);
      alert('Termék sikeresen törölve!');
      fetchProducts(); // Lista frissítése
    } catch (error) {
      console.error('Hiba a termék törlésekor:', error);
      alert('Nem sikerült törölni a terméket!');
    }
  };

  // Editor bezárása és lista frissítése
  const handleEditorClose = (shouldRefresh: boolean) => {
    setIsEditorOpen(false);
    setEditingProduct(null);
    if (shouldRefresh) {
      fetchProducts();
    }
  };

  // Kategória neve ID alapján
  const getCategoryName = (categoryId?: number): string => {
    if (!categoryId) return '-';
    const category = categories.find((c) => c.id === categoryId);
    return category?.name || '-';
  };

  // Ár formázása
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="product-list">
      {/* Fejléc */}
      <header className="list-header">
        <h1>📦 Termékek</h1>
        <div className="header-controls">
          {/* Keresés */}
          <input
            type="text"
            placeholder="Keresés (név, SKU)..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(1);
            }}
            className="search-input"
          />

          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={showOnlyActive}
              onChange={(e) => {
                setShowOnlyActive(e.target.checked);
                setPage(1);
              }}
            />
            Csak aktív termékek
          </label>
          <button onClick={fetchProducts} className="refresh-btn" disabled={isLoading}>
            🔄 Frissítés
          </button>
          <button onClick={handleCreate} className="create-btn">
            ➕ Új termék
          </button>
        </div>
      </header>

      {/* Töltés állapot */}
      {isLoading && products.length === 0 ? (
        <div className="loading-state">Betöltés...</div>
      ) : (
        <>
          {/* Táblázat */}
          <div className="table-container">
            <table className="products-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Név</th>
                  <th>Kategória</th>
                  <th>Alap ár</th>
                  <th>SKU</th>
                  <th>Aktív</th>
                  <th>Műveletek</th>
                </tr>
              </thead>
              <tbody>
                {products.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="empty-state">
                      Nincsenek termékek
                    </td>
                  </tr>
                ) : (
                  products.map((product) => (
                    <tr key={product.id}>
                      <td>{product.id}</td>
                      <td>
                        <strong>{product.name}</strong>
                        {product.description && (
                          <div className="product-description">
                            {product.description}
                          </div>
                        )}
                      </td>
                      <td>{getCategoryName(product.category_id)}</td>
                      <td>{formatPrice(product.base_price)}</td>
                      <td>{product.sku || '-'}</td>
                      <td>
                        <span
                          className={`status-badge ${
                            product.is_active ? 'active' : 'inactive'
                          }`}
                        >
                          {product.is_active ? '✅ Aktív' : '❌ Inaktív'}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            onClick={() => handleEdit(product)}
                            className="edit-btn"
                            title="Szerkesztés"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDelete(product)}
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
              Összesen: {total} termék | Oldal: {page}
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
                disabled={products.length < pageSize}
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
        <ProductEditor
          product={editingProduct}
          categories={categories}
          onClose={handleEditorClose}
        />
      )}
    </div>
  );
};
