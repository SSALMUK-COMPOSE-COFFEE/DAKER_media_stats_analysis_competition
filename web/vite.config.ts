import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  // 서브패스 배포용 (예: https://hajin.xyz/media-stats-analysis-competition/) — 앞뒤 슬래시 필수
  base: process.env.BASE_PATH || '/',
  plugins: [react(), tailwindcss()],
})
