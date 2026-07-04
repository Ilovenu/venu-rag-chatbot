import { test, expect } from '../../../src/fixtures/test-options';
import searchTerms from '../../../src/fixtures/data/search-terms.json' with { type: 'json' };

const termsWithResults = searchTerms.filter((t) => t.expectMinResults > 0);
const termsWithNoResults = searchTerms.filter((t) => t.expectMinResults === 0);

test.describe('Product search', () => {
  for (const { term, expectMinResults } of termsWithResults) {
    test(`search for "${term}" returns matching products @regression`, async ({ productsPage }) => {
      await productsPage.open();
      await productsPage.search(term);

      await expect(productsPage.searchedProductsTitle).toBeVisible();
      const count = await productsPage.resultCount();
      expect(count).toBeGreaterThanOrEqual(expectMinResults);
      await expect(productsPage.card(0).name).toBeVisible();
    });
  }

  for (const { term } of termsWithNoResults) {
    test(`search for "${term}" returns no products @regression`, async ({ productsPage }) => {
      await productsPage.open();
      await productsPage.search(term);

      await expect(productsPage.searchedProductsTitle).toBeVisible();
      expect(await productsPage.resultCount()).toBe(0);
    });
  }
});
