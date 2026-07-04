import { test, expect } from '../../src/fixtures/test-options';
import { generateFakeUser } from '../../src/utils/faker.util';

test.describe('Account & Auth API @api', () => {
  test('full account lifecycle: create, verify login, fetch details, update, delete @smoke', async ({
    apiClient,
  }) => {
    const user = generateFakeUser();

    const createResponse = await apiClient.createAccount(user);
    const createBody = await createResponse.json();
    expect(createBody.responseCode).toBe(201);
    expect(createBody.message).toBe('User created!');

    const verifyResponse = await apiClient.verifyLogin(user.email, user.password);
    const verifyBody = await verifyResponse.json();
    expect(verifyBody.responseCode).toBe(200);
    expect(verifyBody.message).toBe('User exists!');

    const detailsResponse = await apiClient.getUserDetailByEmail(user.email);
    const detailsBody = await detailsResponse.json();
    expect(detailsBody.responseCode).toBe(200);
    expect(detailsBody.user.email).toBe(user.email);
    expect(detailsBody.user.name).toBe(user.name);
    expect(detailsBody.user.first_name).toBe(user.firstName);

    const updateResponse = await apiClient.updateAccount({ ...user, company: 'Updated Co' });
    const updateBody = await updateResponse.json();
    expect(updateBody.responseCode).toBe(200);
    expect(updateBody.message).toBe('User updated!');

    const deleteResponse = await apiClient.deleteAccount(user.email, user.password);
    const deleteBody = await deleteResponse.json();
    expect(deleteBody.responseCode).toBe(200);
    expect(deleteBody.message).toBe('Account deleted!');
  });

  test('creating an account with a duplicate email is rejected @regression', async ({
    apiClient,
    createdApiUser,
  }) => {
    const response = await apiClient.createAccount(createdApiUser);
    const body = await response.json();
    expect(body.responseCode).toBe(400);
    expect(body.message).toBe('Email already exists!');
  });

  test('verifyLogin rejects an unknown email @regression', async ({ apiClient }) => {
    const response = await apiClient.verifyLogin('does-not-exist.qa@example.com', 'whatever');
    const body = await response.json();
    expect(body.responseCode).toBe(404);
    expect(body.message).toBe('User not found!');
  });

  test('verifyLogin with a missing parameter returns a 400-equivalent responseCode @regression', async ({
    apiClient,
    createdApiUser,
  }) => {
    const response = await apiClient.verifyLoginMissingParam(createdApiUser.email);
    const body = await response.json();
    expect(body.responseCode).toBe(400);
    expect(body.message).toBe('Bad request, email or password parameter is missing in POST request.');
  });
});
