import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    strictPort: false, // 允许在端口被占用时自动切换到其他端口
    open: false, // 在沙盒环境中禁用自动打开浏览器
    host: true, // 允许局域网访问
  },
})
