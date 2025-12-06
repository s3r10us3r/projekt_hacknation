import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Przekieruj zapytania API do Flaska
      '/login': 'http://127.0.0.1:5000',
      '/lost_item': 'http://127.0.0.1:5000',
      '/lost_items': 'http://127.0.0.1:5000',
      '/form_autocomplete': 'http://127.0.0.1:5000',
      '/healt': 'http://127.0.0.1:5000',
    }
  }
})
