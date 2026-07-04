import { test, expect } from '../../src/fixtures/test-options';
import type { Product } from '../../src/api/models/product.model';

test.describe('Products API @api', () => {
  test('GET productsList returns a non-empty, well-formed product list @smoke', async ({ apiClient }) => {
    const response = await apiClient.getProductsList();
    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.responseCode).toBe(200);
    expect(Array.isArray(body.products)).toBe(true);
    expect(body.products.length).toBeGreaterThan(0);

    const sample: Product = body.products[0];
    expect(sample).toHaveProperty('id');
    expect(sample).toHaveProperty('name');
    expect(sample).toHaveProperty('price');
    expect(sample).toHaveProperty('brand');
    expect(sample.category).toHaveProperty('category');
  });

  test('POST productsList is rejected with a 405-equivalent responseCode @regression', async ({
    apiClient,
  }) => {
    const response = await apiClient.postProductsList();
    expect(response.status()).toBe(200); // API always answers HTTP 200, real status lives in the body
    const body = await response.json();
    expect(body.responseCode).toBe(405);
    expect(body.message).toBe('This request method is not supported.');
  });
});
