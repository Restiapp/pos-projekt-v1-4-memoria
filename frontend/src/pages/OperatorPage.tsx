/**
 * OperatorPage - Telefonos Rendelésfelvételi Felület
 * V4.0: Product Builder Modal Integration
 *
 * Funkciók:
 *   - Vendégkeresés (név, telefonszám alapján)
 *   - Termékválasztás Product Grid-el
 *   - Product Builder Modal (modifiers, course, notes)
 *   - Kosár kezelés
 *   - Zóna ellenőrzés irányítószám alapján
 */

import { useState } from 'react';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { ProductGrid } from '@/components/operator/ProductGrid';
import { CartSummary } from '@/components/operator/CartSummary';
import type { CartItem } from '@/components/operator/ProductBuilderModal';
import { getCustomers } from '@/services/crmService';
import { getZoneByZipCode } from '@/services/logisticsService';
import type { Customer } from '@/types/customer';
import type { DeliveryZone } from '@/types/logistics';
import { useToast } from '@/components/common/Toast';
import './OperatorPage.css';

export const OperatorPage = () => {
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  // Zóna ellenőrzés
  const [zipCode, setZipCode] = useState('');
  const [deliveryZone, setDeliveryZone] = useState<DeliveryZone | null>(null);
  const [zoneMessage, setZoneMessage] = useState('');

  // Cart state
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [showProducts, setShowProducts] = useState(false);

  // Vendég keresés
  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      showToast('Kérlek adj meg keresési kifejezést (név, email, telefon)!', 'error');
      return;
    }

    try {
      setIsSearching(true);
      const response = await getCustomers(1, 10, undefined, searchTerm);
      setSearchResults(response.items);
      if (response.items.length === 0) {
        showToast('Nem található vendég ezzel a keresési kifejezéssel.', 'info');
      }
    } catch (error) {
      console.error('Hiba a vendég keresésekor:', error);
      showToast('Nem sikerült megtalálni a vendéget!', 'error');
    } finally {
      setIsSearching(false);
    }
  };

  // Vendég kiválasztása
  const handleSelectCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setSearchResults([]);
    setSearchTerm('');
  };

  // Zóna ellenőrzés irányítószám alapján
  const handleCheckZone = async () => {
    if (!zipCode.trim()) {
      showToast('Kérlek adj meg irányítószámot!', 'error');
      return;
    }

    try {
      const response = await getZoneByZipCode(zipCode);
      setDeliveryZone(response.zone);
      setZoneMessage(response.message);
    } catch (error) {
      console.error('Hiba a zóna ellenőrzésekor:', error);
      showToast('Nem sikerült ellenőrizni a zónát!', 'error');
    }
  };

  // Új rendelés indítása
  const handleStartNewOrder = () => {
    if (!selectedCustomer) {
      showToast('Először válassz ki egy vendéget!', 'error');
      return;
    }
<<<<<<< HEAD
    setShowProducts(true);
  };

  // Cart handlers
  const handleAddToCart = (item: CartItem) => {
    setCartItems([...cartItems, item]);
  };

  const handleUpdateQuantity = (index: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    const updatedItems = [...cartItems];
    updatedItems[index].quantity = newQuantity;
    setCartItems(updatedItems);
  };

  const handleRemoveItem = (index: number) => {
    const updatedItems = cartItems.filter((_, i) => i !== index);
    setCartItems(updatedItems);
  };

  const handleClearCart = () => {
    if (confirm('Biztosan törölni szeretnéd a kosár tartalmát?')) {
      setCartItems([]);
    }
  };

  const handleCheckout = () => {
    if (cartItems.length === 0) {
      alert('A kosár üres!');
      return;
    }
    if (!selectedCustomer) {
      alert('Nincs kiválasztott vendég!');
      return;
    }

    // TODO: Implement order creation
    alert(
      `RENDELÉS LEADÁSA\n\nVendég: ${selectedCustomer.first_name} ${selectedCustomer.last_name}\nTételek száma: ${cartItems.length}\n\n(Rendelés létrehozása következik...)`
=======
    showToast(
      `ÚJ KISZÁLLÍTÁSI RENDELÉS\n\nVendég: ${selectedCustomer.first_name} ${selectedCustomer.last_name}\n\n(Ez még placeholder funkció - V4.0-ban lesz teljes rendelésfelvétel)`,
      'info'
>>>>>>> origin/claude/remove-alert-confirm-calls-01C1xe4YBUCvTLwxWG8qCNJE
    );
  };

  // Ár formázása
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('hu-HU', {
      style: 'currency',
      currency: 'HUF',
      minimumFractionDigits: 0,
    }).format(price);
  };

  // If products are shown, display the product builder interface
  if (showProducts) {
    return (
      <div className="operator-page">
        <GlobalHeader currentPage="operator" />

        <div className="operator-product-layout">
          {/* Product Grid */}
          <div className="product-grid-panel">
            <div className="panel-header">
              <h2>🍽️ Termékválasztás</h2>
              <button
                className="back-btn"
                onClick={() => setShowProducts(false)}
              >
                ← Vissza
              </button>
            </div>
            <ProductGrid onAddToCart={handleAddToCart} />
          </div>

          {/* Cart Summary */}
          <div className="cart-panel">
            <CartSummary
              cartItems={cartItems}
              onUpdateQuantity={handleUpdateQuantity}
              onRemoveItem={handleRemoveItem}
              onClearCart={handleClearCart}
              onCheckout={handleCheckout}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="operator-page">
      {/* Globális navigációs header */}
      <GlobalHeader currentPage="operator" />

      <div className="operator-container">
        {/* BAL PANEL: Vendégkeresés */}
        <section className="operator-section customer-search-section">
          <h2>👤 Vendég keresése</h2>

          <div className="search-box">
            <input
              type="text"
              placeholder="Név, email vagy telefonszám..."
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
              {isSearching ? '⏳ Keresés...' : '🔍 Keresés'}
            </button>
          </div>

          {/* Keresési eredmények */}
          {searchResults.length > 0 && (
            <div className="search-results">
              <h3>Találatok ({searchResults.length}):</h3>
              {searchResults.map((customer) => (
                <div
                  key={customer.id}
                  className="search-result-item"
                  onClick={() => handleSelectCustomer(customer)}
                >
                  <strong>
                    {customer.first_name} {customer.last_name}
                  </strong>
                  <span className="customer-contact">
                    {customer.email} | {customer.phone || 'Nincs telefon'}
                  </span>
                  <span className="customer-uid">{customer.customer_uid}</span>
                </div>
              ))}
            </div>
          )}

          {/* Kiválasztott vendég */}
          {selectedCustomer && (
            <div className="selected-customer">
              <h3>Kiválasztott vendég:</h3>
              <div className="customer-card">
                <div className="customer-info">
                  <h4>
                    {selectedCustomer.first_name} {selectedCustomer.last_name}
                  </h4>
                  <p>📧 {selectedCustomer.email}</p>
                  <p>📱 {selectedCustomer.phone || 'Nincs telefon'}</p>
                  <p>🏷️ {selectedCustomer.customer_uid}</p>
                </div>
                <div className="customer-stats">
                  <span>🎯 {selectedCustomer.loyalty_points} hűségpont</span>
                  <span>💰 {formatPrice(selectedCustomer.total_spent)} össz. költés</span>
                  <span>🛒 {selectedCustomer.total_orders} rendelés</span>
                </div>
                <button
                  onClick={() => setSelectedCustomer(null)}
                  className="deselect-btn"
                >
                  ❌ Törlés
                </button>
              </div>
            </div>
          )}
        </section>

        {/* JOBB PANEL: Zóna ellenőrzés és Rendelésfelvétel */}
        <section className="operator-section order-section">
          <h2>🚚 Kiszállítási Zóna Ellenőrzése</h2>

          <div className="zone-check-box">
            <input
              type="text"
              placeholder="Irányítószám (pl. 1051)..."
              value={zipCode}
              onChange={(e) => setZipCode(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCheckZone()}
              className="zip-input"
            />
            <button onClick={handleCheckZone} className="check-btn">
              🔍 Zóna Ellenőrzése
            </button>
          </div>

          {/* Zóna eredmény */}
          {zoneMessage && (
            <div className={`zone-result ${deliveryZone ? 'success' : 'error'}`}>
              <p>{zoneMessage}</p>
              {deliveryZone && (
                <div className="zone-details">
                  <h4>📍 {deliveryZone.zone_name}</h4>
                  <p>{deliveryZone.description}</p>
                  <div className="zone-info">
                    <span>💵 Kiszállítási díj: {formatPrice(deliveryZone.delivery_fee)}</span>
                    <span>
                      📦 Min. rendelés: {formatPrice(deliveryZone.min_order_value)}
                    </span>
                    <span>⏱️ Idő: ~{deliveryZone.estimated_delivery_time_minutes} perc</span>
                  </div>
                </div>
              )}
            </div>
          )}

          <hr />

          <h2>🛒 Új Rendelés</h2>
          <button
            onClick={handleStartNewOrder}
            disabled={!selectedCustomer}
            className="new-order-btn"
          >
            ➕ Új Kiszállítási Rendelés
          </button>

          {!selectedCustomer && (
            <p className="hint-text">
              ℹ️ Először válassz ki egy vendéget a bal oldalon!
            </p>
          )}
        </section>
      </div>
    </div>
  );
};
