import { test, expect } from '../../../src/fixtures/test-options';

test.describe('Login', () => {
  test('rejects an invalid email/password combination @smoke', async ({ loginSignupPage }) => {
    await loginSignupPage.open();
    await expect(loginSignupPage.loginTitle).toBeVisible();

    await loginSignupPage.login('nonexistent.user.qa@example.com', 'wrong-password');

    await expect(loginSignupPage.loginErrorMessage).toBeVisible();
    await expect(loginSignupPage.loginErrorMessage).toHaveText('Your email or password is incorrect!');
  });

  test('logs an API-created user in and out successfully @regression', async ({
    loginSignupPage,
    createdApiUser,
  }) => {
    await loginSignupPage.open();
    await loginSignupPage.login(createdApiUser.email, createdApiUser.password);

    await expect(loginSignupPage.header.loggedInAsText).toBeVisible();
    await expect(loginSignupPage.header.loggedInAsText).toContainText(createdApiUser.name);

    await loginSignupPage.header.logout();
    await expect(loginSignupPage.loginTitle).toBeVisible();
  });
});
