import vue from '@vitejs/plugin-vue'
import { getProxyOptions } from 'frappe-ui/src/utils/vite-dev-server'
import path from 'path'
import { defineConfig } from 'vite'
import { webserver_port } from '../../../sites/common_site_config.json'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/assets/portal_rrhh/frontend/',
  server: {
    host: '0.0.0.0',
    port: 8080,
    proxy: getProxyOptions({ port: webserver_port }),
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: `../${path.basename(path.resolve('..'))}/public/frontend`,
    emptyOutDir: true,
    target: 'es2015',
  },
  optimizeDeps: {
    include: ['frappe-ui > feather-icons', 'showdown', 'engine.io-client'],
  },
})
