import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue({
    reactivityTransform: true, // https://vuejs.org/guide/extras/reactivity-transform.html
  })],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  // build: {
  //   minify: false,
  //   sourcemap: true,
  // },
  
  base: '/static/',
});
