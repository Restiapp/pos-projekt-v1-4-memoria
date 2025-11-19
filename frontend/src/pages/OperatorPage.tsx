/**
 * OperatorPage - Telefonos Rendelésfelvételi Felület
 * V3.0 Fázis 5: GlobalHeader integrálva
 *
 * Funkciók:
 *   - Vendégkeresés (név, telefonszám alapján)
 *   - Új vendég létrehozása
 *   - "Új Kiszállítási Rendelés" gomb (placeholder)
 *   - Zóna ellenőrzés irányítószám alapján
 *
 * TODO (V4.0):
 *   - Teljes rendelésfelvételi folyamat integrációja
 *   - Termékválasztás, kosár kezelés
 *   - Fizetési mód választás
 */

import { useState } from 'react';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { getCustomers } from '@/services/crmService';
import { getZoneByZipCode } from '@/services/logisticsService';
import type { Customer } from '@/types/customer';
import type { DeliveryZone } from '@/types/logistics';
import './OperatorPage.css';

export const OperatorPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  // Zóna ellenőrzés
  const [zipCode, setZipCode] = useState('');
  const [deliveryZone, setDeliveryZone] = useState<DeliveryZone | null>(null);
  const [zoneMessage, setZoneMessage] = useState('');

  // Vendég keresés
  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      alert('Kérlek adj meg keresési kifejezést (név, email, telefon)!');
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

  // Vendég kiválasztása
  const handleSelectCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setSearchResults([]);
    setSearchTerm('');
  };

  // Zóna ellenőrzés irányítószám alapján
  const handleCheckZone = async () => {
    if (!zipCode.trim()) {
      alert('Kérlek adj meg irányítószámot!');
      return;
    }

    try {
      const response = await getZoneByZipCode(zipCode);
      setDeliveryZone(response.zone);
      setZoneMessage(response.message);
    } catch (error) {
      console.error('Hiba a zóna ellenőrzésekor:', error);
      alert('Nem sikerült ellenőrizni a zónát!');
    }
  };

  // Új rendelés indítása (placeholder)
  const handleStartNewOrder = () => {
    if (!selectedCustomer) {
      alert('Először válassz ki egy vendéget!');
      return;
    }
    alert(
      `ÚJ KISZÁLLÍTÁSI RENDELÉS\n\nVendég: ${selectedCustomer.first_name} ${selectedCustomer.last_name}\n\n(Ez még placeholder funkció - V4.0-ban lesz teljes rendelésfelvétel)`
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
