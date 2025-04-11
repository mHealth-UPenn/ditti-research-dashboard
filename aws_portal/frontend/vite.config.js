import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import svgr from 'vite-plugin-svgr';
import { nodePolyfills } from 'vite-plugin-node-polyfills'

export default defineConfig({
  plugins: [
    svgr(),
    nodePolyfills(),
    react(),
    tsconfigPaths(),
  ],
  server: {
    port: 3000
  }
});
