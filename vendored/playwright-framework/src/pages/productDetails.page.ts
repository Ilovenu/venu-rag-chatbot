import type { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class ProductDetailsPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get productName() {
    return this.page.locator('.product-information h2');
  }

  get category() {
    return this.page.locator('.product-information p', { hasText: 'Category' });
  }

  get price() {
    return this.page.locator('.product-information span span');
  }

  get availability() {
    return this.page.locator('.product-information p', { hasText: 'Availability' });
  }

  get condition() {
    return this.page.locator('.product-information p', { hasText: 'Condition' });
  }

  get brand() {
    return this.page.locator('.product-information p', { hasText: 'Brand' });
  }

  get quantityInput() {
    return this.page.locator('#quantity');
  }

  get addToCartButton() {
    return this.page.locator('button.cart');
  }

  get reviewNameInput() {
    return this.page.locator('#review-form #name');
  }

  get reviewEmailInput() {
    return this.page.locator('#review-form #email');
  }

  get reviewTextInput() {
    return this.page.locator('#review');
  }

  get reviewSubmitButton() {
    return this.page.locator('#button-review');
  }

  get reviewSuccessMessage() {
    // #review-section itself collapses to zero height on this site (a live CSS quirk);
    // the inner .alert-success is what actually renders visibly.
    return this.page.locator('#review-section .alert-success');
  }

  async open(productId: number): Promise<void> {
    await this.goto(`/product_details/${productId}`);
  }

  async setQuantity(quantity: number): Promise<void> {
    await this.quantityInput.fill(String(quantity));
  }

  async addToCart(): Promise<void> {
    await this.addToCartButton.click();
    await this.cartModal.waitUntilVisible();
  }

  async submitReview(name: string, email: string, review: string): Promise<void> {
    await this.reviewNameInput.fill(name);
    await this.reviewEmailInput.fill(email);
    await this.reviewTextInput.fill(review);
    await this.reviewSubmitButton.click();
  }
}
