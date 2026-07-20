import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Front servido pela própria FastAPI em produção (mesma origem, base '/').
// Em dev, o Vite (5173) faz proxy de /api para a API (8000).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8000' },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
