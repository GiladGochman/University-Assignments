import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./playwright-tests",
  timeout: 10000,
  use: {
    baseURL: "http://localhost:3000",
    headless: true,
  },
});
