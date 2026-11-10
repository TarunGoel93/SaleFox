import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/backend-5050': { target: 'http://127.0.0.1:5050', changeOrigin: true, rewrite: (path) => path.replace(/^\/backend-5050/, '') },
      '/backend-5051': { target: 'http://127.0.0.1:5051', changeOrigin: true, rewrite: (path) => path.replace(/^\/backend-5051/, '') },
      '/backend-5052': { target: 'http://127.0.0.1:5052', changeOrigin: true, rewrite: (path) => path.replace(/^\/backend-5052/, '') },
      '/backend-5053': { target: 'http://127.0.0.1:5053', changeOrigin: true, rewrite: (path) => path.replace(/^\/backend-5053/, '') },
      '/backend-5054': { target: 'http://127.0.0.1:5054', changeOrigin: true, rewrite: (path) => path.replace(/^\/backend-5054/, '') },
      '/backend-5055': { target: 'http://127.0.0.1:5055', changeOrigin: true, rewrite: (path) => path.replace(/^\/backend-5055/, '') },
      '/backend-5056': { target: 'http://127.0.0.1:5056', changeOrigin: true, rewrite: (path) => path.replace(/^\/backend-5056/, '') },
      '/backend-5057': { target: 'http://127.0.0.1:5057', changeOrigin: true, rewrite: (path) => path.replace(/^\/backend-5057/, '') },
      '/backend-5062': { target: 'http://127.0.0.1:5062', changeOrigin: true, rewrite: (path) => path.replace(/^\/backend-5062/, '') },
    }
  },
})
