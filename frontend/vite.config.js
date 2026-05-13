import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { quasar, transformAssetUrls } from '@quasar/vite-plugin'
import path from 'path'

export default defineConfig({
  plugins: [
    vue({
      template: { transformAssetUrls },
    }),
    quasar({
      sassVariables: 'src/css/quasar.variables.scss',
    }),
  ],

  resolve: {
    alias: {
      // allows "src/..." imports inside .vue and .js files
      src: path.resolve(__dirname, './src'),
    },
  },

  server: {
    port: 9000,
    open: true,
    proxy: {
      // forward /api/* to the Flask backend — no CORS issues in dev
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
