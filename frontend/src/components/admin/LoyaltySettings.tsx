/**
 * LoyaltySettings - Hűségprogram beállítások megjelenítése
 *
 * Funkciók:
 *   - Pontgyűjtési szabályok megjelenítése
 *   - Loyalty program áttekintése
 */

import './LoyaltySettings.css';

export const LoyaltySettings = () => {
  // TODO: Ezek a beállítások később betölthetők lesznek egy API-ból
  const settings = {
    pointsPerHundredHuf: 1, // 100 Ft = 1 pont
    pointValue: 10, // 1 pont = 10 Ft értékű
    minRedemptionPoints: 100, // Minimum beváltható pont
  };

  return (
    <div className="loyalty-settings">
      <header className="settings-header">
        <h1>💎 Hűségprogram beállítások</h1>
      </header>

      <div className="settings-content">
        <div className="settings-card">
          <h2>Pontgyűjtési szabályok</h2>
          <div className="settings-grid">
            <div className="setting-item">
              <span className="setting-icon">💰</span>
              <div className="setting-details">
                <strong>Pontgyűjtés vásárláskor</strong>
                <p>
                  Minden {100} Ft vásárlás után {settings.pointsPerHundredHuf} pont jár
                </p>
              </div>
            </div>

            <div className="setting-item">
              <span className="setting-icon">🎁</span>
              <div className="setting-details">
                <strong>Pont értéke</strong>
                <p>1 pont = {settings.pointValue} Ft kedvezmény</p>
              </div>
            </div>

            <div className="setting-item">
              <span className="setting-icon">🔓</span>
              <div className="setting-details">
                <strong>Minimum beváltás</strong>
                <p>
                  Minimum {settings.minRedemptionPoints} pont szükséges a beváltáshoz
                </p>
              </div>
            </div>

            <div className="setting-item">
              <span className="setting-icon">📊</span>
              <div className="setting-details">
                <strong>Példa számítás</strong>
                <p>
                  5 000 Ft vásárlás = {(5000 / 100) * settings.pointsPerHundredHuf} pont
                  <br />
                  {settings.minRedemptionPoints} pont ={' '}
                  {settings.minRedemptionPoints * settings.pointValue} Ft kedvezmény
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="settings-card">
          <h2>További információk</h2>
          <div className="info-section">
            <p>
              <strong>Pontok érvényessége:</strong> A pontok korlátlan ideig
              érvényesek, amíg a vendég fiókja aktív.
            </p>
            <p>
              <strong>Manuális pontjóváírás:</strong> Az adminisztrátorok manuálisan is
              adhatnak vagy vonhatnak le pontokat a vendégek fiókjából.
            </p>
            <p>
              <strong>Pontok nyomon követése:</strong> A vendégek láthatják pontegyenlegüket
              és tranzakcióikat a vendégpanelen.
            </p>
          </div>
        </div>

        <div className="settings-note">
          <p>
            💡 <strong>Megjegyzés:</strong> Ezek a beállítások jelenleg fix értékek.
            A jövőben lehetőség lesz dinamikus konfigurációra.
          </p>
        </div>
      </div>
    </div>
  );
};
