import type { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class CartPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get emptyCartMessage() {
    return this.page.locator('#empty_cart', { hasText: 'Cart is empty!' });
  }

  get cartRows() {
    return this.page.locator('#cart_info_table tbody tr');
  }

  get proceedToCheckoutButton() {
    return this.page.locator('a.check_out', { hasText: 'Proceed To Checkout' });
  }

  async open(): Promise<void> {
    await this.goto('/view_cart');
  }

  rowForProduct(productId: number) {
    return this.page.locator(`#product-${productId}`);
  }

  async removeProduct(productId: number): Promise<void> {
    await this.rowForProduct(productId).locator('.cart_quantity_delete').click();
  }

  async quantityFor(productId: number): Promise<string> {
    return (await this.rowForProduct(productId).locator('.cart_quantity button').textContent()) ?? '';
  }

  async totalPriceFor(productId: number): Promise<string> {
    return (await this.rowForProduct(productId).locator('.cart_total_price').textContent()) ?? '';
  }

  async proceedToCheckout(): Promise<void> {
    await this.proceedToCheckoutButton.click();
  }
}
