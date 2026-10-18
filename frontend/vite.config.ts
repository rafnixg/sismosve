import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  base: '/static/ui/',
  build: {
    outDir: '../static/ui',
    emptyOutDir: true,
    manifest: true,
    // Preserve Vite 7's browser baseline when upgrading the bundler.
    target: ['chrome107', 'edge107', 'firefox104', 'safari16'],
    rolldownOptions: {
      input: { main: 'src/main.ts', legal: 'src/legal.css' },
      output: {
        // Static legal pages can load their styles without a JavaScript runtime.
        assetFileNames: asset => asset.names.includes('legal.css')
          ? 'legal.css' : 'assets/[name]-[hash][extname]',
      },
    },
  },
  server: { fs: { allow: ['..'] } },
});
