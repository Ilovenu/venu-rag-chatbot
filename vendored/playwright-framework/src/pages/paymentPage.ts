import type { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class PaymentPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get nameOnCardInput() {
    return this.page.locator('[data-qa="name-on-card"]');
  }

  get cardNumberInput() {
    return this.page.locator('[data-qa="card-number"]');
  }

  get cvcInput() {
    return this.page.locator('[data-qa="cvc"]');
  }

  get expiryMonthInput() {
    return this.page.locator('[data-qa="expiry-month"]');
  }

  get expiryYearInput() {
    return this.page.locator('[data-qa="expiry-year"]');
  }

  get payButton() {
    return this.page.locator('[data-qa="pay-button"]');
  }

  get orderPlacedMessage() {
    return this.page.locator('[data-qa="order-placed"]');
  }

  async fillPaymentDetails(details: {
    nameOnCard: string;
    cardNumber: string;
    cvc: string;
    expiryMonth: string;
    expiryYear: string;
  }): Promise<void> {
    await this.nameOnCardInput.fill(details.nameOnCard);
    await this.cardNumberInput.fill(details.cardNumber);
    await this.cvcInput.fill(details.cvc);
    await this.expiryMonthInput.fill(details.expiryMonth);
    await this.expiryYearInput.fill(details.expiryYear);
  }

  async confirmPayment(): Promise<void> {
    await this.payButton.click();
  }
}
