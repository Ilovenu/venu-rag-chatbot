import { test, expect } from '../../../src/fixtures/test-options';
import { generateFakeUser } from '../../../src/utils/faker.util';

test.describe('Signup', () => {
  test('registers a brand new user end-to-end @smoke', async ({
    loginSignupPage,
    signupInfoPage,
    accountCreatedPage,
    apiClient,
  }) => {
    const user = generateFakeUser();

    await loginSignupPage.open();
    await expect(loginSignupPage.signupTitle).toBeVisible();
    await loginSignupPage.startSignup(user.name, user.email);

    await expect(signupInfoPage.accountInfoTitle).toBeVisible();
    await signupInfoPage.fillAccountInformation(user);
    await signupInfoPage.submit();

    await expect(accountCreatedPage.accountCreatedMessage).toBeVisible();
    await accountCreatedPage.continueToHome();

    await expect(accountCreatedPage.header.loggedInAsText).toContainText(user.name);

    // cleanup via API so this test doesn't leak accounts
    await apiClient.deleteAccount(user.email, user.password);
  });

  test('rejects signup with an already-registered email @regression', async ({
    loginSignupPage,
    createdApiUser,
  }) => {
    await loginSignupPage.open();
    await loginSignupPage.startSignup('Duplicate Attempt', createdApiUser.email);

    await expect(loginSignupPage.signupErrorMessage).toBeVisible();
    await expect(loginSignupPage.signupErrorMessage).toHaveText('Email Address already exist!');
  });
});
