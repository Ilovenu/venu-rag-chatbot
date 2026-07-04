import type { Page } from '@playwright/test';

export class CartModalComponent {
  private readonly root;

  constructor(page: Page) {
    this.root = page.locator('#cartModal');
  }

  get viewCartLink() {
    return this.root.locator('a[href="/view_cart"]');
  }

  get continueShoppingButton() {
    return this.root.locator('.close-modal');
  }

  async waitUntilVisible(): Promise<void> {
    await this.root.waitFor({ state: 'visible' });
  }

  async viewCart(): Promise<void> {
    await this.waitUntilVisible();
    await this.viewCartLink.click();
  }

  async continueShopping(): Promise<void> {
    await this.waitUntilVisible();
    await this.continueShoppingButton.click();
  }
}
