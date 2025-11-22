/**
 * Axios instance - Központi HTTP kliens
 * Automatikus Authorization header hozzáadás (JWT Bearer token)
 *
 * FONTOS: A baseURL eltávolításra került, mivel a Vite proxy
 * resource-alapú routing-ot használ (/api/auth, /api/tables, stb.)
 */

import axios from 'axios';
import { storage } from '@/utils/storage';

// Axios instance létrehozása (baseURL nélkül - Vite proxy kezeli a routing-ot)
const apiClient = axios.create({
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: JWT token hozzáadása minden kéréshez
apiClient.interceptors.request.use(
  (config) => {
    const token = storage.getToken();
    console.log('[API Client] Request:', config.method?.toUpperCase(), config.url, {
      hasToken: !!token,
      tokenPreview: token ? `${token.substring(0, 20)}...` : 'NO TOKEN'
    });
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.warn('[API Client] ⚠️ No token found in storage! Request will fail if endpoint requires auth.');
    }
    return config;
  },
  (error) => {
    console.error('[API Client] Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response Interceptor: 401 Unauthorized kezelés (token lejárt)
apiClient.interceptors.response.use(
  (response) => {
    console.log('[API Client] Response:', response.status, response.config.method?.toUpperCase(), response.config.url);
    return response;
  },
  (error) => {
    console.error('[API Client] Response error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      detail: error.response?.data?.detail,
      fullError: error.response?.data
    });

    if (error.response?.status === 401) {
      console.warn('[API Client] ❌ 401 Unauthorized - Clearing auth and redirecting to login');
      // Token lejárt vagy érvénytelen → kijelentkezés
      storage.clear();
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      console.warn('[API Client] ❌ 403 Forbidden - User lacks required permission:', error.response?.data?.detail);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
