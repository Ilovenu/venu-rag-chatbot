import { test, expect } from '../../../src/fixtures/test-options';

test.describe('Contact us', () => {
  test('submits the contact form successfully @smoke', async ({ contactUsPage }) => {
    await contactUsPage.open();
    await expect(contactUsPage.getInTouchHeading).toBeVisible();

    await contactUsPage.fillForm(
      'QA Contact',
      'qa.contact@example.com',
      'Automated framework showcase',
      'This message was submitted by an automated Playwright test.',
    );
    await contactUsPage.submit();

    await expect(contactUsPage.successMessage).toBeVisible();
    await expect(contactUsPage.successMessage).toHaveText(
      'Success! Your details have been submitted successfully.',
    );
  });
});
