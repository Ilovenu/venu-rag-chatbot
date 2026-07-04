import { test, expect } from '../../src/fixtures/test-options';

test.describe('Brands API @api', () => {
  test('GET brandsList returns a non-empty brand list @smoke', async ({ apiClient }) => {
    const response = await apiClient.getBrandsList();
    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.responseCode).toBe(200);
    expect(Array.isArray(body.brands)).toBe(true);
    expect(body.brands.length).toBeGreaterThan(0);
    expect(body.brands[0]).toHaveProperty('id');
    expect(body.brands[0]).toHaveProperty('brand');
  });

  test('PUT brandsList is rejected with a 405-equivalent responseCode @regression', async ({ apiClient }) => {
    const response = await apiClient.putBrandsList();
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.responseCode).toBe(405);
    expect(body.message).toBe('This request method is not supported.');
  });
});
