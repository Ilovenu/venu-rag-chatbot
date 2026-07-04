import type { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class AccountCreatedPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get accountCreatedMessage() {
    return this.page.locator('[data-qa="account-created"]');
  }

  get accountDeletedMessage() {
    return this.page.locator('[data-qa="account-deleted"]');
  }

  get continueButton() {
    return this.page.locator('[data-qa="continue-button"]');
  }

  async continueToHome(): Promise<void> {
    await this.continueButton.click();
  }
}
