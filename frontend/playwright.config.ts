import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./playwright-tests",
  timeout: 3000,
  use: {
    baseURL: "http://localhost:3000", // זו כתובת ברירת המחדל של Vite
    headless: true,
  },
});
