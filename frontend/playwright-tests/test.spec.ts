import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:3001';

let token: string;

test.setTimeout(10000); 

test.beforeEach(async ({ page }) => {
  // איפוס השרת
  await page.request.delete(`${API_URL}/test/reset`);

  // יצירת משתמש חדש
  await page.request.post(`${API_URL}/users`, {
    data: {
      name: 'Test User',
      email: 'test@example.com',
      username: 'testuser',
      password: 'testpass',
    },
  });

  // התחברות וקבלת טוקן
  const loginResponse = await page.request.post(`${API_URL}/login`, {
    data: {
      username: 'testuser',
      password: 'testpass',
    },
  });
  const loginData = await loginResponse.json();
  token = loginData.token;

  // הזרקת הטוקן ל-localStorage עוד לפני עליית האפליקציה
  await page.addInitScript((value) => {
    window.localStorage.setItem('user-token', value);
  }, token);

  // יצירת פתק לדוגמה
  await page.request.post(`${API_URL}/notes`, {
    data: {
      title: 'Test Note',
      content: 'Initial content',
      author: { name: 'Test User', email: 'test@example.com' },
    },
    headers: { Authorization: `Bearer ${token}` },
  });

  // ניווט לדף הבית
  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 10000 });
});

test('should display a list of notes', async ({ page }) => {
  const notes = page.locator('.note');
  await expect(notes).toHaveCount(1);
});

test('should add a new note', async ({ page }) => {
  await page.click('button[name="add_new_note"]');
  await page.fill('input[name="text_input_new_note"]', 'Playwright test note');
  await page.click('button[name="text_input_save_new_note"]');
  await expect(page.locator('.notification')).toHaveText('Added a new note');
  await expect(page.locator('.note').first()).toContainText('Playwright test note');
});

test('should edit a note', async ({ page }) => {
  const firstNote = page.locator('.note').first();
  const noteId = await firstNote.getAttribute('data-testid');
  await page.click(`button[data-testid="edit-${noteId}"]`);
  await page.fill(`textarea[data-testid="text_input-${noteId}"]`, 'Updated content');
  await page.click(`button[data-testid="text_input_save-${noteId}"]`);
  await expect(page.locator('.notification')).toHaveText('Note updated');
  await expect(page.locator(`.note[data-testid="${noteId}"]`)).toContainText('Updated content');
});

test('should delete a note', async ({ page }) => {
  const notes = page.locator('.note');
  await expect(notes).toHaveCount(1);
  const noteId = await notes.first().getAttribute('data-testid');
  await page.click(`button[name="delete-${noteId}"]`);
  await expect(page.locator('.notification')).toHaveText('Note deleted');
  await expect(page.locator('.note')).toHaveCount(0);
});

test('should navigate between pages with pagination', async ({ page }) => {
  for (let i = 0; i < 11; i++) {
    await page.request.post(`${API_URL}/notes`, {
      data: {
        title: `Note ${i + 1}`,
        content: 'Some content',
        author: { name: 'Test User', email: 'test@example.com' },
      },
      headers: { Authorization: `Bearer ${token}` },
    });
  }

  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 10000 });

  await expect(page.locator('.note')).toHaveCount(5);
  await page.click('button[name="next"]');
  await expect(page.locator('.note')).toHaveCount(5);
  await page.click('button[name="next"]');
  await expect(page.locator('.note')).toHaveCount(2);
});
