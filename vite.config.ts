import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
import topLevelAwait from "vite-plugin-top-level-await";


// https://vitejs.dev/config/
export default defineConfig(async () => ({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
    topLevelAwait({
      promiseExportName: "__tla",
      promiseImportName: i => `__tla_${i}`
    })
  ],
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
  },
  envPrefix: ["VITE_", "TAURI_"],
  build:{
    target: 'esnext',
    minify: !process.env.TAURI_DEBUG ? "esbuild" : false,
    sourcemap: !!process.env.TAURI_DEBUG
  }
}));
