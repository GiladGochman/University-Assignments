import { test, expect } from '@playwright/test';

test('register → login → logout', async ({ page }) => {
  const BASE = 'http://localhost:3000';

  // generate a fresh user each time
  const unique = Date.now();
  const user     = `bob${unique}`;
  const email    = `bob${unique}@example.com`;
  const password = 'secret';

  // Register
  await page.goto(`${BASE}/create-user`);
  await page.fill('[data-testid="create_user_form_name"]', `Bob ${unique}`);
  await page.fill('[data-testid="create_user_form_email"]', email);
  await page.fill('[data-testid="create_user_form_username"]', user);
  await page.fill('[data-testid="create_user_form_password"]', password);
  await page.click('[data-testid="create_user_form_create_user"]');

  // Now it should redirect to /login
  await expect(page).toHaveURL(`${BASE}/login`);

  // Login
  await page.fill('[data-testid="login_form_username"]', user);
  await page.fill('[data-testid="login_form_password"]', password);
  await page.click('[data-testid="login_form_login"]');

  // After login we end up on home
  await expect(page).toHaveURL(`${BASE}/`);
  await expect(page.locator('[data-testid="logout"]')).toBeVisible();

  // Logout
  await page.click('[data-testid="logout"]');
  await expect(page.locator('[data-testid="go_to_login_button"]')).toBeVisible();
});