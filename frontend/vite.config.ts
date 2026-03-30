import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// https://vite.dev/config/
export default defineConfig({
  base: '/static/',
  plugins: [react()],  // Removed inspectAttr()
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: '../backend/staticfiles',
    emptyOutDir: true,
  },
});