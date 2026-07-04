import type { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class HomePage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get subscriptionEmailInput() {
    return this.page.locator('#susbscribe_email');
  }

  get subscribeButton() {
    return this.page.locator('#subscribe');
  }

  get subscriptionSuccessMessage() {
    return this.page.locator('#success-subscribe .alert-success');
  }

  async open(): Promise<void> {
    await this.goto('/');
  }

  async subscribe(email: string): Promise<void> {
    await this.subscriptionEmailInput.fill(email);
    await this.subscribeButton.click();
  }
}
