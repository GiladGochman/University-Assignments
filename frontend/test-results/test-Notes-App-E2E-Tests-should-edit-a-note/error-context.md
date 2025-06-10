# Test info

- Name: Notes App E2E Tests >> should edit a note
- Location: C:\Users\Study\Desktop\semester F\תכנות קצה\submission_hw2\frontend\playwright-tests\test.spec.ts:39:7

# Error details

```
Error: page.click: Test timeout of 10000ms exceeded.
Call log:
  - waiting for locator('button[data-testid="edit-null"]')

    at C:\Users\Study\Desktop\semester F\תכנות קצה\submission_hw2\frontend\playwright-tests\test.spec.ts:42:16
```

# Page snapshot

```yaml
- button "Add Note"
- heading "Test Note" [level=2]
- text: By gilad Initial content
- paragraph: Initial content
- button "Delete"
- button "Edit"
- text: "page: 1 / 1"
- button "first" [disabled]
- button "previous" [disabled]
- button "1" [disabled]
- button "next" [disabled]
- button "last" [disabled]
```

# Test source

```ts
   1 | import { test, expect } from "@playwright/test";
   2 |
   3 | const BASE_URL = "http://localhost:3000";
   4 |
   5 | test.describe("Notes App E2E Tests", () => {
   6 |   test.beforeEach(async ({ page }) => {
   7 |     await page.request.delete("http://localhost:3001/test/reset");
   8 |     await page.request.post("http://localhost:3001/notes", {
   9 |       data: {
  10 |         title: "Test Note",
  11 |         author: { name: "gilad", email: "gochman@post.ac.il" },
  12 |         content: "Initial content",
  13 |       },
  14 |     });
  15 |     await page.goto(BASE_URL);
  16 |   });
  17 |
  18 |   // 1. Read notes
  19 |   test("should display a list of notes", async ({ page }) => {
  20 |     const notes = page.locator(".note");
  21 |     await expect(notes).toHaveCount(1);
  22 |   });
  23 |
  24 |   // 2. Create note
  25 |   test("should add a new note", async ({ page }) => {
  26 |     await page.click('button[name="add_new_note"]');
  27 |     await page.fill(
  28 |       'input[name="text_input_new_note"]',
  29 |       "Playwright test note"
  30 |     );
  31 |     await page.click('button[name="text_input_save_new_note"]');
  32 |     await expect(page.locator(".notification")).toHaveText("Added a new note");
  33 |     await expect(page.locator(".note").first()).toContainText(
  34 |       "Playwright test note"
  35 |     );
  36 |   });
  37 |
  38 |   // 3. Update note
  39 |   test("should edit a note", async ({ page }) => {
  40 |     const firstNote = page.locator(".note").first();
  41 |     const noteId = await firstNote.getAttribute("data-testid");
> 42 |     await page.click(`button[data-testid="edit-${noteId}"]`);
     |                ^ Error: page.click: Test timeout of 10000ms exceeded.
  43 |     await page.fill(
  44 |       `textarea[data-testid="text_input-${noteId}"]`,
  45 |       "Updated content"
  46 |     );
  47 |     await page.click(`button[data-testid="text_input_save-${noteId}"]`);
  48 |     await expect(page.locator(".notification")).toHaveText("Note updated");
  49 |     await expect(page.locator(`.note[data-testid="${noteId}"]`)).toContainText(
  50 |       "Updated content"
  51 |     );
  52 |   });
  53 |
  54 |   // 4. Delete note
  55 |   test("should delete a note", async ({ page }) => {
  56 |     const notes = page.locator(".note");
  57 |     await expect(notes).toHaveCount(1);
  58 |
  59 |     const noteId = await notes.first().getAttribute("data-testid");
  60 |     await page.click(`button[name="delete-${noteId}"]`);
  61 |     await expect(page.locator(".notification")).toHaveText("Note deleted");
  62 |
  63 |     await expect(page.locator(".note")).toHaveCount(0);
  64 |   });
  65 | });
  66 |
```