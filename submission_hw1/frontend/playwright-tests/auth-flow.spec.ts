// playwright-tests/auth-flow.spec.ts
import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:3000';

test('register → login → logout (unique user)', async ({ page }) => {
  // generate a fresh user each run
  const unique = Date.now();
  const username = `bob${unique}`;
  const email    = `bob${unique}@example.com`;
  const password = 'secret';

  // Register
  await page.goto(`${BASE}/create-user`);
  await page.fill('[data-testid="create_user_form_name"]', `Bob ${unique}`);
  await page.fill('[data-testid="create_user_form_email"]', email);
  await page.fill('[data-testid="create_user_form_username"]', username);
  await page.fill('[data-testid="create_user_form_password"]', password);
  await page.click('[data-testid="create_user_form_create_user"]');

  // after register, app redirects to home
  await expect(page).toHaveURL(`${BASE}/`);
  // show the login button
  await expect(page.locator('[data-testid="go_to_login_button"]')).toBeVisible();

  // Navigate to login
  await page.click('[data-testid="go_to_login_button"]');
  await expect(page).toHaveURL(`${BASE}/login`);

  // Login
  await page.fill('[data-testid="login_form_username"]', username);
  await page.fill('[data-testid="login_form_password"]', password);
  await page.click('[data-testid="login_form_login"]');

  // after login, back to home + logout visible
  await expect(page).toHaveURL(`${BASE}/`);
  await expect(page.locator('[data-testid="logout"]')).toBeVisible();

  // Logout
  await page.click('[data-testid="logout"]');
  await expect(page.locator('[data-testid="go_to_login_button"]')).toBeVisible();
});