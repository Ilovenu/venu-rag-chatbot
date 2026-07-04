import type { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class LoginSignupPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Login form
  get loginTitle() {
    return this.page.locator('.login-form h2', { hasText: 'Login to your account' });
  }

  get loginEmailInput() {
    return this.page.locator('[data-qa="login-email"]');
  }

  get loginPasswordInput() {
    return this.page.locator('[data-qa="login-password"]');
  }

  get loginButton() {
    return this.page.locator('[data-qa="login-button"]');
  }

  get loginErrorMessage() {
    return this.page.locator('.login-form p', { hasText: 'incorrect' });
  }

  // Signup form
  get signupTitle() {
    return this.page.locator('.signup-form h2', { hasText: 'New User Signup!' });
  }

  get signupNameInput() {
    return this.page.locator('[data-qa="signup-name"]');
  }

  get signupEmailInput() {
    return this.page.locator('[data-qa="signup-email"]');
  }

  get signupButton() {
    return this.page.locator('[data-qa="signup-button"]');
  }

  get signupErrorMessage() {
    return this.page.locator('.signup-form p', { hasText: 'already exist' });
  }

  async open(): Promise<void> {
    await this.goto('/login');
  }

  async login(email: string, password: string): Promise<void> {
    await this.loginEmailInput.fill(email);
    await this.loginPasswordInput.fill(password);
    await this.loginButton.click();
  }

  async startSignup(name: string, email: string): Promise<void> {
    await this.signupNameInput.fill(name);
    await this.signupEmailInput.fill(email);
    await this.signupButton.click();
  }
}
