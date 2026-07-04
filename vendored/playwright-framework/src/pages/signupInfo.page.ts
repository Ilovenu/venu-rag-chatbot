import type { Page } from '@playwright/test';
import { BasePage } from './base.page';
import type { User } from '../api/models/user.model';

export class SignupInfoPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  get accountInfoTitle() {
    return this.page.locator('h2', { hasText: 'Enter Account Information' });
  }

  get titleRadio() {
    return (title: 'Mr' | 'Mrs') => this.page.locator(`#id_gender${title === 'Mr' ? 1 : 2}`);
  }

  get passwordInput() {
    return this.page.locator('[data-qa="password"]');
  }

  get daysSelect() {
    return this.page.locator('[data-qa="days"]');
  }

  get monthsSelect() {
    return this.page.locator('[data-qa="months"]');
  }

  get yearsSelect() {
    return this.page.locator('[data-qa="years"]');
  }

  get newsletterCheckbox() {
    return this.page.locator('#newsletter');
  }

  get optinCheckbox() {
    return this.page.locator('#optin');
  }

  get firstNameInput() {
    return this.page.locator('[data-qa="first_name"]');
  }

  get lastNameInput() {
    return this.page.locator('[data-qa="last_name"]');
  }

  get companyInput() {
    return this.page.locator('[data-qa="company"]');
  }

  get address1Input() {
    return this.page.locator('[data-qa="address"]');
  }

  get address2Input() {
    return this.page.locator('[data-qa="address2"]');
  }

  get countrySelect() {
    return this.page.locator('[data-qa="country"]');
  }

  get stateInput() {
    return this.page.locator('[data-qa="state"]');
  }

  get cityInput() {
    return this.page.locator('[data-qa="city"]');
  }

  get zipcodeInput() {
    return this.page.locator('[data-qa="zipcode"]');
  }

  get mobileNumberInput() {
    return this.page.locator('[data-qa="mobile_number"]');
  }

  get createAccountButton() {
    return this.page.locator('[data-qa="create-account"]');
  }

  async fillAccountInformation(user: User): Promise<void> {
    await this.titleRadio(user.title).check();
    await this.passwordInput.fill(user.password);
    await this.daysSelect.selectOption(user.birthDate);
    await this.monthsSelect.selectOption(user.birthMonth);
    await this.yearsSelect.selectOption(user.birthYear);

    if (user.newsletter) await this.newsletterCheckbox.check();
    if (user.optin) await this.optinCheckbox.check();

    await this.firstNameInput.fill(user.firstName);
    await this.lastNameInput.fill(user.lastName);
    await this.companyInput.fill(user.company);
    await this.address1Input.fill(user.address1);
    await this.address2Input.fill(user.address2);
    await this.countrySelect.selectOption(user.country);
    await this.stateInput.fill(user.state);
    await this.cityInput.fill(user.city);
    await this.zipcodeInput.fill(user.zipcode);
    await this.mobileNumberInput.fill(user.mobileNumber);
  }

  async submit(): Promise<void> {
    await this.createAccountButton.click();
  }
}
