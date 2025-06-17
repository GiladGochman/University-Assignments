# Test info

- Name: full user flow: register → login → add/edit/delete notes → pagination → logout
- Location: C:\Users\Rotem Aftabi\submission_hw1\frontend\playwright-tests\test.spec.ts:9:1

# Error details

```
Error: Timed out 5000ms waiting for expect(locator).toBeVisible()

Locator: getByTestId('logout')
Expected: visible
Received: <element(s) not found>
Call log:
  - expect.toBeVisible with timeout 5000ms
  - waiting for getByTestId('logout')

    at C:\Users\Rotem Aftabi\submission_hw1\frontend\playwright-tests\test.spec.ts:43:44
```

# Page snapshot

```yaml
- heading "Notes" [level=1]
- button "Go to Login"
- button "Create New User"
- text: "page: 1 / 0"
- button "first" [disabled]
- button "previous" [disabled]
- button "next"
- button "last"
```

# Test source

```ts
   1 | // playwright-tests/full-flow.spec.ts
   2 | import { test, expect } from "@playwright/test";
   3 |
   4 | const BASE_URL = "http://localhost:3000";
   5 | const API_URL = "http://localhost:3001";
   6 |
   7 | test.setTimeout(10000);
   8 |
   9 | test("full user flow: register → login → add/edit/delete notes → pagination → logout", async ({ page }) => {
  10 |   const user = {
  11 |     name: "Frontend Tester",
  12 |     email: "tester@example.com",
  13 |     username: "frontend123",
  14 |     password: "securepass",
  15 |   };
  16 |
  17 |   // Reset server
  18 |   await page.request.delete(`${API_URL}/test/reset`);
  19 |   await page.context().clearCookies();
  20 |   await page.goto(BASE_URL);
  21 |   await page.evaluate(() => localStorage.clear());
  22 |
  23 |   // Create user via UI
  24 |   await page.goto(`${BASE_URL}/create-user`);
  25 |   await page.getByTestId("create_user_form_name").fill(user.name);
  26 |   await page.getByTestId("create_user_form_email").fill(user.email);
  27 |   await page.getByTestId("create_user_form_username").fill(user.username);
  28 |   await page.getByTestId("create_user_form_password").fill(user.password);
  29 |   await page.getByTestId("create_user_form_create_user").click();
  30 |
  31 |   await expect(page).toHaveURL(`${BASE_URL}/`);
  32 |   await expect(page.getByTestId("go_to_login_button")).toBeVisible();
  33 |
  34 |   // Login via UI
  35 |   await page.getByTestId("go_to_login_button").click();
  36 |   await page.getByTestId("login_form_username").fill(user.username);
  37 |   await page.getByTestId("login_form_password").fill(user.password);
  38 |   await page.getByTestId("login_form_login").click();
  39 |
  40 |   await page.waitForURL(`${BASE_URL}/`, { timeout: 5000 });
  41 |
  42 |   await expect(page).toHaveURL(`${BASE_URL}/`);
> 43 |   await expect(page.getByTestId("logout")).toBeVisible();
     |                                            ^ Error: Timed out 5000ms waiting for expect(locator).toBeVisible()
  44 |
  45 |   // Add a new note
  46 |   await page.click('button[name="add_new_note"]');
  47 |   await page.fill('input[name="text_input_new_note"]', 'Playwright test note');
  48 |   await page.click('button[name="text_input_save_new_note"]');
  49 |   await expect(page.locator('.notification')).toHaveText('Added a new note');
  50 |
  51 |   // Edit note
  52 |   const firstNote = page.locator('.note').first();
  53 |   const noteId = await firstNote.getAttribute('data-testid');
  54 |   await page.click(`button[data-testid="edit-${noteId}"]`);
  55 |   await page.fill(`textarea[data-testid="text_input-${noteId}"]`, 'Updated content');
  56 |   await page.click(`button[data-testid="text_input_save-${noteId}"]`);
  57 |   await expect(page.locator('.notification')).toHaveText('Note updated');
  58 |   await expect(page.locator(`.note[data-testid="${noteId}"]`)).toContainText('Updated content');
  59 |
  60 |   // Add more notes via API
  61 |   const loginResp = await page.request.post(`${API_URL}/login`, {
  62 |     data: { username: user.username, password: user.password },
  63 |   });
  64 |   const { token } = await loginResp.json();
  65 |   for (let i = 0; i < 11; i++) {
  66 |     await page.request.post(`${API_URL}/notes`, {
  67 |       data: {
  68 |         title: `Note ${i + 1}`,
  69 |         content: "Some content",
  70 |         author: { name: user.name, email: user.email },
  71 |       },
  72 |       headers: { Authorization: `Bearer ${token}` },
  73 |     });
  74 |   }
  75 |
  76 |   await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
  77 |   await expect(page.locator(".note")).toHaveCount(5); // page 1
  78 |   await page.click('button[name="next"]');
  79 |   await expect(page.locator(".note")).toHaveCount(5); // page 2
  80 |   await page.click('button[name="next"]');
  81 |   await expect(page.locator(".note")).toHaveCount(2); // page 3
  82 |
  83 |   // Delete a note
  84 |   const toDelete = await page.locator(".note").first().getAttribute("data-testid");
  85 |   await page.click(`button[name="delete-${toDelete}"]`);
  86 |   await expect(page.locator('.notification')).toHaveText('Note deleted');
  87 |
  88 |   // Logout
  89 |   await page.getByTestId("logout").click();
  90 |   await expect(page.getByTestId("go_to_login_button")).toBeVisible();
  91 | });
  92 |
```