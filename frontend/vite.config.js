import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],

  server: {
    host: "0.0.0.0",
    allowedHosts: ["4e15d65a5129.ngrok-free.app"],
  },

  build: {
    outDir: "../backend/dist",
    assetsDir: "assets", // Subdirectory inside outDir for static assets
    sourcemap: true, // Generate source maps
    emptyOutDir: true, // Clean the output dir before building
  },
});
