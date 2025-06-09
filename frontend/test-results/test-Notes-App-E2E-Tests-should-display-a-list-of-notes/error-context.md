# Test info

- Name: Notes App E2E Tests >> should display a list of notes
- Location: C:\Users\Study\Desktop\semester F\תכנות קצה\submission_hw2\frontend\playwright-tests\test.spec.ts:19:7

# Error details

```
Error: Timed out 5000ms waiting for expect(locator).toHaveCount(expected)

Locator: locator('.note')
Expected: 1
Received: 10
Call log:
  - expect.toHaveCount with timeout 5000ms
  - waiting for locator('.note')
    3 × locator resolved to 0 elements
      - unexpected value "0"
    5 × locator resolved to 10 elements
      - unexpected value "10"

    at C:\Users\Study\Desktop\semester F\תכנות קצה\submission_hw2\frontend\playwright-tests\test.spec.ts:21:25
```

# Page snapshot

```yaml
- button "Add Note"
- heading "Note 1" [level=2]
- text: By Author 1 Content for note 1
- heading "Note 2" [level=2]
- text: By Author 2 Content for note 2
- heading "Note 3" [level=2]
- text: By Author 3 Content for note 3
- heading "Note 4" [level=2]
- text: By Author 4 Content for note 4
- heading "Note 5" [level=2]
- text: By Author 5 Content for note 5
- heading "Note 6" [level=2]
- text: By Author 6 Content for note 6
- heading "Note 7" [level=2]
- text: By Author 7 Content for note 7
- heading "Note 8" [level=2]
- text: By Author 8 Content for note 8
- heading "Note 9" [level=2]
- text: By Author 9 Content for note 9
- heading "Note 10" [level=2]
- text: "By Author 10 Content for note 10 page: 1 / 1"
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
  11 |         author: { name: "Rotem", email: "rotem@example.com" },
  12 |         content: "Initial content",
  13 |       },
  14 |     });
  15 |     await page.goto(BASE_URL);
  16 |   });
  17 |
  18 |   // 1. Read notes
  19 |   test("should display a list of notes", async ({ page }) => {
  20 |     const notes = page.locator(".note");
> 21 |     await expect(notes).toHaveCount(1);
     |                         ^ Error: Timed out 5000ms waiting for expect(locator).toHaveCount(expected)
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
  42 |     await page.click(`button[data-testid="edit-${noteId}"]`);
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