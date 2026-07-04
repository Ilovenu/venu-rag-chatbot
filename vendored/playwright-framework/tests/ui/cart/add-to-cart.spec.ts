import { test, expect } from '../../../src/fixtures/test-options';

test.describe('Cart', () => {
  test('adds a product from the listing page and reflects it in the cart @smoke', async ({
    productsPage,
    cartPage,
  }) => {
    await productsPage.open();
    await productsPage.card(0).addToCart();
    await productsPage.cartModal.viewCart();

    await expect(cartPage.rowForProduct(1)).toBeVisible();
  });

  test('lets a customer set quantity on the product page before adding to cart @regression', async ({
    productDetailsPage,
    cartPage,
  }) => {
    await productDetailsPage.open(1);
    await productDetailsPage.setQuantity(4);
    await productDetailsPage.addToCart();
    await productDetailsPage.cartModal.viewCart();

    const quantityText = await cartPage.quantityFor(1);
    expect(quantityText.trim()).toBe('4');
  });

  test('removes a product from the cart @regression', async ({ productDetailsPage, cartPage }) => {
    await productDetailsPage.open(2);
    await productDetailsPage.addToCart();
    await productDetailsPage.cartModal.viewCart();

    await expect(cartPage.rowForProduct(2)).toBeVisible();
    await cartPage.removeProduct(2);
    await expect(cartPage.rowForProduct(2)).toBeHidden();
  });
});
