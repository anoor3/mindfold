import { test, expect } from "@playwright/test";

test("landing page has CTA", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("link", { name: /upload csv/i })).toBeVisible();
});
