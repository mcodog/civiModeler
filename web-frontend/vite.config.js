import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      ignored: ["**/src/assets/*.zip", "**/src/assets/loaders/build.gif"],
    },
  },
  optimizeDeps: {
    include: ["@react-three/drei"],
  },
});
