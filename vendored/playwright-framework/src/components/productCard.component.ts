import type { Locator, Page } from '@playwright/test';

export class ProductCardComponent {
  constructor(private readonly root: Locator) {}

  static byIndex(page: Page, index: number): ProductCardComponent {
    return new ProductCardComponent(page.locator('.product-image-wrapper').nth(index));
  }

  static byProductId(page: Page, productId: number): ProductCardComponent {
    return new ProductCardComponent(
      page
        .locator('.product-image-wrapper')
        .filter({ has: page.locator(`a.add-to-cart[data-product-id="${productId}"]`) }),
    );
  }

  get name(): Locator {
    return this.root.locator('.productinfo p');
  }

  get price(): Locator {
    return this.root.locator('.productinfo h2');
  }

  get addToCartButton(): Locator {
    return this.root.locator('.productinfo .add-to-cart');
  }

  get viewProductLink(): Locator {
    return this.root.locator('.choose a', { hasText: 'View Product' });
  }

  async addToCart(): Promise<void> {
    await this.addToCartButton.click();
  }

  async viewProduct(): Promise<void> {
    await this.viewProductLink.click();
  }
}
