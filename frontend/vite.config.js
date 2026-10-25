import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // The backend's CORS settings allow this exact origin.
  server: { port: 5173, strictPort: true },
  // `globals` lets Testing Library clean up the page after each test automatically.
  test: { environment: "jsdom", globals: true },
});
