import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // ========================================
      // Admin Service (Port 8008)
      // ========================================
      '/api/auth': {
        target: 'http://localhost:8008',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/auth/, '/api/v1/auth')
      },
      '/api/employees': {
        target: 'http://localhost:8008',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/employees/, '/api/v1/employees')
      },
      '/api/roles': {
        target: 'http://localhost:8008',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/roles/, '/api/v1/roles')
      },
      '/api/permissions': {
        target: 'http://localhost:8008',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/permissions/, '/api/v1/permissions')
      },
      // ÚJ: Finance API (Admin Service)
      '/api/finance': {
        target: 'http://localhost:8008',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/finance/, '/api/v1/finance')
      },
      // ÚJ: Assets API (Admin Service) - FÁZIS 3.3
      '/api/assets': {
        target: 'http://localhost:8008',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/assets/, '/api/v1/assets')
      },
      // ÚJ: Vehicles API (Admin Service) - FÁZIS 3.4
      '/api/vehicles': {
        target: 'http://localhost:8008',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/vehicles/, '/api/v1/vehicles')
      },
      // ÚJ: Reports API (Admin Service) - Dashboard Analytics
      '/api/reports': {
        target: 'http://localhost:8008',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/reports/, '/api/v1/reports')
      },

      // ========================================
      // Orders Service (Port 8002)
      // ========================================
      '/api/tables': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/tables/, '/api/v1/tables')
      },
      '/api/seats': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/seats/, '/api/v1/seats')
      },
      '/api/orders': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/orders/, '/api/v1/orders')
      },
      '/api/order_items': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/order_items/, '/api/v1/order_items')
      },
      '/api/kds': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/kds/, '/api/v1/kds')
      },
      '/api/items': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/items/, '/api/v1/items')
      },

      // ========================================
      // Menu Service (Port 8001)
      // ========================================
      '/api/categories': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/categories/, '/api/v1/categories')
      },
      '/api/products': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/products/, '/api/v1/products')
      },
      '/api/modifier_groups': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/modifier_groups/, '/api/v1/modifier_groups')
      },
      '/api/images': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/images/, '/api/v1/images')
      },
      '/api/channels': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/channels/, '/api/v1/channels')
      },

      // ========================================
      // Inventory Service (Port 8003)
      // ========================================
      '/api/inventory': {
        target: 'http://localhost:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/inventory/, '/api/v1/inventory')
      },

      // ========================================
      // CRM Service (Port 8004)
      // ========================================
      '/api/customers': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/customers/, '/api/v1/customers')
      },
      '/api/coupons': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/coupons/, '/api/v1/coupons')
      },
      '/api/gift_cards': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/gift_cards/, '/api/v1/gift_cards')
      },

      // ========================================
      // Logistics Service (Port 8006) - V3.0 Hullám 10
      // ========================================
      '/api/logistics': {
        target: 'http://localhost:8006',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/logistics/, '/api/v1')
      },
    }
  }
})
