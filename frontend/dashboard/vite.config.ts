import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/upload': 'http://api-gateway:8000',
      '/documents': 'http://api-gateway:8000',
      '/keys': 'http://key-manager:8000',
    }
  }
})
