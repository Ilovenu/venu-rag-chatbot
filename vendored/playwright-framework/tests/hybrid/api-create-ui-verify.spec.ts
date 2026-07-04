import { test, expect } from '../../src/fixtures/test-options';

// API creates the account (fast, no UI wizard); the UI is used only to verify
// the account actually works end-to-end from a real user's perspective.
test.describe('Hybrid: API creates, UI verifies', () => {
  test('a user created via the API can log in through the UI @hybrid', async ({
    loginSignupPage,
    createdApiUser,
  }) => {
    await loginSignupPage.open();
    await loginSignupPage.login(createdApiUser.email, createdApiUser.password);

    await expect(loginSignupPage.header.loggedInAsText).toBeVisible();
    await expect(loginSignupPage.header.loggedInAsText).toContainText(createdApiUser.name);
    await expect(loginSignupPage.header.deleteAccountLink).toBeVisible();
  });
});
