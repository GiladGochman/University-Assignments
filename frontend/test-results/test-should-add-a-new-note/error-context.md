# Test info

- Name: should add a new note
- Location: C:\Users\Rotem Aftabi\submission_hw1\frontend\playwright-tests\test.spec.ts:51:1

# Error details

```
Error: page.click: Test timeout of 10000ms exceeded.
Call log:
  - waiting for locator('button[name="add_new_note"]')

    at C:\Users\Rotem Aftabi\submission_hw1\frontend\playwright-tests\test.spec.ts:52:14
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
   8 | test.setTimeout(10000);
   9 | test.beforeEach(async ({ page }) => {
  10 |   await page.request.delete(`${API_URL}/test/reset`);
  11 |
  12 |   await page.request.post(`${API_URL}/users`, {
  13 |     data: {
  14 |       name: 'Test User',
  15 |       email: 'test@example.com',
  16 |       username: 'testuser',
  17 |       password: 'testpass',
  18 |     },
  19 |   });
  20 |
  21 |   const loginResponse = await page.request.post(`${API_URL}/login`, {
  22 |     data: {
  23 |       username: 'testuser',
  24 |       password: 'testpass',
  25 |     },
  26 |   });
  27 |   const loginData = await loginResponse.json();
  28 |   token = loginData.token;
  29 |
  30 |   await page.addInitScript((value) => {
  31 |     window.localStorage.setItem('user-token', value);
  32 |   }, token);
  33 |
  34 |   await page.request.post(`${API_URL}/notes`, {
  35 |     data: {
  36 |       title: 'Test Note',
  37 |       content: 'Initial content',
  38 |       author: { name: 'Test User', email: 'test@example.com' },
  39 |     },
  40 |     headers: { Authorization: `Bearer ${token}` },
  41 |   });
  42 |
  43 |   await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 10000 });
  44 | });
  45 |
  46 | test('should display a list of notes', async ({ page }) => {
  47 |   const notes = page.locator('.note');
  48 |   await expect(notes).toHaveCount(1);
  49 | });
  50 |
  51 | test('should add a new note', async ({ page }) => {
> 52 |   await page.click('button[name="add_new_note"]');
     |              ^ Error: page.click: Test timeout of 10000ms exceeded.
  53 |   await page.fill('input[name="text_input_new_note"]', 'Playwright test note');
  54 |   await page.click('button[name="text_input_save_new_note"]');
  55 |   await expect(page.locator('.notification')).toHaveText('Added a new note');
  56 |   await expect(page.locator('.note').first()).toContainText('Playwright test note');
  57 | });
  58 |
  59 | test('should edit a note', async ({ page }) => {
  60 |   const firstNote = page.locator('.note').first();
  61 |   const noteId = await firstNote.getAttribute('data-testid');
  62 |   await page.click(`button[data-testid="edit-${noteId}"]`);
  63 |   await page.fill(`textarea[data-testid="text_input-${noteId}"]`, 'Updated content');
  64 |   await page.click(`button[data-testid="text_input_save-${noteId}"]`);
  65 |   await expect(page.locator('.notification')).toHaveText('Note updated');
  66 |   await expect(page.locator(`.note[data-testid="${noteId}"]`)).toContainText('Updated content');
  67 | });
  68 |
  69 | test('should delete a note', async ({ page }) => {
  70 |   const notes = page.locator('.note');
  71 |   await expect(notes).toHaveCount(1);
  72 |   const noteId = await notes.first().getAttribute('data-testid');
  73 |   await page.click(`button[name="delete-${noteId}"]`);
  74 |   await expect(page.locator('.notification')).toHaveText('Note deleted');
  75 |   await expect(page.locator('.note')).toHaveCount(0);
  76 | });
  77 |
  78 | test('should navigate between pages with pagination', async ({ page }) => {
  79 |   for (let i = 0; i < 11; i++) {
  80 |     await page.request.post(`${API_URL}/notes`, {
  81 |       data: {
  82 |         title: `Note ${i + 1}`,
  83 |         content: 'Some content',
  84 |         author: { name: 'Test User', email: 'test@example.com' },
  85 |       },
  86 |       headers: { Authorization: `Bearer ${token}` },
  87 |     });
  88 |   }
  89 |
  90 |   await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 10000 });
  91 |
  92 |   await expect(page.locator('.note')).toHaveCount(5);
  93 |   await page.click('button[name="next"]');
  94 |   await expect(page.locator('.note')).toHaveCount(5);
  95 |   await page.click('button[name="next"]');
  96 |   await expect(page.locator('.note')).toHaveCount(2);
  97 | });
  98 |
```