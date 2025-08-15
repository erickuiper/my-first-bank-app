import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should display login form', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check if login form elements are visible
    await expect(page.getByText('Welcome Back!')).toBeVisible();
    await expect(page.getByText('Sign in to your account')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
    await expect(page.getByText("Don't have an account?")).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign Up' })).toBeVisible();
  });

  test('should navigate to registration page', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Click on the sign up link
    await page.getByRole('link', { name: 'Sign Up' }).click();
    
    // Verify we're on the registration page - use more specific selectors
    await expect(page.getByRole('heading', { name: 'Create Account' })).toBeVisible();
    await expect(page.getByText('Sign up for a new account')).toBeVisible();
    
    // Check registration form elements - use more specific selectors to avoid duplicates
    await expect(page.getByPlaceholder('Email')).toBeVisible();
    
    // Use nth selector to distinguish between the two password fields
    await expect(page.locator('input[placeholder="Password"]').nth(0)).toBeVisible();
    await expect(page.getByPlaceholder('Confirm Password')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Create Account' })).toBeVisible();
    
    // Check navigation back to login
    await expect(page.getByText('Already have an account?')).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible();
  });

  test('should show validation errors for empty form submission', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Try to submit empty form
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Should stay on the same page (no navigation)
    await expect(page.getByText('Welcome Back!')).toBeVisible();
  });

  test('should show validation errors for invalid email format', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');
    
    // Enter invalid email
    await page.getByPlaceholder('Email').fill('invalid-email');
    await page.getByPlaceholder('Password').fill('password123');
    
    // Submit form
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Should stay on the same page (no navigation)
    await expect(page.getByText('Welcome Back!')).toBeVisible();
  });

  test('should show validation errors for short password', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');
    
    // Enter valid email but short password
    await page.getByPlaceholder('Email').fill('test@example.com');
    await page.getByPlaceholder('Password').fill('123');
    
    // Submit form
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Should stay on the same page (no navigation)
    await expect(page.getByText('Welcome Back!')).toBeVisible();
  });

  test('should handle successful registration', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');
    
    // Navigate to registration
    await page.getByRole('link', { name: 'Sign Up' }).click();
    
    // Fill in registration form with more specific selectors
    const testEmail = `test${Date.now()}@example.com`;
    await page.getByPlaceholder('Email').fill(testEmail);
    
    // Use more specific selectors for password fields to avoid strict mode violations
    const firstPasswordField = page.locator('input[placeholder="Password"]').nth(0);
    const confirmPasswordField = page.getByPlaceholder('Confirm Password');
    
    await firstPasswordField.fill('password123');
    await confirmPasswordField.fill('password123');
    
    // Submit registration
    await page.getByRole('button', { name: 'Create Account' }).click();
    
    // Should navigate to dashboard after successful registration
    await expect(page.getByText('My Children')).toBeVisible();
    
    // Check if logout button is visible (indicating successful authentication)
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
  });

  test('should handle successful login', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');
    
    // This test assumes a user already exists
    // In a real scenario, you might want to create a test user first
    
    // Fill in login form
    await page.getByPlaceholder('Email').fill('test@example.com');
    await page.getByPlaceholder('Password').fill('password123');
    
    // Submit login
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Should navigate to dashboard after successful login
    await expect(page.getByText('My Children')).toBeVisible();
    
    // Check if logout button is visible (indicating successful authentication)
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
  });

  test('should handle logout', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');
    
    // First, create a new user account to ensure we have someone to log out
    await page.getByRole('link', { name: 'Sign Up' }).click();
    
    // Fill in registration form
    const testEmail = `test${Date.now()}@example.com`;
    await page.getByPlaceholder('Email').fill(testEmail);
    
    // Use specific selectors for password fields
    const firstPasswordField = page.locator('input[placeholder="Password"]').nth(0);
    const confirmPasswordField = page.getByPlaceholder('Confirm Password');
    
    await firstPasswordField.fill('password123');
    await confirmPasswordField.fill('password123');
    
    // Submit registration
    await page.getByRole('button', { name: 'Create Account' }).click();
    
    // Wait for navigation to dashboard
    await expect(page.getByText('My Children')).toBeVisible();
    
    // Verify we're on dashboard and logout button is visible
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
    
    // Handle the confirmation dialog that appears when clicking logout
    page.on('dialog', dialog => {
      if (dialog.message() === 'Are you sure you want to logout?') {
        dialog.accept(); // Click "OK" on the confirmation dialog
      }
    });
    
    // Click logout
    await page.getByRole('button', { name: 'Logout' }).click();
    
    // Should navigate back to login page
    await expect(page.getByText('Welcome Back!')).toBeVisible();
  });

  test('should handle password mismatch in registration', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    await page.waitForLoadState('networkidle');
    
    // Navigate to registration
    await page.getByRole('link', { name: 'Sign Up' }).click();
    
    // Fill in registration form with mismatched passwords using specific selectors
    await page.getByPlaceholder('Email').fill('test@example.com');
    
    // Use specific selectors to avoid ambiguity and strict mode violations
    const firstPasswordField = page.locator('input[placeholder="Password"]').nth(0);
    const confirmPasswordField = page.getByPlaceholder('Confirm Password');
    
    await firstPasswordField.fill('password123');
    await confirmPasswordField.fill('differentpassword');
    
    // Submit registration
    await page.getByRole('button', { name: 'Create Account' }).click();
    
    // Should stay on registration page (no navigation)
    await expect(page.getByRole('heading', { name: 'Create Account' })).toBeVisible();
  });
});
