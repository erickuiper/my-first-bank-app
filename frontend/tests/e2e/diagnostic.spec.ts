import { test, expect } from '@playwright/test';

// Frontend diagnostic tests - can run in CI/CD with proper setup
test.describe('Frontend Diagnostic Tests', () => {

  test('should verify application is working properly', async ({ page }) => {
    // Navigate to the frontend
    await page.goto('/');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');

    // Check if we get any content at all
    const bodyText = await page.textContent('body');
    console.log('Body content length:', bodyText?.length || 0);

    // Check if there are any console errors
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
        console.log('Console error:', msg.text());
      }
    });

    // Wait a bit for any JavaScript errors to appear
    await page.waitForTimeout(2000);

    // Check if the page has any visible content
    const isVisible = await page.isVisible('body');
    console.log('Body visible:', isVisible);

    // Try to find any text content
    const allText = await page.evaluate(() => {
      return document.body.innerText || document.body.textContent || '';
    });
    console.log('All text content:', allText);

    // Check if there are any React components rendered
    const reactRoot = await page.locator('#root, [data-reactroot]').count();
    console.log('React root elements found:', reactRoot);

    // Take a screenshot for debugging
    await page.screenshot({ path: 'diagnostic-screenshot.png', fullPage: true });

    // Log page source for debugging
    const pageSource = await page.content();
    console.log('Page source length:', pageSource.length);

    // Check if the page is actually blank
    const isBlank = await page.evaluate(() => {
      const body = document.body;
      return body.children.length === 0 ||
             (body.children.length === 1 && body.children[0].tagName === 'SCRIPT');
    });

    console.log('Page appears blank:', isBlank);

    // Basic assertions to verify the application is working
    expect(consoleErrors.length).toBeLessThan(10); // Should not have too many errors
    expect(isVisible).toBe(true); // Body should be visible
    expect(pageSource.length).toBeGreaterThan(100); // Should have some content
    expect(isBlank).toBe(false); // Page should not be blank
    expect(reactRoot).toBeGreaterThan(0); // Should have React root elements
  });

  test('should check for specific React Native Paper errors', async ({ page }) => {
    await page.goto('/');

    // Check for React Native Paper related errors
    const paperErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error' &&
          (msg.text().includes('react-native-paper') ||
           msg.text().includes('colors') ||
           msg.text().includes('theme'))) {
        paperErrors.push(msg.text());
        console.log('Paper-related error:', msg.text());
      }
    });

    await page.waitForTimeout(3000);

    console.log('Paper-related errors found:', paperErrors.length);
    paperErrors.forEach(error => console.log('Error:', error));

    // Should not have too many Paper-related errors
    expect(paperErrors.length).toBeLessThan(5);
  });

  test('should check for JavaScript bundle loading issues', async ({ page }) => {
    await page.goto('/');

    // Check if JavaScript bundles are loading
    const jsErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error' &&
          (msg.text().includes('Failed to load') ||
           msg.text().includes('Script error') ||
           msg.text().includes('Bundle'))) {
        jsErrors.push(msg.text());
        console.log('JavaScript loading error:', msg.text());
      }
    });

    await page.waitForTimeout(3000);

    console.log('JavaScript loading errors found:', jsErrors.length);
    jsErrors.forEach(error => console.log('Error:', error));

    // Should not have JavaScript loading errors
    expect(jsErrors.length).toBe(0);
  });

  test('should verify login form elements are present', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check if essential login form elements are present
    await expect(page.getByText('Welcome Back!')).toBeVisible();
    await expect(page.getByPlaceholder('Email')).toBeVisible();
    await expect(page.getByPlaceholder('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();

    console.log('✅ Login form elements are present and visible');
  });

  test('should verify navigation to registration works', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Click on sign up link
    await page.getByRole('link', { name: 'Sign Up' }).click();

    // Verify we're on registration page
    await expect(page.getByRole('heading', { name: 'Create Account' })).toBeVisible();
    await expect(page.getByText('Sign up for a new account')).toBeVisible();
    await expect(page.getByPlaceholder('Email')).toBeVisible();

    // Use specific selectors to avoid strict mode violations
    await expect(page.locator('input[placeholder="Password"]').nth(0)).toBeVisible();
    await expect(page.getByPlaceholder('Confirm Password')).toBeVisible();

    console.log('✅ Navigation to registration page works');
  });
});
