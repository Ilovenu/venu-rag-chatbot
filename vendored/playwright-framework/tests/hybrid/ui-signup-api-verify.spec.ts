import { test, expect } from '../../src/fixtures/test-options';
import { generateFakeUser } from '../../src/utils/faker.util';

// The UI drives the full signup wizard; the API is then used to verify the
// account persisted correctly and that its stored fields match what was
// actually typed into the form - a genuine cross-layer consistency check.
test.describe('Hybrid: UI creates, API verifies', () => {
  test('a user signed up through the UI is verifiable and consistent via the API @hybrid', async ({
    loginSignupPage,
    signupInfoPage,
    accountCreatedPage,
    apiClient,
  }) => {
    const user = generateFakeUser();

    await loginSignupPage.open();
    await loginSignupPage.startSignup(user.name, user.email);
    await expect(signupInfoPage.accountInfoTitle).toBeVisible();
    await signupInfoPage.fillAccountInformation(user);
    await signupInfoPage.submit();
    await expect(accountCreatedPage.accountCreatedMessage).toBeVisible();

    const verifyResponse = await apiClient.verifyLogin(user.email, user.password);
    const verifyBody = await verifyResponse.json();
    expect(verifyBody.responseCode).toBe(200);
    expect(verifyBody.message).toBe('User exists!');

    const detailsResponse = await apiClient.getUserDetailByEmail(user.email);
    const detailsBody = await detailsResponse.json();
    expect(detailsBody.user.name).toBe(user.name);
    expect(detailsBody.user.email).toBe(user.email);
    expect(detailsBody.user.first_name).toBe(user.firstName);
    expect(detailsBody.user.last_name).toBe(user.lastName);
    expect(detailsBody.user.company).toBe(user.company);
    expect(detailsBody.user.city).toBe(user.city);

    await apiClient.deleteAccount(user.email, user.password);
  });
});
