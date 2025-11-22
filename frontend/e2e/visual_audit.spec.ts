/**
 * Visual Audit Test - A-Epic On-prem Dining Flow
 * Complete user journey with screenshots at each step
 *
 * Purpose: Identify UI glitches, layout issues, and visual inconsistencies
 */

import { test, expect } from '@playwright/test';
import path from 'path';

// Screenshot directory
const SCREENSHOT_DIR = path.join(process.cwd(), 'test-results', 'visual-audit');

test.describe('A-Epic Visual Audit - Complete Flow', () => {
  test('Complete dining flow with visual checkpoints', async ({ page }) => {
    // Set viewport to standard desktop size
    await page.setViewportSize({ width: 1920, height: 1080 });

    // ========================================
    // STEP 1: LOGIN
    // ========================================
    console.log('[STEP 1] Navigating to login page...');
    await page.goto('http://localhost:5173/login');
    await page.waitForLoadState('networkidle');

    // Fill login form with correct credentials
    await page.fill('#username', 'admin');
    await page.fill('#pin', '1234');

    // Take screenshot BEFORE clicking login
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, '01-login.png'),
      fullPage: true
    });
    console.log('[STEP 1] Screenshot saved: 01-login.png');

    // Click login button with correct text
    const loginButton = page.locator('button:has-text("Bejelentkezés")');
    await loginButton.click();

    // Wait for navigation to /tables
    await page.waitForURL('**/tables', { timeout: 10000 });
    await page.waitForLoadState('networkidle');

    // ========================================
    // STEP 2: TABLE MAP
    // ========================================
    console.log('[STEP 2] Checking table map page...');

    // Navigate to tables if not already there
    const currentUrl = page.url();
    if (!currentUrl.includes('/tables')) {
      await page.goto('http://localhost:5173/tables');
      await page.waitForLoadState('networkidle');
    }

    // Wait for tables to load
    await page.waitForSelector('text=/asztal|table/i', { timeout: 10000 }).catch(() => {
      console.warn('[STEP 2] No tables found on page, continuing anyway...');
    });

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, '02-tables.png'),
      fullPage: true
    });
    console.log('[STEP 2] Screenshot saved: 02-tables.png');

    // ========================================
    // STEP 3: SELECT TABLE & NAVIGATE TO ORDER PAGE
    // ========================================
    console.log('[STEP 3] Selecting a table and navigating to order page...');

    // Try to find and click a table (look for various possible selectors)
    const tableSelector = await page.locator('button:has-text("Asztal"), [class*="table"], [data-table-id]').first();
    const tableExists = await tableSelector.count() > 0;

    if (tableExists) {
      await tableSelector.click();
      await page.waitForTimeout(1000); // Wait for any modal or navigation
    } else {
      console.warn('[STEP 3] No table found, navigating directly to /orders/new');
      await page.goto('http://localhost:5173/orders/new');
    }

    // Ensure we're on order page
    if (!page.url().includes('/orders')) {
      await page.goto('http://localhost:5173/orders/new');
    }
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, '03-order-empty.png'),
      fullPage: true
    });
    console.log('[STEP 3] Screenshot saved: 03-order-empty.png');

    // ========================================
    // STEP 4: ADD PRODUCTS TO CART
    // ========================================
    console.log('[STEP 4] Adding products to cart...');

    // Wait for products to load
    await page.waitForSelector('[class*="product"], [data-product-id], button:has-text("Hozzáad"), button:has-text("Add")', { timeout: 10000 }).catch(() => {
      console.warn('[STEP 4] No products found on page');
    });

    // Try to add 2-3 products to cart
    const addButtons = page.locator('button:has-text("Hozzáad"), button:has-text("Add"), button:has-text("+")');
    const addButtonCount = await addButtons.count();

    if (addButtonCount > 0) {
      // Add first product
      await addButtons.first().click();
      await page.waitForTimeout(500);

      // Add second product if available
      if (addButtonCount > 1) {
        await addButtons.nth(1).click();
        await page.waitForTimeout(500);
      }

      // Add third product if available
      if (addButtonCount > 2) {
        await addButtons.nth(2).click();
        await page.waitForTimeout(500);
      }
    } else {
      console.warn('[STEP 4] No "Add" buttons found');
    }

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, '04-order-cart.png'),
      fullPage: true
    });
    console.log('[STEP 4] Screenshot saved: 04-order-cart.png');

    // ========================================
    // STEP 5: OPEN PAYMENT MODAL
    // ========================================
    console.log('[STEP 5] Opening payment modal...');

    // Look for "Checkout" or "Fizetés" button
    const checkoutButton = page.locator('button:has-text("Fizetés"), button:has-text("Checkout"), button:has-text("Rendelés leadása")').first();
    const checkoutExists = await checkoutButton.count() > 0;

    if (checkoutExists) {
      await checkoutButton.click();
      await page.waitForTimeout(1000); // Wait for modal to open

      // Wait for payment modal to appear
      await page.waitForSelector('[class*="modal"], [role="dialog"], text=/fizetés|payment/i', { timeout: 5000 }).catch(() => {
        console.warn('[STEP 5] Payment modal not detected');
      });
    } else {
      console.warn('[STEP 5] No checkout button found');
    }

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, '05-payment-modal.png'),
      fullPage: true
    });
    console.log('[STEP 5] Screenshot saved: 05-payment-modal.png');

    // ========================================
    // STEP 6: INVOICE PREVIEW (if available)
    // ========================================
    console.log('[STEP 6] Checking for invoice preview...');

    // Look for invoice button or link
    const invoiceButton = page.locator('button:has-text("Számla"), button:has-text("Invoice")').first();
    const invoiceExists = await invoiceButton.count() > 0;

    if (invoiceExists) {
      await invoiceButton.click();
      await page.waitForTimeout(1000);
    } else {
      console.warn('[STEP 6] No invoice button found, screenshot will show current state');
    }

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, '06-invoice.png'),
      fullPage: true
    });
    console.log('[STEP 6] Screenshot saved: 06-invoice.png');

    // ========================================
    // STEP 7: FINANCE/DAILY CLOSURE PAGE
    // ========================================
    console.log('[STEP 7] Navigating to finance/daily closure page...');

    // Navigate to admin/finance page
    await page.goto('http://localhost:5173/admin/finance');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, '07-finance.png'),
      fullPage: true
    });
    console.log('[STEP 7] Screenshot saved: 07-finance.png');

    console.log('[VISUAL AUDIT] All screenshots captured successfully!');
  });
});
