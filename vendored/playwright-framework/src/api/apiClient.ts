import type { APIRequestContext, APIResponse } from '@playwright/test';
import { endpoints } from './endpoints';
import type { User } from './models/user.model';

function userToForm(user: User): Record<string, string> {
  return {
    name: user.name,
    email: user.email,
    password: user.password,
    title: user.title,
    birth_date: user.birthDate,
    birth_month: user.birthMonth,
    birth_year: user.birthYear,
    firstname: user.firstName,
    lastname: user.lastName,
    company: user.company,
    address1: user.address1,
    address2: user.address2,
    country: user.country,
    zipcode: user.zipcode,
    state: user.state,
    city: user.city,
    mobile_number: user.mobileNumber,
  };
}

export class ApiClient {
  constructor(private readonly request: APIRequestContext) {}

  getProductsList(): Promise<APIResponse> {
    return this.request.get(endpoints.productsList);
  }

  postProductsList(): Promise<APIResponse> {
    return this.request.post(endpoints.productsList);
  }

  getBrandsList(): Promise<APIResponse> {
    return this.request.get(endpoints.brandsList);
  }

  putBrandsList(): Promise<APIResponse> {
    return this.request.put(endpoints.brandsList);
  }

  searchProduct(searchTerm: string): Promise<APIResponse> {
    return this.request.post(endpoints.searchProduct, { form: { search_product: searchTerm } });
  }

  searchProductMissingParam(): Promise<APIResponse> {
    return this.request.post(endpoints.searchProduct);
  }

  verifyLogin(email: string, password: string): Promise<APIResponse> {
    return this.request.post(endpoints.verifyLogin, { form: { email, password } });
  }

  verifyLoginMissingParam(email: string): Promise<APIResponse> {
    return this.request.post(endpoints.verifyLogin, { form: { email } });
  }

  deleteVerifyLogin(): Promise<APIResponse> {
    return this.request.delete(endpoints.verifyLogin);
  }

  createAccount(user: User): Promise<APIResponse> {
    return this.request.post(endpoints.createAccount, { form: userToForm(user) });
  }

  updateAccount(user: User): Promise<APIResponse> {
    return this.request.put(endpoints.updateAccount, { form: userToForm(user) });
  }

  deleteAccount(email: string, password: string): Promise<APIResponse> {
    return this.request.delete(endpoints.deleteAccount, { form: { email, password } });
  }

  getUserDetailByEmail(email: string): Promise<APIResponse> {
    return this.request.get(endpoints.getUserDetailByEmail, { params: { email } });
  }
}
