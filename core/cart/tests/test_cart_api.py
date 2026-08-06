from api.tests.base import APIBaseTestCase
from rest_framework import status
from cart.models import CartItemModel, CartModel



class CartAPITest(APIBaseTestCase):
    def test_cart_requires_jwt_authentication(self):
        response = self.client.get("/api/v1/cart/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_add_product_to_cart(self):
        self.authenticate(self.customer)

        response = self.client.post(
            "/api/v1/cart/items/",
            {
                "product_id": self.published_product.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_quantity"], 2)

        self.assertTrue(
            CartItemModel.objects.filter(
                cart__user=self.customer,
                product=self.published_product,
                quantity=2,
            ).exists()
        )

    def test_cart_cannot_exceed_product_stock(self):
        self.authenticate(self.customer)

        response = self.client.post(
            "/api/v1/cart/items/",
            {
                "product_id": self.published_product.id,
                "quantity": 20,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_see_another_user_cart(self):
        customer_cart = CartModel.objects.create(user=self.customer)

        CartItemModel.objects.create(
            cart=customer_cart,
            product=self.published_product,
            quantity=2,
        )

        self.authenticate(self.other_customer)

        response = self.client.get("/api/v1/cart/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_quantity"], 0)

    def test_user_can_update_and_delete_cart_item(self):
        cart = CartModel.objects.create(user=self.customer)

        CartItemModel.objects.create(
            cart=cart,
            product=self.published_product,
            quantity=1,
        )

        self.authenticate(self.customer)

        update_response = self.client.patch(
            f"/api/v1/cart/items/"
            f"{self.published_product.id}/",
            {
                "quantity": 3,
            },
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["total_quantity"], 3)

        delete_response = self.client.delete(
            f"/api/v1/cart/items/"
            f"{self.published_product.id}/"
        )

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.data["total_quantity"], 0)