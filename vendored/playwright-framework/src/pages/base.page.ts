import type { Locator, Page } from '@playwright/test';
import { HeaderComponent } from '../components/header.component';
import { CartModalComponent } from '../components/cartModal.component';

export class BasePage {
  readonly header: HeaderComponent;
  readonly cartModal: CartModalComponent;

  constructor(protected readonly page: Page) {
    this.header = new HeaderComponent(page);
    this.cartModal = new CartModalComponent(page);
  }

  async goto(path = '/'): Promise<void> {
    await this.page.goto(path);
  }

  async waitForVisible(locator: Locator): Promise<void> {
    await locator.waitFor({ state: 'visible' });
  }
}
