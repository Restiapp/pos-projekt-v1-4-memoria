/**
 * OrderPage - Rendelésfelvételi Képernyő
 * Task A10: Order Entry UI
 *
 * Funkciók:
 *   - Termékek megjelenítése kategóriák szerint
 *   - Tételek hozzáadása course (fogás) és notes (jegyzet) mezőkkel
 *   - Vendégszám kezelés
 *   - Vendégkeresés (CRM integráció)
 *   - Reszponzív design
 */

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { getCustomers } from '@/services/crmService';
import type { Customer } from '@/types/customer';
import './OrderPage.css';

// Fogások (courses) típusai
type CourseType = 'Előétel' | 'Főétel' | 'Desszert' | 'Ital' | 'Egyéb';

// Order item típus
interface OrderItem {
  id: string; // Egyedi azonosító a kosárban
  productId: number;
  productName: string;
  basePrice: number;
  quantity: number;
  course: CourseType;
  notes: string;
}

// Dummy Product típus
interface DummyProduct {
  id: number;
  name: string;
  description?: string;
  base_price: number;
  category_id: number;
}

// Dummy Category típus
interface DummyCategory {
  id: number;
  name: string;
  description?: string;
}

export const OrderPage = () => {
  // ========================================
  // ROUTE PARAMS - Asztal ID az URL-ből
  // ========================================
  const { tableId } = useParams<{ tableId: string }>();

  // ========================================
  // STATE - Vendég & Asztal
  // ========================================
  const [guestCount, setGuestCount] = useState<number>(2);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  // ========================================
  // STATE - Termékek & Kategóriák
  // ========================================
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);

  // ========================================
  // STATE - Kosár (Order Items)
  // ========================================
  const [orderItems, setOrderItems] = useState<OrderItem[]>([]);

  // ========================================
  // DUMMY DATA - Kategóriák
  // ========================================
  const dummyCategories: DummyCategory[] = [
    { id: 1, name: '🍕 Pizzák', description: 'Frissen sült pizzák' },
    { id: 2, name: '🍝 Tésztaételek', description: 'Házias tésztaételek' },
    { id: 3, name: '🥗 Saláták', description: 'Friss saláták' },
    { id: 4, name: '🍰 Desszertek', description: 'Édes finomságok' },
    { id: 5, name: '☕ Italok', description: 'Hideg és meleg italok' },
  ];

  // ========================================
  // DUMMY DATA - Termékek
  // ========================================
  const dummyProducts: DummyProduct[] = [
    // Pizzák (category_id: 1)
    { id: 1, name: 'Margherita', description: 'Paradicsom, mozzarella, bazsalikom', base_price: 2490, category_id: 1 },
    { id: 2, name: 'Prosciutto', description: 'Paradicsom, mozzarella, sonka', base_price: 2890, category_id: 1 },
    { id: 3, name: 'Quattro Formaggi', description: 'Négyféle sajt', base_price: 3190, category_id: 1 },
    { id: 4, name: 'Diavola', description: 'Paradicsom, mozzarella, csípős szalámi', base_price: 2990, category_id: 1 },

    // Tésztaételek (category_id: 2)
    { id: 5, name: 'Carbonara', description: 'Tojás, bacon, parmezán', base_price: 2690, category_id: 2 },
    { id: 6, name: 'Bolognai Spagetti', description: 'Darált marhahús raguval', base_price: 2590, category_id: 2 },
    { id: 7, name: 'Lasagne', description: 'Rétegelt tészta, darált hús, besamel', base_price: 2890, category_id: 2 },

    // Saláták (category_id: 3)
    { id: 8, name: 'Cézár Saláta', description: 'Csirke, jégsaláta, parmezán, kruton', base_price: 2190, category_id: 3 },
    { id: 9, name: 'Görög Saláta', description: 'Paradicsom, uborka, olívabogyó, feta', base_price: 1990, category_id: 3 },

    // Desszertek (category_id: 4)
    { id: 10, name: 'Tiramisu', description: 'Klasszikus olasz desszert', base_price: 1490, category_id: 4 },
    { id: 11, name: 'Panna Cotta', description: 'Tejszínes desszert erdei gyümölccsel', base_price: 1290, category_id: 4 },
    { id: 12, name: 'Lava Cake', description: 'Folyékony csokoládétorta', base_price: 1690, category_id: 4 },

    // Italok (category_id: 5)
    { id: 13, name: 'Cappuccino', description: 'Eszpresszó habos tejjel', base_price: 690, category_id: 5 },
    { id: 14, name: 'Limonádé', description: 'Házi készítésű citromos üdítő', base_price: 590, category_id: 5 },
    { id: 15, name: 'Coca-Cola (0.33L)', base_price: 490, category_id: 5 },
  ];

  // ========================================
  // COMPUTED - Szűrt termékek
  // ========================================
  const filteredProducts = selectedCategoryId
    ? dummyProducts.filter((p) => p.category_id === selectedCategoryId)
    : dummyProducts;

  // ========================================
  // COMPUTED - Rendelés összegzés
  // ========================================
  const subtotal = orderItems.reduce((sum, item) => sum + item.basePrice * item.quantity, 0);
  const vatRate = 0.27; // 27% ÁFA
  const vatAmount = subtotal * vatRate;
  const total = subtotal + vatAmount;

  // ========================================
  // HANDLERS - Vendégkeresés
  // ========================================
  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      alert('Kérlek adj meg keresési kifejezést!');
      return;
    }

    try {
      setIsSearching(true);
      const response = await getCustomers(1, 10, undefined, searchTerm);
      setSearchResults(response.items);
      if (response.items.length === 0) {
        alert('Nem található vendég ezzel a keresési kifejezéssel.');
      }
    } catch (error) {
      console.error('Hiba a vendég keresésekor:', error);
      alert('Nem sikerült megtalálni a vendéget!');
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setSearchResults([]);
    setSearchTerm('');
  };

  // ========================================
  // HANDLERS - Termék hozzáadása
  // ========================================
  const handleAddProduct = (product: DummyProduct) => {
    const newItem: OrderItem = {
      id: `${product.id}-${Date.now()}`, // Egyedi ID
      productId: product.id,
      productName: product.name,
      basePrice: product.base_price,
      quantity: 1,
      course: 'Főétel', // Alapértelmezett
      notes: '',
    };
    setOrderItems([...orderItems, newItem]);
  };

  // ========================================
  // HANDLERS - Tétel módosítása
  // ========================================
  const handleUpdateItemCourse = (itemId: string, course: CourseType) => {
    setOrderItems(orderItems.map((item) =>
      item.id === itemId ? { ...item, course } : item
    ));
  };

  const handleUpdateItemNotes = (itemId: string, notes: string) => {
    setOrderItems(orderItems.map((item) =>
      item.id === itemId ? { ...item, notes } : item
    ));
  };

  const handleUpdateItemQuantity = (itemId: string, quantity: number) => {
    if (quantity < 1) return;
    setOrderItems(orderItems.map((item) =>
      item.id === itemId ? { ...item, quantity } : item
    ));
  };

  const handleRemoveItem = (itemId: string) => {
    setOrderItems(orderItems.filter((item) => item.id !== itemId));
  };

  // ========================================
  // HANDLERS - Rendelés mentése
  // ========================================
  const handleSaveOrder = () => {
    if (orderItems.length === 0) {
      alert('Nincs tétel a rendelésben!');
      return;
    }

    // TODO: API hívás a rendelés mentéséhez
    alert(
      `RENDELÉS MENTVE!\n\n` +
      `Asztal: #${tableId}\n` +
      `Vendégek száma: ${guestCount}\n` +
      `Tételek: ${orderItems.length}\n` +
      `Végösszeg: ${formatPrice(total)}\n\n` +
      `(API integráció később - V4.0)`
    );
  };

  // ========================================
  // UTILS - Ár formázás
  // ========================================
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="order-page">
      {/* Globális navigációs header */}
      <GlobalHeader currentPage="tables" />

      <div className="order-container">
        {/* ====================================== */}
        {/* BAL PANEL: Asztal & Vendég Info */}
        {/* ====================================== */}
        <aside className="order-sidebar left-sidebar">
          <section className="sidebar-section">
            <h2>🍽️ Asztal Információ</h2>
            <div className="table-info-card">
              <div className="info-row">
                <span className="info-label">Asztal:</span>
                <span className="info-value">#{tableId || 'N/A'}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Vendégek:</span>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={guestCount}
                  onChange={(e) => setGuestCount(Number(e.target.value))}
                  className="guest-count-input"
                />
              </div>
            </div>
          </section>

          <section className="sidebar-section">
            <h2>👤 Vendég Keresése (CRM)</h2>
            <div className="search-box">
              <input
                type="text"
                placeholder="Név, email vagy telefon..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="search-input"
              />
              <button
                onClick={handleSearch}
                disabled={isSearching}
                className="search-btn"
              >
                {isSearching ? '⏳' : '🔍'}
              </button>
            </div>

            {/* Keresési eredmények */}
            {searchResults.length > 0 && (
              <div className="search-results">
                <h4>Találatok ({searchResults.length}):</h4>
                {searchResults.map((customer) => (
                  <div
                    key={customer.id}
                    className="search-result-item"
                    onClick={() => handleSelectCustomer(customer)}
                  >
                    <strong>{customer.first_name} {customer.last_name}</strong>
                    <span className="customer-contact">
                      {customer.phone || customer.email}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Kiválasztott vendég */}
            {selectedCustomer && (
              <div className="selected-customer-card">
                <h4>Kiválasztott vendég:</h4>
                <div className="customer-details">
                  <p><strong>{selectedCustomer.first_name} {selectedCustomer.last_name}</strong></p>
                  <p>📧 {selectedCustomer.email}</p>
                  <p>📱 {selectedCustomer.phone || 'N/A'}</p>
                  <p>🎯 {selectedCustomer.loyalty_points} pont</p>
                </div>
                <button
                  onClick={() => setSelectedCustomer(null)}
                  className="deselect-btn"
                >
                  ✕ Törlés
                </button>
              </div>
            )}
          </section>
        </aside>

        {/* ====================================== */}
        {/* KÖZÉPSŐ PANEL: Termékek */}
        {/* ====================================== */}
        <main className="order-main">
          <section className="products-section">
            <h2>📋 Menü</h2>

            {/* Kategória szűrők */}
            <div className="category-filters">
              <button
                className={`category-btn ${selectedCategoryId === null ? 'active' : ''}`}
                onClick={() => setSelectedCategoryId(null)}
              >
                Összes
              </button>
              {dummyCategories.map((cat) => (
                <button
                  key={cat.id}
                  className={`category-btn ${selectedCategoryId === cat.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategoryId(cat.id)}
                >
                  {cat.name}
                </button>
              ))}
            </div>

            {/* Termékek Grid */}
            <div className="products-grid">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  className="product-card"
                  onClick={() => handleAddProduct(product)}
                >
                  <h3 className="product-name">{product.name}</h3>
                  {product.description && (
                    <p className="product-description">{product.description}</p>
                  )}
                  <div className="product-footer">
                    <span className="product-price">{formatPrice(product.base_price)}</span>
                    <button className="add-btn">+</button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </main>

        {/* ====================================== */}
        {/* JOBB PANEL: Kosár & Összegzés */}
        {/* ====================================== */}
        <aside className="order-sidebar right-sidebar">
          <section className="sidebar-section">
            <h2>🛒 Rendelés ({orderItems.length} tétel)</h2>

            {orderItems.length === 0 ? (
              <p className="empty-cart-message">
                Nincs még tétel a rendelésben.<br />
                Kattints egy termékre a hozzáadáshoz!
              </p>
            ) : (
              <>
                <div className="order-items-list">
                  {orderItems.map((item) => (
                    <div key={item.id} className="order-item-card">
                      <div className="item-header">
                        <span className="item-name">{item.productName}</span>
                        <button
                          onClick={() => handleRemoveItem(item.id)}
                          className="remove-item-btn"
                        >
                          ✕
                        </button>
                      </div>

                      <div className="item-controls">
                        {/* Mennyiség */}
                        <div className="quantity-control">
                          <button
                            onClick={() => handleUpdateItemQuantity(item.id, item.quantity - 1)}
                            className="qty-btn"
                          >
                            −
                          </button>
                          <span className="qty-value">{item.quantity}</span>
                          <button
                            onClick={() => handleUpdateItemQuantity(item.id, item.quantity + 1)}
                            className="qty-btn"
                          >
                            +
                          </button>
                        </div>

                        {/* Ár */}
                        <span className="item-price">
                          {formatPrice(item.basePrice * item.quantity)}
                        </span>
                      </div>

                      {/* Fogás (Course) */}
                      <div className="item-field">
                        <label>Fogás:</label>
                        <select
                          value={item.course}
                          onChange={(e) => handleUpdateItemCourse(item.id, e.target.value as CourseType)}
                          className="course-select"
                        >
                          <option value="Előétel">Előétel</option>
                          <option value="Főétel">Főétel</option>
                          <option value="Desszert">Desszert</option>
                          <option value="Ital">Ital</option>
                          <option value="Egyéb">Egyéb</option>
                        </select>
                      </div>

                      {/* Jegyzet (Notes) */}
                      <div className="item-field">
                        <label>Megjegyzés:</label>
                        <input
                          type="text"
                          placeholder="pl. extra fűszeres, gluténmentes..."
                          value={item.notes}
                          onChange={(e) => handleUpdateItemNotes(item.id, e.target.value)}
                          className="notes-input"
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Összegzés */}
                <div className="order-summary">
                  <div className="summary-row">
                    <span>Részösszeg:</span>
                    <span>{formatPrice(subtotal)}</span>
                  </div>
                  <div className="summary-row">
                    <span>ÁFA (27%):</span>
                    <span>{formatPrice(vatAmount)}</span>
                  </div>
                  <div className="summary-row total-row">
                    <span>Végösszeg:</span>
                    <span>{formatPrice(total)}</span>
                  </div>
                </div>

                {/* Akciógombok */}
                <div className="order-actions">
                  <button
                    onClick={handleSaveOrder}
                    className="save-order-btn"
                  >
                    💾 Rendelés Mentése
                  </button>
                  <button
                    onClick={() => setOrderItems([])}
                    className="clear-order-btn"
                  >
                    🗑️ Kosár Ürítése
                  </button>
                </div>
              </>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
};
