import { test, expect } from '../../src/fixtures/test-options';
import searchTerms from '../../src/fixtures/data/search-terms.json' with { type: 'json' };

test.describe('Search Product API @api', () => {
  for (const { term, expectMinResults } of searchTerms) {
    test(`searching for "${term}" returns at least ${expectMinResults} product(s) @regression`, async ({
      apiClient,
    }) => {
      const response = await apiClient.searchProduct(term);
      expect(response.status()).toBe(200);

      const body = await response.json();
      expect(body.responseCode).toBe(200);
      expect(body.products.length).toBeGreaterThanOrEqual(expectMinResults);
    });
  }

  test('missing search_product parameter returns a 400-equivalent responseCode @regression', async ({
    apiClient,
  }) => {
    const response = await apiClient.searchProductMissingParam();
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.responseCode).toBe(400);
    expect(body.message).toBe('Bad request, search_product parameter is missing in POST request.');
  });
});
