/**
 * LoginPage - PIN-alapú bejelentkezés
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await login({ username, password: pin });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Hibás felhasználónév vagy PIN kód');
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h1>POS Bejelentkezés</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Felhasználónév</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="jkovacs"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="pin">PIN Kód</label>
            <input
              id="pin"
              type="password"
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              placeholder="****"
              required
              maxLength={4}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Bejelentkezés...' : 'Bejelentkezés'}
          </button>
        </form>
      </div>
    </div>
  );
};
