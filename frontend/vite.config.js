import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Przekieruj zapytania API do Flaska
      '/api/konta/logowanie': 'http://127.0.0.1:5000',
      '/api/rzeczy_znalezione': 'http://127.0.0.1:5000',
      '/api/rzeczy_znalezione/<id_ewidencyjny>': 'http://127.0.0.1:5000',
      '/api/narzedzia/auto_uzupelnianie': 'http://127.0.0.1:5000',
      '/zdrowie': 'http://127.0.0.1:5000',
      '/api/open-data': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    }
  }
})
