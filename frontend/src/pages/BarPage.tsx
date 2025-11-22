/**
 * BarPage - Bar Management Interface
 * Sprint 1 Bar Integration
 *
 * LEFT SIDE:
 *  - BarCounterOrders
 *  - TakeawayOrders
 *  - QuickOrderButton
 *
 * RIGHT SIDE:
 *  - DrinkKdsQueue
 *
 * Features:
 *  - Clean architecture with error boundaries
 *  - Responsive layout (mobile, tablet, desktop)
 *  - Role-based visibility
 *  - Skeleton loaders for better UX
 */

import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { GlobalHeader } from '@/components/layout/GlobalHeader';
import { BarCounterOrders } from '@/components/bar/BarCounterOrders';
import { TakeawayOrders } from '@/components/bar/TakeawayOrders';
import { QuickOrderButton } from '@/components/bar/QuickOrderButton';
import { DrinkKdsQueue } from '@/components/bar/DrinkKdsQueue';
import { useAuth } from '@/hooks/useAuth';
import './BarPage.css';

export const BarPage = () => {
  const { user, hasPermission } = useAuth();

  // Check if user has bar access permissions
  const canAccessBar = hasPermission('orders:manage') || hasPermission('kds:view');

  if (!canAccessBar) {
    return (
      <div className="bar-page">
        <GlobalHeader currentPage="bar" />
        <div className="bar-unauthorized">
          <div className="unauthorized-content">
            <span className="unauthorized-icon">🔒</span>
            <h2>Hozzáférés megtagadva</h2>
            <p>Nincs jogosultságod a bár kezelőfelülethez.</p>
            <a href="/tables" className="back-link">
              ← Vissza az asztaltérképre
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bar-page">
      {/* Global Navigation Header */}
      <GlobalHeader currentPage="bar" />

      {/* Bar Page Title */}
      <div className="bar-page-header">
        <h1>🍹 Bár Kezelőfelület</h1>
        {user && (
          <div className="user-info">
            <span className="user-name">{user.name}</span>
            <span className="user-role">{user.roles.map(r => r.name).join(', ')}</span>
          </div>
        )}
      </div>

      {/* Main Content: Two-Column Layout */}
      <main className="bar-content">
        {/* LEFT COLUMN */}
        <div className="bar-left-column">
          <ErrorBoundary>
            <BarCounterOrders />
          </ErrorBoundary>

          <ErrorBoundary>
            <TakeawayOrders />
          </ErrorBoundary>

          <ErrorBoundary>
            <QuickOrderButton />
          </ErrorBoundary>
        </div>

        {/* RIGHT COLUMN */}
        <div className="bar-right-column">
          <ErrorBoundary>
            <DrinkKdsQueue />
          </ErrorBoundary>
        </div>
      </main>
    </div>
  );
};
