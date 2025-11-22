/**
 * QuickOrderButton - Fast Bar Order Component
 *
 * Features:
 * - Quick button to open modal for bar orders
 * - Product/drink selector
 * - Quantity selector
 * - Optional note field
 * - Creates order via POST /api/orders and adds item
 * - Success/Error toast notifications
 *
 * Usage:
 *   <QuickOrderButton />
 */

import { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { useToast } from '@/hooks/useToast';
import { getProducts } from '@/services/menuService';
import { createOrder } from '@/services/orderService';
import { addItemToOrder } from '@/services/orderService';
import type { Product } from '@/types/menu';
import type { OrderCreate } from '@/types/order';
import './QuickOrderButton.css';

interface OrderItemCreate {
  order_id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  notes?: string;
  kds_station?: string;
}

export const QuickOrderButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [note, setNote] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const toast = useToast();

  // Load products when modal opens
  useEffect(() => {
    if (isModalOpen) {
      loadProducts();
    }
  }, [isModalOpen]);

  const loadProducts = async () => {
    try {
      setIsLoading(true);
      const response = await getProducts(1, 100, true); // Get active products
      setProducts(response.items);
    } catch (error) {
      console.error('Error loading products:', error);
      toast.error('Hiba a termékek betöltésekor');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    // Reset form
    setSelectedProductId(null);
    setQuantity(1);
    setNote('');
  };

  const handleSubmit = async () => {
    if (!selectedProductId) {
      toast.error('Kérlek válassz egy terméket!');
      return;
    }

    const selectedProduct = products.find(p => p.id === selectedProductId);
    if (!selectedProduct) {
      toast.error('A kiválasztott termék nem található!');
      return;
    }

    try {
      setIsSubmitting(true);

      // Step 1: Create order
      const orderData: OrderCreate = {
        order_type: 'Elvitel', // Bar orders are typically takeout
        status: 'NYITOTT',
        notes: note || undefined,
      };

      const newOrder = await createOrder(orderData);

      // Step 2: Add item to order
      const itemData: OrderItemCreate = {
        order_id: newOrder.id,
        product_id: selectedProduct.id,
        quantity: quantity,
        unit_price: selectedProduct.base_price,
        notes: note || undefined,
        kds_station: 'BAR',
      };

      await addItemToOrder(newOrder.id, itemData);

      // Success!
      toast.success(`Rendelés sikeresen létrehozva! (Rendelés #${newOrder.id})`);
      handleCloseModal();
    } catch (error: any) {
      console.error('Error creating order:', error);
      const errorMessage = error.response?.data?.detail || 'Hiba a rendelés létrehozásakor';
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedProduct = products.find(p => p.id === selectedProductId);

  return (
    <>
      {/* Quick Order Button */}
      <button className="quick-order-button" onClick={handleOpenModal}>
        + Gyors Rendelés
      </button>

      {/* Quick Order Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title="Gyors Rendelés - Bar"
        maxWidth="500px"
      >
        <div className="quick-order-modal">
          {isLoading ? (
            <div className="loading-state">
              <p>Betöltés...</p>
            </div>
          ) : (
            <>
              {/* Product Selector */}
              <div className="form-group">
                <label htmlFor="product-select">Termék / Ital</label>
                <select
                  id="product-select"
                  value={selectedProductId || ''}
                  onChange={(e) => setSelectedProductId(Number(e.target.value) || null)}
                  className="product-select"
                  disabled={isSubmitting}
                >
                  <option value="">-- Válassz terméket --</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name} - {formatPrice(product.base_price)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Selected Product Info */}
              {selectedProduct && (
                <div className="product-info">
                  {selectedProduct.description && (
                    <p className="product-description">{selectedProduct.description}</p>
                  )}
                </div>
              )}

              {/* Quantity Selector */}
              <div className="form-group">
                <label>Mennyiség</label>
                <div className="quantity-control">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="qty-btn"
                    disabled={quantity <= 1 || isSubmitting}
                    type="button"
                  >
                    −
                  </button>
                  <span className="quantity-display">{quantity}</span>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="qty-btn"
                    disabled={isSubmitting}
                    type="button"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Notes */}
              <div className="form-group">
                <label htmlFor="notes">Megjegyzés (opcionális)</label>
                <textarea
                  id="notes"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="pl. 'Extra jég', 'Kevés cukor'..."
                  className="notes-textarea"
                  rows={3}
                  disabled={isSubmitting}
                />
              </div>

              {/* Price Summary */}
              {selectedProduct && (
                <div className="price-summary">
                  <div className="price-row">
                    <span>Egységár:</span>
                    <span className="price">{formatPrice(selectedProduct.base_price)}</span>
                  </div>
                  {quantity > 1 && (
                    <div className="price-row total">
                      <span>Összesen ({quantity} db):</span>
                      <span className="price">
                        {formatPrice(selectedProduct.base_price * quantity)}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Submit Button */}
              <button
                onClick={handleSubmit}
                disabled={!selectedProductId || isSubmitting}
                className="submit-btn"
              >
                {isSubmitting ? 'Rendelés küldése...' : 'Rendelés leadása'}
              </button>
            </>
          )}
        </div>
      </Modal>
    </>
  );
};

/**
 * Format price in HUF currency
 */
function formatPrice(price: number): string {
  return new Intl.NumberFormat('hu-HU', {
    style: 'currency',
    currency: 'HUF',
    minimumFractionDigits: 0,
  }).format(price);
}
