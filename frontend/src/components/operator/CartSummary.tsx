/**
 * CartSummary - Shopping Cart Display for Operator Page
 *
 * Features:
 * - Display cart items with modifiers
 * - Show course and notes
 * - Quantity adjustment
 * - Remove items
 * - Total calculation
 */

import type { CartItem } from './ProductBuilderModal';
import './CartSummary.css';

interface CartSummaryProps {
  cartItems: CartItem[];
  onUpdateQuantity: (index: number, newQuantity: number) => void;
  onRemoveItem: (index: number) => void;
  onClearCart: () => void;
  onCheckout: () => void;
}

export const CartSummary = ({
  cartItems,
  onUpdateQuantity,
  onRemoveItem,
  onClearCart,
  onCheckout,
}: CartSummaryProps) => {
  // Calculate total
  const calculateTotal = (): number => {
    return cartItems.reduce((sum, item) => sum + item.unit_price * item.quantity, 0);
  };

  // Format price
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const total = calculateTotal();
  const isEmpty = cartItems.length === 0;

  return (
    <div className="cart-summary">
      <div className="cart-header">
        <h2>🛒 Kosár</h2>
        {!isEmpty && (
          <button className="clear-cart-btn" onClick={onClearCart}>
            Ürítés
          </button>
        )}
      </div>

      <div className="cart-items">
        {isEmpty ? (
          <div className="empty-cart">
            <p>A kosár üres</p>
            <p className="hint">Válassz terméket az oldalsó menüből!</p>
          </div>
        ) : (
          cartItems.map((item, index) => (
            <div key={index} className="cart-item">
              <div className="item-header">
                <h4 className="item-name">{item.product.name}</h4>
                <button
                  className="remove-item-btn"
                  onClick={() => onRemoveItem(index)}
                  title="Törlés"
                >
                  ✕
                </button>
              </div>

              {/* Modifiers */}
              {item.selected_modifiers && item.selected_modifiers.length > 0 && (
                <div className="item-modifiers">
                  {item.selected_modifiers.map((modifier, idx) => (
                    <div key={idx} className="modifier-item">
                      <span className="modifier-label">
                        • {modifier.modifier_name}
                      </span>
                      {modifier.price !== 0 && (
                        <span className="modifier-price-small">
                          {modifier.price > 0 ? '+' : ''}
                          {formatPrice(modifier.price)}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Course */}
              {item.course && (
                <div className="item-meta">
                  <span className="meta-label">Fogás:</span>
                  <span className="meta-value">{item.course}</span>
                </div>
              )}

              {/* Notes */}
              {item.notes && (
                <div className="item-notes">
                  <span className="notes-icon">📝</span>
                  <span className="notes-text">{item.notes}</span>
                </div>
              )}

              {/* Price and Quantity */}
              <div className="item-footer">
                <div className="quantity-control">
                  <button
                    className="qty-btn"
                    onClick={() => onUpdateQuantity(index, item.quantity - 1)}
                    disabled={item.quantity <= 1}
                  >
                    −
                  </button>
                  <span className="quantity">{item.quantity}</span>
                  <button
                    className="qty-btn"
                    onClick={() => onUpdateQuantity(index, item.quantity + 1)}
                  >
                    +
                  </button>
                </div>
                <div className="item-total">
                  {formatPrice(item.unit_price * item.quantity)}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Cart Footer */}
      {!isEmpty && (
        <div className="cart-footer">
          <div className="total-row">
            <span className="total-label">Összesen:</span>
            <span className="total-amount">{formatPrice(total)}</span>
          </div>
          <button className="checkout-btn" onClick={onCheckout}>
            Rendelés leadása
          </button>
        </div>
      )}
    </div>
  );
};
