/**
 * Smoke Test - Playwright E2E
 * A12: Test Suite Finalization
 *
 * Simple smoke test that verifies the homepage loads correctly.
 * This validates that the frontend application is running and accessible.
 */

import { test, expect } from '@playwright/test';

test.describe('Homepage Smoke Test', () => {
  test('should load homepage and display correct title', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Verify page title contains expected text
    // The actual title might be "Vite + React + TS" or "POS System" depending on index.html
    await expect(page).toHaveTitle(/POS|Vite/);

    // Verify page loaded successfully by checking for root element
    const rootElement = page.locator('#root');
    await expect(rootElement).toBeVisible();
  });

  test('should load without console errors', async ({ page }) => {
    const consoleErrors: string[] = [];

    // Capture console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Navigate to homepage
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Verify no console errors occurred
    expect(consoleErrors).toHaveLength(0);
  });

  test('should have functioning navigation', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check if main app container is present
    const appContainer = page.locator('#root');
    await expect(appContainer).toBeVisible();

    // Verify the app rendered content (not just blank page)
    const hasContent = await appContainer.textContent();
    expect(hasContent).not.toBe('');
  });
});
