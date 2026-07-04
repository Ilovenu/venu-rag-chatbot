import type { Page } from '@playwright/test';

export class HeaderComponent {
  private readonly root;

  constructor(page: Page) {
    this.root = page.locator('#header');
  }

  get cartLink() {
    return this.root.locator('a[href="/view_cart"]');
  }

  get signupLoginLink() {
    return this.root.locator('a[href="/login"]');
  }

  get loggedInAsText() {
    return this.root.locator('a', { hasText: 'Logged in as' });
  }

  get deleteAccountLink() {
    return this.root.locator('a[href="/delete_account"]');
  }

  get logoutLink() {
    return this.root.locator('a[href="/logout"]');
  }

  async goToCart(): Promise<void> {
    await this.cartLink.click();
  }

  async goToSignupLogin(): Promise<void> {
    await this.signupLoginLink.click();
  }

  async logout(): Promise<void> {
    await this.logoutLink.click();
  }
}
