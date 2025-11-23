// TODO-S0-STUB: TypeScript checking disabled - fix dependency issues
// @ts-nocheck
/**
 * OrderPage - Rendelésfelvétel oldal
 *
 * Funkciók:
 *   - Termékek böngészése kategóriák szerint
 *   - Kosár kezelése (hozzáadás, törlés, mennyiség módosítás)
 *   - Rendelés leadása (POST /api/orders + POST /api/orders/{id}/items)
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { getProducts, getCategories } from '@/services/menuService';
import { createOrder, addItemToOrder } from '@/services/orderService';
import { ItemFlags } from '@/components/order/ItemFlags';
import type { Product, Category } from '@/types/menu';
import type { CartItem, OrderTypeEnum, OrderStatusEnum } from '@/types/order';
import './OrderPage.css';

export const OrderPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const tableIdParam = searchParams.get('table_id');

  // State
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Order details
  const [tableId, setTableId] = useState<number>(tableIdParam ? parseInt(tableIdParam) : 1);
  const [orderType, setOrderType] = useState<string>('Helyben');

  // Load categories and products
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);

        // Load categories
        const categoriesResponse = await getCategories(1, 100, true);
        setCategories(categoriesResponse.items);

        // Load all active products
        const productsResponse = await getProducts(1, 100, true);
        setProducts(productsResponse.items);
      } catch (error) {
        console.error('Hiba az adatok betöltésekor:', error);
        alert('Nem sikerült betölteni a termékeket!');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter products by selected category
  const filteredProducts = selectedCategory
    ? products.filter((p) => p.category_id === selectedCategory)
    : products;

  // Add product to cart
  const addToCart = (product: Product) => {
    const existingItem = cart.find((item) => item.product_id === product.id);

    if (existingItem) {
      // Increment quantity
      setCart(
        cart.map((item) =>
          item.product_id === product.id
            ? {
                ...item,
                quantity: item.quantity + 1,
                total_price: (item.quantity + 1) * item.unit_price,
              }
            : item
        )
      );
    } else {
      // Add new item
      setCart([
        ...cart,
        {
          product_id: product.id,
          product_name: product.name,
          quantity: 1,
          unit_price: product.base_price,
          total_price: product.base_price,
          is_urgent: false,
          metadata: {},
        },
      ]);
    }
  };

  // Update urgent flag for cart item
  const updateUrgent = (productId: number, isUrgent: boolean) => {
    setCart(
      cart.map((item) =>
        item.product_id === productId
          ? { ...item, is_urgent: isUrgent }
          : item
      )
    );
  };

  // Update sync flag for cart item
  const updateSync = (productId: number, syncWith: string | undefined) => {
    setCart(
      cart.map((item) =>
        item.product_id === productId
          ? {
              ...item,
              metadata: {
                ...item.metadata,
                sync_with_course: syncWith,
              },
            }
          : item
      )
    );
  };

  // Remove product from cart
  const removeFromCart = (productId: number) => {
    setCart(cart.filter((item) => item.product_id !== productId));
  };

  // Update quantity in cart
  const updateQuantity = (productId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }

    setCart(
      cart.map((item) =>
        item.product_id === productId
          ? {
              ...item,
              quantity: newQuantity,
              total_price: newQuantity * item.unit_price,
            }
          : item
      )
    );
  };

  // Calculate total
  const calculateTotal = (): number => {
    return cart.reduce((sum, item) => sum + item.total_price, 0);
  };

  // Submit order
  const handleSubmitOrder = async () => {
    if (cart.length === 0) {
      alert('A kosár üres! Adj hozzá legalább egy terméket.');
      return;
    }

    try {
      setIsSubmitting(true);

      // Step 1: Create order
      const orderData = {
        order_type: orderType as any,
        status: 'NYITOTT' as any,
        table_id: tableId,
        total_amount: calculateTotal(),
        final_vat_rate: 27.0,
      };

      console.log('Creating order:', orderData);
      const createdOrder = await createOrder(orderData);
      console.log('Order created:', createdOrder);

      // Step 2: Add items to order
      for (const cartItem of cart) {
        const itemData = {
          order_id: createdOrder.id,
          product_id: cartItem.product_id,
          quantity: cartItem.quantity,
          unit_price: cartItem.unit_price,
          kds_status: 'VÁRAKOZIK',
          is_urgent: cartItem.is_urgent || false,
          // TODO: metadata not sent yet - backend needs metadata_json field support
          // metadata: cartItem.metadata || {},
        };

        console.log('Adding item to order:', itemData);
        await addItemToOrder(createdOrder.id, itemData);
      }

      alert(`Rendelés sikeresen leadva! Rendelésszám: #${createdOrder.id}`);

      // Clear cart
      setCart([]);

      // Navigate to table map or order details
      navigate('/tables');
    } catch (error: any) {
      console.error('Hiba a rendelés leadásakor:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Ismeretlen hiba';
      alert(`Nem sikerült leadni a rendelést!\n\n${errorMessage}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Format price
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="order-page">
      <GlobalHeader currentPage="orders" />

      <main className="page-content">
        <div className="order-container">
          {/* Left panel: Product Browser */}
          <div className="product-browser">
            <header className="browser-header">
              <h2>Termékek</h2>
              <div className="order-info">
                <label>
                  Rendelés típusa:
                  <select
                    value={orderType}
                    onChange={(e) => setOrderType(e.target.value)}
                    className="order-type-select"
                  >
                    <option value="Helyben">Helyben</option>
                    <option value="Elvitel">Elvitel</option>
                    <option value="Kiszállítás">Kiszállítás</option>
                  </select>
                </label>
                <label>
                  Asztal:
                  <input
                    type="number"
                    value={tableId}
                    onChange={(e) => setTableId(parseInt(e.target.value) || 1)}
                    min="1"
                    className="table-id-input"
                  />
                </label>
              </div>
            </header>

            {/* Category Filter */}
            <div className="category-filter">
              <button
                className={`category-btn ${selectedCategory === null ? 'active' : ''}`}
                onClick={() => setSelectedCategory(null)}
              >
                Összes
              </button>
              {categories.map((category) => (
                <button
                  key={category.id}
                  className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category.id)}
                >
                  {category.name}
                </button>
              ))}
            </div>

            {/* Product Grid */}
            {isLoading ? (
              <div className="loading-state">Betöltés...</div>
            ) : (
              <div className="product-grid">
                {filteredProducts.length === 0 ? (
                  <div className="empty-state">Nincsenek termékek ebben a kategóriában</div>
                ) : (
                  filteredProducts.map((product) => (
                    <div
                      key={product.id}
                      className="product-card"
                      onClick={() => addToCart(product)}
                    >
                      <div className="product-name">{product.name}</div>
                      {product.description && (
                        <div className="product-description">{product.description}</div>
                      )}
                      <div className="product-price">{formatPrice(product.base_price)}</div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Right panel: Cart */}
          <div className="cart-panel">
            <header className="cart-header">
              <h2>Kosár</h2>
              {cart.length > 0 && (
                <button
                  onClick={() => setCart([])}
                  className="clear-cart-btn"
                  title="Kosár ürítése"
                >
                  🗑️ Kosár ürítése
                </button>
              )}
            </header>

            <div className="cart-items">
              {cart.length === 0 ? (
                <div className="empty-cart">
                  <p>A kosár üres</p>
                  <p className="empty-cart-hint">Kattints egy termékre a hozzáadáshoz</p>
                </div>
              ) : (
                cart.map((item) => (
                  <div
                    key={item.product_id}
                    className={`cart-item ${item.is_urgent ? 'urgent' : ''} ${
                      item.metadata?.sync_with_course ? 'synced' : ''
                    }`}
                  >
                    <div className="cart-item-info">
                      <div className="cart-item-name">{item.product_name}</div>
                      <div className="cart-item-price">
                        {formatPrice(item.unit_price)} × {item.quantity} = {formatPrice(item.total_price)}
                      </div>
                      {/* Visual indicator badges */}
                      {(item.is_urgent || item.metadata?.sync_with_course) && (
                        <div className="item-indicators">
                          {item.is_urgent && (
                            <span className="indicator-badge urgent">⚡ Sürgős</span>
                          )}
                          {item.metadata?.sync_with_course && (
                            <span className="indicator-badge synced">
                              {item.metadata.sync_with_course === 'starter' && '🥗 Előételhez'}
                              {item.metadata.sync_with_course === 'main' && '🍽️ Főételhez'}
                              {item.metadata.sync_with_course === 'dessert' && '🍰 Desszerthez'}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="cart-item-controls">
                      {/* Item flags (urgent + sync) */}
                      <ItemFlags
                        isUrgent={item.is_urgent || false}
                        syncWith={item.metadata?.sync_with_course}
                        onUrgentChange={(value) => updateUrgent(item.product_id, value)}
                        onSyncChange={(value) => updateSync(item.product_id, value)}
                      />
                      {/* Quantity controls */}
                      <button
                        onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                        className="qty-btn"
                        title="Csökkentés"
                      >
                        −
                      </button>
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) =>
                          updateQuantity(item.product_id, parseInt(e.target.value) || 1)
                        }
                        min="1"
                        className="qty-input"
                      />
                      <button
                        onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                        className="qty-btn"
                        title="Növelés"
                      >
                        +
                      </button>
                      <button
                        onClick={() => removeFromCart(item.product_id)}
                        className="remove-btn"
                        title="Törlés"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Cart Footer */}
            {cart.length > 0 && (
              <footer className="cart-footer">
                <div className="cart-total">
                  <span className="total-label">Összesen:</span>
                  <span className="total-amount">{formatPrice(calculateTotal())}</span>
                </div>
                <button
                  onClick={handleSubmitOrder}
                  disabled={isSubmitting}
                  className="submit-order-btn"
                >
                  {isSubmitting ? 'Leadás...' : '✓ Rendelés leadása'}
                </button>
              </footer>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};
