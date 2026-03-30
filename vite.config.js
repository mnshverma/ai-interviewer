import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ['pdfjs-dist'],
  },
  server: {
    proxy: {
      '/api/kilo-gateway': {
        target: 'https://api.kilo.ai/api/gateway',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/kilo-gateway/, ''),
        secure: true
      }
    }
  }
})
