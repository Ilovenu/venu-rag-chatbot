import { test, expect } from '../../../src/fixtures/test-options';

test.describe('Product details', () => {
  test('shows full product information @smoke', async ({ productDetailsPage }) => {
    await productDetailsPage.open(1);

    await expect(productDetailsPage.productName).toBeVisible();
    await expect(productDetailsPage.category).toContainText('Category:');
    await expect(productDetailsPage.price).toContainText('Rs.');
    await expect(productDetailsPage.availability).toContainText('In Stock');
    await expect(productDetailsPage.condition).toContainText('New');
    await expect(productDetailsPage.brand).toContainText('Brand:');
  });

  test('accepts and submits a product review @regression', async ({ productDetailsPage }) => {
    await productDetailsPage.open(1);
    await productDetailsPage.submitReview(
      'QA Reviewer',
      'qa.reviewer@example.com',
      'Great product, true to size.',
    );

    await expect(productDetailsPage.reviewSuccessMessage).toBeVisible();
    await expect(productDetailsPage.reviewSuccessMessage).toContainText('Thank you for your review.');
  });
});
