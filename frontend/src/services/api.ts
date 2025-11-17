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
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: 401 Unauthorized kezelés (token lejárt)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token lejárt vagy érvénytelen → kijelentkezés
      storage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
