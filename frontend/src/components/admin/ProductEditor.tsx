/**
 * ProductEditor - Termék létrehozása / szerkesztése (Modal)
 *
 * Funkciók:
 *   - Új termék létrehozása (POST /api/products)
 *   - Meglévő termék szerkesztése (PUT /api/products/{id})
 *   - Validáció (név kötelező, ár >= 0)
 *   - Kategória választás (dropdown)
 *   - Modal overlay (háttérre kattintva bezárás)
 */

import { useState, useEffect } from 'react';
import { createProduct, updateProduct } from '@/services/menuService';
import type { Product, Category, ProductCreate, ProductUpdate } from '@/types/menu';
import './ProductEditor.css';
import { notifications } from '@mantine/notifications';

interface ProductEditorProps {
  product: Product | null; // null = új termék, Product = szerkesztés
  categories: Category[];
  onClose: (shouldRefresh: boolean) => void;
}

export const ProductEditor = ({
  product,
  categories,
  onClose,
}: ProductEditorProps) => {
  const isEditing = !!product; // true = szerkesztés, false = új létrehozás
    
  // Form állapot
  const [formData, setFormData] = useState({
    name: product?.name || '',
    description: product?.description || '',
    base_price: product?.base_price || 0,
    category_id: product?.category_id || undefined,
    sku: product?.sku || '',
    is_active: product?.is_active ?? true,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form mező változás
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    // Checkbox kezelés
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    // Szám mező kezelés
    if (name === 'base_price') {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }));
      return;
    }

    // Category ID (opcionális)
    if (name === 'category_id') {
      setFormData((prev) => ({
        ...prev,
        [name]: value ? parseInt(value, 10) : undefined,
      }));
      return;
    }

    // String mezők
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Form submit (létrehozás / frissítés)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validáció
    if (!formData.name.trim()) {
      notifications.show({
        title: 'Figyelmeztetés',
        message: 'A termék neve kötelező!',
        color: 'yellow',
      });
      return;
    }

    if (formData.base_price < 0) {
      notifications.show({
        title: 'Figyelmeztetés',
        message: 'Az ár nem lehet negatív!',
        color: 'yellow',
      });
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditing && product) {
        // Frissítés
        const updateData: ProductUpdate = {
          name: formData.name,
          description: formData.description || undefined,
          base_price: formData.base_price,
          category_id: formData.category_id,
          sku: formData.sku || undefined,
          is_active: formData.is_active,
        };
        await updateProduct(product.id, updateData);
        notifications.show({
        title: 'Siker',
        message: 'Termék sikeresen frissítve!',
        color: 'green',
      });
      } else {
        // Létrehozás
        const createData: ProductCreate = {
          name: formData.name,
          description: formData.description || undefined,
          base_price: formData.base_price,
          category_id: formData.category_id,
          sku: formData.sku || undefined,
          is_active: formData.is_active,
        };
        await createProduct(createData);
        notifications.show({
        title: 'Siker',
        message: 'Termék sikeresen létrehozva!',
        color: 'green',
      });
      }

      onClose(true); // Bezárás + lista frissítése
    } catch (error: any) {
      console.error('Hiba a termék mentésekor:', error);
      const errorMessage =
        error.response?.data?.detail || 'Nem sikerült menteni a terméket!';
      notify.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Modal overlay kattintás (háttérre kattintva bezárás)
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <header className="modal-header">
          <h2>{isEditing ? '✏️ Termék szerkesztése' : '➕ Új termék'}</h2>
          <button onClick={() => onClose(false)} className="close-btn">
            ✕
          </button>
        </header>

        <form onSubmit={handleSubmit} className="product-form">
          {/* Név */}
          <div className="form-group">
            <label htmlFor="name">
              Név <span className="required">*</span>
            </label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="pl. Sajtos Hamburger"
              required
              maxLength={255}
            />
          </div>

          {/* Leírás */}
          <div className="form-group">
            <label htmlFor="description">Leírás</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Termék részletes leírása..."
              rows={3}
            />
          </div>

          {/* Alap ár */}
          <div className="form-group">
            <label htmlFor="base_price">
              Alap ár (HUF) <span className="required">*</span>
            </label>
            <input
              id="base_price"
              name="base_price"
              type="number"
              value={formData.base_price}
              onChange={handleChange}
              min={0}
              step={10}
              required
            />
          </div>

          {/* Kategória */}
          <div className="form-group">
            <label htmlFor="category_id">Kategória</label>
            <select
              id="category_id"
              name="category_id"
              value={formData.category_id || ''}
              onChange={handleChange}
            >
              <option value="">-- Nincs kategória --</option>
              {categories
                .filter((c) => c.is_active)
                .map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
            </select>
          </div>

          {/* SKU */}
          <div className="form-group">
            <label htmlFor="sku">SKU (Cikkszám)</label>
            <input
              id="sku"
              name="sku"
              type="text"
              value={formData.sku}
              onChange={handleChange}
              placeholder="pl. BURG-CHEESE-001"
              maxLength={100}
            />
          </div>

          {/* Aktív */}
          <div className="form-group checkbox-group">
            <label>
              <input
                name="is_active"
                type="checkbox"
                checked={formData.is_active}
                onChange={handleChange}
              />
              Aktív (elérhető értékesítésre)
            </label>
          </div>

          {/* Gombok */}
          <footer className="modal-footer">
            <button
              type="button"
              onClick={() => onClose(false)}
              className="cancel-btn"
              disabled={isSubmitting}
            >
              Mégse
            </button>
            <button type="submit" className="save-btn" disabled={isSubmitting}>
              {isSubmitting
                ? 'Mentés...'
                : isEditing
                ? '💾 Mentés'
                : '➕ Létrehozás'}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
};
