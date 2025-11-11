import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import path from "node:path"
import tailwindcss from '@tailwindcss/vite'
import wasm from "vite-plugin-wasm";

const host = process.env.TAURI_DEV_HOST;

// https://vite.dev/config/
export default defineConfig({
  worker: {
    format: 'es'
  },
  clearScreen: false,
  server: {
    port: 5173,
    strictPort: true,
    host: host || false,
    hmr: host
      ? {
        protocol: 'ws',
        host,
        port: 1421,
      }
      : undefined,
    watch: {
      // tell vite to ignore watching `src-tauri`
      ignored: ['**/src-tauri/**'],
    },
  },
  envPrefix: ['VITE_', 'TAURI_ENV_*'],
  plugins: [svelte(), tailwindcss(), wasm()],
  build: {
    outDir: "./dist",
    emptyOutDir: true,
    // Tauri uses Chromium on Windows and WebKit on macOS and Linux
    target:
      process.env.TAURI_ENV_PLATFORM == 'windows'
        ? 'chrome105'
        : 'safari13',
    // don't minify for debug builds
    minify: !process.env.TAURI_ENV_DEBUG ? 'esbuild' : false,
    // produce sourcemaps for debug builds
    sourcemap: !!process.env.TAURI_ENV_DEBUG,
  },
  resolve: {
    alias: {

      $components: path.resolve("./src/components"),
      $pages: path.resolve("./src/pages"),
      $modules: path.resolve("./src/modules"),

      $lib: path.resolve("./src/lib"),

      $controllers: path.resolve("./src/controllers"),
    },
  },

})
