import type { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class ContactUsPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get getInTouchHeading() {
    return this.page.locator('h2', { hasText: 'Get In Touch' });
  }

  get nameInput() {
    return this.page.locator('[data-qa="name"]');
  }

  get emailInput() {
    return this.page.locator('[data-qa="email"]');
  }

  get subjectInput() {
    return this.page.locator('[data-qa="subject"]');
  }

  get messageInput() {
    return this.page.locator('[data-qa="message"]');
  }

  get uploadFileInput() {
    return this.page.locator('input[name="upload_file"]');
  }

  get submitButton() {
    return this.page.locator('[data-qa="submit-button"]');
  }

  get successMessage() {
    return this.page.locator('.status.alert-success');
  }

  get homeButton() {
    return this.page.locator('a.btn-success', { hasText: 'Home' });
  }

  async open(): Promise<void> {
    await this.goto('/contact_us');
  }

  async fillForm(name: string, email: string, subject: string, message: string): Promise<void> {
    await this.nameInput.fill(name);
    await this.emailInput.fill(email);
    await this.subjectInput.fill(subject);
    await this.messageInput.fill(message);
  }

  async submit(): Promise<void> {
    this.page.once('dialog', (dialog) => dialog.accept());
    await this.submitButton.click();
  }
}
