# Test info

- Name: register → login → logout
- Location: /Users/roei/Documents/ProgramingProjects/Edge/submission_hw1/frontend/playwright-tests/auth-flow.spec.ts:3:1

# Error details

```
Error: expect(locator).toHaveURL(expected)

Locator: locator(':root')
Expected string: "http://localhost:3000/login"
Received string: "http://localhost:3000/"
Call log:
  - expect.toHaveURL with timeout 5000ms
  - waiting for locator(':root')
    3 × locator resolved to <html lang="en">…</html>
      - unexpected value "http://localhost:3000/create-user"
    3 × locator resolved to <html lang="en">…</html>
      - unexpected value "http://localhost:3000/"

    at /Users/roei/Documents/ProgramingProjects/Edge/submission_hw1/frontend/playwright-tests/auth-flow.spec.ts:21:22
```

# Page snapshot

```yaml
- heading "Notes" [level=1]
- button "Go to Login"
- button "Create New User"
- text: "page: 1 / NaN"
- button "first" [disabled]
- button "previous" [disabled]
- button "1" [disabled]
- button "2"
- button "3"
- button "4"
- button "5"
- button "next"
- button "last"
```

# Test source

```ts
   1 | import { test, expect } from '@playwright/test';
   2 |
   3 | test('register → login → logout', async ({ page }) => {
   4 |   const BASE = 'http://localhost:3000';
   5 |
   6 |   // generate a fresh user each time
   7 |   const unique = Date.now();
   8 |   const user     = `bob${unique}`;
   9 |   const email    = `bob${unique}@example.com`;
  10 |   const password = 'secret';
  11 |
  12 |   // Register
  13 |   await page.goto(`${BASE}/create-user`);
  14 |   await page.fill('[data-testid="create_user_form_name"]', `Bob ${unique}`);
  15 |   await page.fill('[data-testid="create_user_form_email"]', email);
  16 |   await page.fill('[data-testid="create_user_form_username"]', user);
  17 |   await page.fill('[data-testid="create_user_form_password"]', password);
  18 |   await page.click('[data-testid="create_user_form_create_user"]');
  19 |
  20 |   // Now it should redirect to /login
> 21 |   await expect(page).toHaveURL(`${BASE}/login`);
     |                      ^ Error: expect(locator).toHaveURL(expected)
  22 |
  23 |   // Login
  24 |   await page.fill('[data-testid="login_form_username"]', user);
  25 |   await page.fill('[data-testid="login_form_password"]', password);
  26 |   await page.click('[data-testid="login_form_login"]');
  27 |
  28 |   // After login we end up on home
  29 |   await expect(page).toHaveURL(`${BASE}/`);
  30 |   await expect(page.locator('[data-testid="logout"]')).toBeVisible();
  31 |
  32 |   // Logout
  33 |   await page.click('[data-testid="logout"]');
  34 |   await expect(page.locator('[data-testid="go_to_login_button"]')).toBeVisible();
  35 | });
```