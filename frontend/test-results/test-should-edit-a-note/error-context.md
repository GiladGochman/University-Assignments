# Test info

- Name: should edit a note
- Location: C:\Users\Rotem Aftabi\submission_hw1\frontend\playwright-tests\test.spec.ts:25:1

# Error details

```
Error: page.click: Test timeout of 3000ms exceeded.
Call log:
  - waiting for locator('button[data-testid="edit-${noteId}"]')

    at C:\Users\Rotem Aftabi\submission_hw1\frontend\playwright-tests\test.spec.ts:28:14
```

# Page snapshot

```yaml
- text: Notification area
- heading "פתק בדיקה" [level=2]
- text: By רותם
- paragraph: זה פתק ראשון לדוגמה
- button "Edit"
- button "Delete"
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
   3 | const BASE_URL = 'http://localhost:3000';
   4 |
   5 | test.beforeEach(async ({ page }) => {
   6 |   await page.goto(BASE_URL);
   7 | });
   8 |
   9 | // 1. Read notes
  10 | test('should display a list of notes', async ({ page }) => {
  11 |   const notes = page.locator('.note');
  12 |   await expect(await notes.count()).toBeGreaterThan(0);
  13 | });
  14 |
  15 | // 2. Create note
  16 | test('should add a new note', async ({ page }) => {
  17 |   await page.click('button[name="add_new_note"]');
  18 |   await page.fill('input[name="text_input_new_note"]', 'Playwright test note');
  19 |   await page.click('button[name="text_input_save_new_note"]');
  20 |   await expect(page.locator('.notification')).toHaveText('Added a new note');
  21 |   await expect(page.locator('.note').first()).toContainText('Playwright test note');
  22 | });
  23 |
  24 | // 3. Update note
  25 | test('should edit a note', async ({ page }) => {
  26 |   const firstNote = page.locator('.note').first();
  27 |   const noteId = await firstNote.getAttribute('data-testid');
> 28 |   await page.click('button[data-testid="edit-${noteId}"]');
     |              ^ Error: page.click: Test timeout of 3000ms exceeded.
  29 |   await page.fill('textarea[data-testid="text_input-${noteId}"]', 'Updated content');
  30 |   await page.click('button[data-testid="text_input_save-${noteId}"]');
  31 |   await expect(page.locator('.notification')).toHaveText('Note updated');
  32 |   await expect(firstNote).toContainText('Updated content');
  33 | });
  34 |
  35 | // 4. Delete note
  36 | test('should delete a note', async ({ page }) => {
  37 |   const firstNote = page.locator('.note').first();
  38 |   const noteId = await firstNote.getAttribute('data-testid');
  39 |   await page.click('button[data-testid="delete-${noteId}"]');
  40 |   await expect(page.locator('.notification')).toHaveText('Note deleted');
  41 |   await expect(page.locator('.note[data-testid="${noteId}"]')).toHaveCount(0);
  42 | });
```