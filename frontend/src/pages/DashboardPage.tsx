/**
 * DashboardPage - Főoldal bejelentkezés után
 */

import { useAuth } from '@/hooks/useAuth';

export const DashboardPage = () => {
  const { user, logout } = useAuth();

  return (
    <div className="dashboard-page">
      <header>
        <h1>POS Dashboard</h1>
        <div className="user-info">
          <span>Üdvözöljük, {user?.name}!</span>
          <button onClick={logout}>Kijelentkezés</button>
        </div>
      </header>

      <main>
        <h2>Funkciók:</h2>
        <ul>
          <li>Asztaltérkép (később implementálva)</li>
          <li>Konyhai Kijelző (KDS) (később implementálva)</li>
          <li>Fizetési képernyő (később implementálva)</li>
        </ul>

        <div className="user-permissions">
          <h3>Jogosultságok:</h3>
          <ul>
            {user?.permissions.map((perm) => (
              <li key={perm}>{perm}</li>
            ))}
          </ul>
        </div>
      </main>
    </div>
  );
};
