import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  base: '/static/ui/',
  build: {
    outDir: '../static/ui',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: { input: 'src/main.ts' },
  },
  server: { fs: { allow: ['..'] } },
});
