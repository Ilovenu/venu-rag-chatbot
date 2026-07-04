import { test as base } from '@playwright/test';
import { ApiClient } from '../api/apiClient';
import { generateFakeUser } from '../utils/faker.util';
import type { User } from '../api/models/user.model';
import { HomePage } from '../pages/home.page';
import { LoginSignupPage } from '../pages/loginSignup.page';
import { SignupInfoPage } from '../pages/signupInfo.page';
import { AccountCreatedPage } from '../pages/accountCreated.page';
import { ProductsPage } from '../pages/products.page';
import { ProductDetailsPage } from '../pages/productDetails.page';
import { CartPage } from '../pages/cart.page';
import { CheckoutPage } from '../pages/checkout.page';
import { PaymentPage } from '../pages/paymentPage';
import { ContactUsPage } from '../pages/contactUs.page';

// automationexercise.com serves live Google ad interstitials/vignettes that
// intercept clicks and keep the network busy indefinitely, which makes
// 'networkidle' waits and even plain clicks flaky. Blocking ad domains
// eliminates that flakiness without touching the flows under test.
const AD_DOMAINS = /doubleclick|googlesyndication|google-analytics|googletagmanager|adsbygoogle/;

type Fixtures = {
  homePage: HomePage;
  loginSignupPage: LoginSignupPage;
  signupInfoPage: SignupInfoPage;
  accountCreatedPage: AccountCreatedPage;
  productsPage: ProductsPage;
  productDetailsPage: ProductDetailsPage;
  cartPage: CartPage;
  checkoutPage: CheckoutPage;
  paymentPage: PaymentPage;
  contactUsPage: ContactUsPage;
  apiClient: ApiClient;
  testUser: User;
  createdApiUser: User;
};

export const test = base.extend<Fixtures>({
  page: async ({ page }, use) => {
    await page.route(AD_DOMAINS, (route) => route.abort());
    await use(page);
  },

  homePage: async ({ page }, use) => use(new HomePage(page)),
  loginSignupPage: async ({ page }, use) => use(new LoginSignupPage(page)),
  signupInfoPage: async ({ page }, use) => use(new SignupInfoPage(page)),
  accountCreatedPage: async ({ page }, use) => use(new AccountCreatedPage(page)),
  productsPage: async ({ page }, use) => use(new ProductsPage(page)),
  productDetailsPage: async ({ page }, use) => use(new ProductDetailsPage(page)),
  cartPage: async ({ page }, use) => use(new CartPage(page)),
  checkoutPage: async ({ page }, use) => use(new CheckoutPage(page)),
  paymentPage: async ({ page }, use) => use(new PaymentPage(page)),
  contactUsPage: async ({ page }, use) => use(new ContactUsPage(page)),

  apiClient: async ({ request }, use) => use(new ApiClient(request)),

  testUser: async ({}, use) => use(generateFakeUser()),

  createdApiUser: async ({ apiClient }, use) => {
    const user = generateFakeUser();
    await apiClient.createAccount(user);
    await use(user);
    await apiClient.deleteAccount(user.email, user.password);
  },
});

export { expect } from '@playwright/test';
