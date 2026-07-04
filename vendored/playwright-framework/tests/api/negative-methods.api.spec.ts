import { test, expect } from '../../src/fixtures/test-options';
import type { ApiClient } from '../../src/api/apiClient';

const UNSUPPORTED_METHOD_CASES: {
  name: string;
  call: (client: ApiClient) => ReturnType<ApiClient['postProductsList']>;
}[] = [
  { name: 'POST productsList', call: (client) => client.postProductsList() },
  { name: 'PUT brandsList', call: (client) => client.putBrandsList() },
  { name: 'DELETE verifyLogin', call: (client) => client.deleteVerifyLogin() },
];

test.describe('Unsupported HTTP method contract @api', () => {
  for (const { name, call } of UNSUPPORTED_METHOD_CASES) {
    test(`${name} consistently reports a 405-equivalent responseCode @regression`, async ({ apiClient }) => {
      const response = await call(apiClient);
      expect(response.status()).toBe(200);

      const body = await response.json();
      expect(body.responseCode).toBe(405);
      expect(body.message).toBe('This request method is not supported.');
    });
  }
});
