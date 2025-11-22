/**
 * QuickOrderButton - Quick access button to create new orders
 * Provides easy navigation to order creation page
 */

import { useNavigate } from 'react-router-dom';
import './QuickOrderButton.css';

export const QuickOrderButton = () => {
  const navigate = useNavigate();

  const handleCreateOrder = () => {
    navigate('/orders/new');
  };

  return (
    <div className="quick-order-button">
      <button onClick={handleCreateOrder} className="quick-order-btn">
        <span className="quick-order-icon">➕</span>
        <div className="quick-order-content">
          <span className="quick-order-title">Új Rendelés</span>
          <span className="quick-order-subtitle">Gyors rendelésfelvétel</span>
        </div>
      </button>
    </div>
  );
};
