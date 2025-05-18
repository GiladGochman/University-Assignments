import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.beforeEach(async ({ page }) => {
  await page.goto(BASE_URL);
});

// 1. Read notes
test('should display a list of notes', async ({ page }) => {
  const notes = page.locator('.note');
  await expect(await notes.count()).toBeGreaterThan(0);
});

// 2. Create note
test('should add a new note', async ({ page }) => {
  await page.click('button[name="add_new_note"]');
  await page.fill('input[name="text_input_new_note"]', 'Playwright test note');
  await page.click('button[name="text_input_save_new_note"]');
  await expect(page.locator('.notification')).toHaveText('Added a new note');
  await expect(page.locator('.note').first()).toContainText('Playwright test note');
});

// 3. Update note
test('should edit a note', async ({ page }) => {
  const firstNote = page.locator('.note').first();
  const noteId = await firstNote.getAttribute('data-testid');
  await page.click('button[data-testid="edit-${noteId}"]');
  await page.fill('textarea[data-testid="text_input-${noteId}"]', 'Updated content');
  await page.click('button[data-testid="text_input_save-${noteId}"]');
  await expect(page.locator('.notification')).toHaveText('Note updated');
  await expect(firstNote).toContainText('Updated content');
});

// 4. Delete note
test('should delete a note', async ({ page }) => {
  const firstNote = page.locator('.note').first();
  const noteId = await firstNote.getAttribute('data-testid');
  await page.click('button[data-testid="delete-${noteId}"]');
  await expect(page.locator('.notification')).toHaveText('Note deleted');
  await expect(page.locator('.note[data-testid="${noteId}"]')).toHaveCount(0);
});