/*
Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
SPDX-License-Identifier: AGPL-3.0-only
Additional author-attribution term under section 7(b): see repository-root NOTICE.
*/
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  base: '/static/ui/',
  build: {
    outDir: '../static/ui',
    emptyOutDir: true,
    manifest: true,
    license: { fileName: 'third-party-licenses.txt' },
    // Preserve Vite 7's browser baseline when upgrading the bundler.
    target: ['chrome107', 'edge107', 'firefox104', 'safari16'],
    rolldownOptions: {
      input: { main: 'src/main.ts', legal: 'src/legal.css' },
      output: {
        postBanner: '/* SismosVE: AGPL-3.0-only; additional author attribution under section 7(b): /notice. Third-party licenses: /static/ui/third-party-licenses.txt */',
        // Static legal pages can load their styles without a JavaScript runtime.
        assetFileNames: asset => asset.names.includes('legal.css')
          ? 'legal.css' : 'assets/[name]-[hash][extname]',
      },
    },
  },
  server: { fs: { allow: ['..'] } },
});
