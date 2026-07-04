import type { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class CheckoutPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get addressDetailsHeading() {
    return this.page.locator('h2.heading', { hasText: 'Address Details' });
  }

  get reviewOrderHeading() {
    return this.page.locator('h2.heading', { hasText: 'Review Your Order' });
  }

  get deliveryAddress() {
    return this.page.locator('#address_delivery');
  }

  get invoiceAddress() {
    return this.page.locator('#address_invoice');
  }

  get orderTotal() {
    return this.page.locator('.cart_total_price').last();
  }

  get commentTextarea() {
    return this.page.locator('#ordermsg textarea[name="message"]');
  }

  get placeOrderButton() {
    return this.page.locator('a.check_out', { hasText: 'Place Order' });
  }

  async open(): Promise<void> {
    await this.goto('/checkout');
  }

  async addComment(comment: string): Promise<void> {
    await this.commentTextarea.fill(comment);
  }

  async placeOrder(): Promise<void> {
    await this.placeOrderButton.click();
  }
}
