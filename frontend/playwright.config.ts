import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './playwright-tests',
  timeout: 3000,
  use: {
    headless: true,
  },
});
