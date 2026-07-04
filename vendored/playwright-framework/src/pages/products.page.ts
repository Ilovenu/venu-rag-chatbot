import type { Page } from '@playwright/test';
import { BasePage } from './base.page';
import { ProductCardComponent } from '../components/productCard.component';

export class ProductsPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get searchInput() {
    return this.page.locator('#search_product');
  }

  get searchButton() {
    return this.page.locator('#submit_search');
  }

  get searchedProductsTitle() {
    return this.page.locator('h2.title', { hasText: 'Searched Products' });
  }

  get allProductsTitle() {
    return this.page.locator('h2.title', { hasText: 'All Products' });
  }

  get productCards() {
    return this.page.locator('.product-image-wrapper');
  }

  async open(): Promise<void> {
    await this.goto('/products');
  }

  async search(term: string): Promise<void> {
    await this.searchInput.fill(term);
    await this.searchButton.click();
  }

  card(index: number): ProductCardComponent {
    return ProductCardComponent.byIndex(this.page, index);
  }

  cardByProductId(productId: number): ProductCardComponent {
    return ProductCardComponent.byProductId(this.page, productId);
  }

  async resultCount(): Promise<number> {
    return this.productCards.count();
  }
}
