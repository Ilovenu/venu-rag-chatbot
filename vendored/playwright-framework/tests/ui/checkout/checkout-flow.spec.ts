import { test, expect } from '../../../src/fixtures/test-options';

test.describe('Checkout', () => {
  test('places an order end-to-end for a logged-in user @smoke', async ({
    loginSignupPage,
    productDetailsPage,
    cartPage,
    checkoutPage,
    paymentPage,
    createdApiUser,
  }) => {
    await loginSignupPage.open();
    await loginSignupPage.login(createdApiUser.email, createdApiUser.password);
    await expect(loginSignupPage.header.loggedInAsText).toBeVisible();

    await productDetailsPage.open(1);
    await productDetailsPage.addToCart();
    await productDetailsPage.cartModal.continueShopping();

    await cartPage.open();
    await expect(cartPage.rowForProduct(1)).toBeVisible();
    await cartPage.proceedToCheckout();

    await expect(checkoutPage.addressDetailsHeading).toBeVisible();
    await expect(checkoutPage.reviewOrderHeading).toBeVisible();
    await expect(checkoutPage.deliveryAddress).toContainText(createdApiUser.address1);
    await checkoutPage.addComment('Please deliver in the morning.');
    await checkoutPage.placeOrder();

    await paymentPage.fillPaymentDetails({
      nameOnCard: createdApiUser.name,
      cardNumber: '4111111111111111',
      cvc: '123',
      expiryMonth: '05',
      expiryYear: '2030',
    });
    await paymentPage.confirmPayment();

    await expect(paymentPage.orderPlacedMessage).toBeVisible();
    await expect(paymentPage.orderPlacedMessage).toHaveText('Order Placed!');
  });
});
