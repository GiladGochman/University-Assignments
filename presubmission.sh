#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <git_repo_url>"
  exit 1
fi

REPO_URL="$1"
TMP_DIR="tmp_submission_check"
TEST_DIR="playwright-tests"

rm -rf "$TMP_DIR"
mkdir "$TMP_DIR"
cd "$TMP_DIR" || exit 1

git clone "$REPO_URL" repo
if [ $? -ne 0 ]; then
  echo "Git clone failed."
  exit 1
fi

cd repo || exit 1
git checkout tags/submission_hw1 || { echo "Tag checkout failed"; exit 1; }

npm install || { echo "npm install failed"; exit 1; }
npx playwright install || { echo "Playwright install failed"; exit 1; }

PORTS=(3000 3001)
for PORT in "${PORTS[@]}"; do
  echo "Checking port $PORT..."
  PID=$(lsof -ti tcp:$PORT)
  if [ -n "$PID" ]; then
    echo "Killing process $PID on port $PORT"
    kill -9 "$PID" || echo "Failed to kill process $PID"
  else
    echo "No process found on port $PORT"
  fi
done

npx json-server --port 3001 --watch ./data/notes.json > backend.log 2>&1 &
BACK_PID=$!
sleep 2

npm run dev > frontend.log 2>&1 &
FRONT_PID=$!
sleep 4

mkdir "$TEST_DIR"
cat > "$TEST_DIR/test.spec.js" <<'EOF'
import { test, expect } from '@playwright/test';

test('check note and pagination button', async ({ page }) => {
  await page.goto('http://localhost:3000');
  const notes = page.locator('.note');
  await expect(notes).toHaveCount(10);
  await expect(page.locator('button[name="first"]')).toBeVisible();
});

test.describe('Pagination UI and logic', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('navigation buttons always exist', async ({ page }) => {
    for (const name of ['first', 'previous', 'next', 'last']) {
      await expect(page.locator(`button[name="${name}"]`)).toBeVisible();
    }
  });

  test('correct notes per page', async ({ page }) => {
    await expect(page.locator('.note')).toHaveCount(10);
  });

  test('navigation buttons state on first page', async ({ page }) => {
    await expect(page.locator('button[name="first"]')).toBeDisabled();
    await expect(page.locator('button[name="previous"]')).toBeDisabled();
    await expect(page.locator('button[name="next"]')).toBeEnabled();
    await expect(page.locator('button[name="last"]')).toBeEnabled();
  });

  test('navigation buttons state on last page', async ({ page }) => {
    await page.locator('button[name="last"]').click();
    await expect(page.locator('button[name="next"]')).toBeDisabled();
    await expect(page.locator('button[name="last"]')).toBeDisabled();
    await expect(page.locator('button[name="first"]')).toBeEnabled();
    await expect(page.locator('button[name="previous"]')).toBeEnabled();
  });

  test('click page button updates current page', async ({ page }) => {
    await page.locator('button[name="page-2"]').click();
    const page2Button = page.locator('button[name="page-2"]');
    await expect(page2Button).toHaveClass(/active/);
  });

  test('first page button disabled on first page', async ({ page }) => {
    const firstPageBtn = page.locator('button[name="page-1"]');
    await expect(firstPageBtn).toBeDisabled();
  });

  test('each note has a unique HTML id', async ({ page }) => {
    const ids = await page.$$eval('.note', notes => notes.map(note => note.id));
    const unique = new Set(ids);
    expect(unique.size).toBe(ids.length);
  });
});
EOF

cat > playwright.config.js <<EOF
import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './$TEST_DIR',
  timeout: 10000,
  use: {
    headless: true,
  },
});
EOF

cat > vite.config.ts <<EOF
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
});
EOF

npx playwright test || {
  echo "Test failed."
  kill $BACK_PID $FRONT_PID
  exit 1
}

kill $BACK_PID $FRONT_PID
exit 0