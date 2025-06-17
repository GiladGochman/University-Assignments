import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:3000";
const API_URL = "http://localhost:3001";

test("auth flow: register → login → logout", async ({ page }) => {
  const user = {
    name: "Frontend Tester",
    email: "tester@example.com",
    username: "frontend123",
    password: "securepass",
  };

  // 🔁 איפוס שרת
  await page.request.delete(`${API_URL}/test/reset`);

  // ⬅️ כניסה לדף יצירת משתמש
  await page.goto(`${BASE_URL}/create-user`);

  await page.getByTestId("create_user_form_name").fill(user.name);
  await page.getByTestId("create_user_form_email").fill(user.email);
  await page.getByTestId("create_user_form_username").fill(user.username);
  await page.getByTestId("create_user_form_password").fill(user.password);
  await page.getByTestId("create_user_form_create_user").click();

  // 📍 חוזר לדף הבית כשהמשתמש עדיין מנותק
  await expect(page).toHaveURL(`${BASE_URL}/`);
  await expect(page.getByTestId("go_to_login_button")).toBeVisible();

  // 🔐 התחברות
  await page.getByTestId("go_to_login_button").click();
  await expect(page).toHaveURL(`${BASE_URL}/login`);

  await page.getByTestId("login_form_username").fill(user.username);
  await page.getByTestId("login_form_password").fill(user.password);
  await page.getByTestId("login_form_login").click();

  // 🏠 חזרה לדף הבית, עכשיו מחובר
  await expect(page).toHaveURL(`${BASE_URL}/`);
  await expect(page.getByTestId("logout")).toBeVisible();

  // 🔄 התנתקות
  await page.getByTestId("logout").click();
  await expect(page).toHaveURL(`${BASE_URL}/`);
  await expect(page.getByTestId("go_to_login_button")).toBeVisible();
});
