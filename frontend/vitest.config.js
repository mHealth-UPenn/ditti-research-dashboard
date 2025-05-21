import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    projects: ["src/*"],
    globals: true,
    environment: "jsdom",
  },
});
