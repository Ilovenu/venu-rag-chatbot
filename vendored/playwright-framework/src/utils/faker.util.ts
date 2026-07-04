import { faker } from '@faker-js/faker';
import type { User } from '../api/models/user.model';

export function generateFakeUser(overrides: Partial<User> = {}): User {
  const firstName = faker.person.firstName();
  const lastName = faker.person.lastName();

  return {
    name: `${firstName} ${lastName}`,
    email: `qa.${Date.now()}.${faker.string.alphanumeric(6).toLowerCase()}@example.com`,
    password: faker.internet.password({ length: 12 }),
    title: 'Mr',
    birthDate: String(faker.number.int({ min: 1, max: 28 })),
    birthMonth: String(faker.number.int({ min: 1, max: 12 })),
    birthYear: String(faker.number.int({ min: 1970, max: 2000 })),
    firstName,
    lastName,
    company: faker.company.name(),
    address1: faker.location.streetAddress(),
    address2: faker.location.secondaryAddress(),
    country: 'United States',
    state: faker.location.state(),
    city: faker.location.city(),
    zipcode: faker.location.zipCode(),
    mobileNumber: faker.phone.number({ style: 'national' }).replace(/\D/g, '').slice(0, 10),
    newsletter: true,
    optin: true,
    ...overrides,
  };
}
