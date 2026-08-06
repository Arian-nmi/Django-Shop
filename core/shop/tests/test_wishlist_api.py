from api.tests.base import APIBaseTestCase
from rest_framework import status
from shop.models import WishlistProductModel


class WishlistAPITest(APIBaseTestCase):
    def test_wishlist_requires_authentication(self):
        response = self.client.get("/api/v1/shop/wishlist/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_add_product_to_wishlist(self):
        self.authenticate(self.customer)

        response = self.client.post(
            "/api/v1/shop/wishlist/",
            {
                "product_id": self.published_product.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(WishlistProductModel.objects.filter(
                user=self.customer,
                product=self.published_product,
            ).exists()
        )

    def test_adding_same_product_twice_does_not_duplicate(self):
        WishlistProductModel.objects.create(
            user=self.customer,
            product=self.published_product,
        )

        self.authenticate(self.customer)

        response = self.client.post(
            "/api/v1/shop/wishlist/",
            {
                "product_id": self.published_product.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            WishlistProductModel.objects.filter(
                user=self.customer,
                product=self.published_product,
            ).count(), 1
        )

    def test_user_cannot_delete_another_user_wishlist_item(self):
        WishlistProductModel.objects.create(
            user=self.customer,
            product=self.published_product,
        )

        self.authenticate(self.other_customer)

        response = self.client.delete(
            f"/api/v1/shop/wishlist/"
            f"{self.published_product.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)