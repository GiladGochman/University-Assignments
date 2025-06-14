# Test info

- Name: should delete a note
- Location: C:\Users\Rotem Aftabi\submission_hw1\frontend\playwright-tests\test.spec.ts:76:1

# Error details

```
Error: Timed out 5000ms waiting for expect(locator).toHaveText(expected)

Locator: locator('.notification')
Expected string: "Note deleted"
Received: <element(s) not found>
Call log:
  - expect.toHaveText with timeout 5000ms
  - waiting for locator('.notification')
    4 × locator resolved to <div class="notification"></div>
      - unexpected value ""

    at C:\Users\Rotem Aftabi\submission_hw1\frontend\playwright-tests\test.spec.ts:81:47
```

# Test source

```ts
   1 | import { test, expect } from '@playwright/test';
   2 |
   3 | const BASE_URL = 'http://localhost:3000';
   4 | const API_URL = 'http://localhost:3001';
   5 |
   6 | let token: string;
   7 |
   8 | test.setTimeout(10000); // זמן ריצה מרבי של 10 שניות לטסט
   9 |
   10 | test.beforeEach(async ({ page }) => {
   11 |   // איפוס השרת
   12 |   await page.request.delete(`${API_URL}/test/reset`);
   13 |
   14 |   // יצירת משתמש חדש
   15 |   await page.request.post(`${API_URL}/users`, {
   16 |     data: {
   17 |       name: 'Test User',
   18 |       email: 'test@example.com',
   19 |       username: 'testuser',
   20 |       password: 'testpass',
   21 |     },
   22 |   });
   23 |
   24 |   // התחברות וקבלת טוקן
   25 |   const loginResponse = await page.request.post(`${API_URL}/login`, {
   26 |     data: {
   27 |       username: 'testuser',
   28 |       password: 'testpass',
   29 |     },
   30 |   });
   31 |   const loginData = await loginResponse.json();
   32 |   token = loginData.token;
   33 |
   34 |   // הזרקת הטוקן ל-localStorage עוד לפני עליית האפליקציה
   35 |   await page.addInitScript((value) => {
   36 |     window.localStorage.setItem('user-token', value);
   37 |   }, token);
   38 |
   39 |   // יצירת פתק לדוגמה
   40 |   await page.request.post(`${API_URL}/notes`, {
   41 |     data: {
   42 |       title: 'Test Note',
   43 |       content: 'Initial content',
   44 |       author: { name: 'Test User', email: 'test@example.com' },
   45 |     },
   46 |     headers: { Authorization: `Bearer ${token}` },
   47 |   });
   48 |
   49 |   // ניווט לדף הבית
   50 |   await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 10000 });
   51 | });
   52 |
   53 | test('should display a list of notes', async ({ page }) => {
   54 |   const notes = page.locator('.note');
   55 |   await expect(notes).toHaveCount(1);
   56 | });
   57 |
   58 | test('should add a new note', async ({ page }) => {
   59 |   await page.click('button[name="add_new_note"]');
   60 |   await page.fill('input[name="text_input_new_note"]', 'Playwright test note');
   61 |   await page.click('button[name="text_input_save_new_note"]');
   62 |   await expect(page.locator('.notification')).toHaveText('Added a new note');
   63 |   await expect(page.locator('.note').first()).toContainText('Playwright test note');
   64 | });
   65 |
   66 | test('should edit a note', async ({ page }) => {
   67 |   const firstNote = page.locator('.note').first();
   68 |   const noteId = await firstNote.getAttribute('data-testid');
   69 |   await page.click(`button[data-testid="edit-${noteId}"]`);
   70 |   await page.fill(`textarea[data-testid="text_input-${noteId}"]`, 'Updated content');
   71 |   await page.click(`button[data-testid="text_input_save-${noteId}"]`);
   72 |   await expect(page.locator('.notification')).toHaveText('Note updated');
   73 |   await expect(page.locator(`.note[data-testid="${noteId}"]`)).toContainText('Updated content');
   74 | });
   75 |
   76 | test('should delete a note', async ({ page }) => {
   77 |   const notes = page.locator('.note');
   78 |   await expect(notes).toHaveCount(1);
   79 |   const noteId = await notes.first().getAttribute('data-testid');
   80 |   await page.click(`button[name="delete-${noteId}"]`);
>  81 |   await expect(page.locator('.notification')).toHaveText('Note deleted');
      |                                               ^ Error: Timed out 5000ms waiting for expect(locator).toHaveText(expected)
   82 |   await expect(page.locator('.note')).toHaveCount(0);
   83 | });
   84 |
   85 | test('should navigate between pages with pagination', async ({ page }) => {
   86 |   for (let i = 0; i < 11; i++) {
   87 |     await page.request.post(`${API_URL}/notes`, {
   88 |       data: {
   89 |         title: `Note ${i + 1}`,
   90 |         content: 'Some content',
   91 |         author: { name: 'Test User', email: 'test@example.com' },
   92 |       },
   93 |       headers: { Authorization: `Bearer ${token}` },
   94 |     });
   95 |   }
   96 |
   97 |   await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 10000 });
   98 |
   99 |   await expect(page.locator('.note')).toHaveCount(5);
  100 |   await page.click('button[name="next"]');
  101 |   await expect(page.locator('.note')).toHaveCount(5);
  102 |   await page.click('button[name="next"]');
  103 |   await expect(page.locator('.note')).toHaveCount(2);
  104 | });
  105 |
```