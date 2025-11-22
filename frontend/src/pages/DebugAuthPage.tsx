import { useAuth } from '@/hooks/useAuth';
import { storage } from '@/utils/storage';

export const DebugAuthPage = () => {
  const { token, user, isAuthenticated } = useAuth();

  const storedToken = storage.getToken();
  const storedUser = storage.getUser();

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>🔍 Auth Debug Info</h1>
      
      <h2>Zustand Store State:</h2>
      <pre>{JSON.stringify({ isAuthenticated, hasToken: !!token, hasUser: !!user }, null, 2)}</pre>
      
      <h2>LocalStorage:</h2>
      <pre>{JSON.stringify({ 
        hasStoredToken: !!storedToken, 
        hasStoredUser: !!storedUser,
        tokenPreview: storedToken ? storedToken.substring(0, 30) + '...' : null
      }, null, 2)}</pre>
      
      <h2>User Data:</h2>
      <pre>{JSON.stringify(user || storedUser, null, 2)}</pre>
    </div>
  );
};
