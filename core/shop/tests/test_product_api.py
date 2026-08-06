from api.tests.base import APIBaseTestCase
from rest_framework import status


class ShopAPITest(APIBaseTestCase):
    def test_category_list_is_public(self):
        response = self.client.get("/api/v1/shop/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], self.category.title)

    def test_product_list_only_returns_published_products(self):
        response = self.client.get("/api/v1/shop/products/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_slugs = [product["slug"] for product in response.data["results"]]

        self.assertIn(self.published_product.slug, product_slugs)
        self.assertNotIn(self.draft_product.slug, product_slugs)

    def test_product_search_works(self):
        response = self.client.get("/api/v1/shop/products/", {"q": "تیشرت"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        self.assertEqual(response.data["results"][0]["id"], self.published_product.id)

    def test_product_category_filter_works(self):
        response = self.client.get(
            "/api/v1/shop/products/",
            {
                "category_id": self.category.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)

    def test_draft_product_detail_returns_404(self):
        response = self.client.get(
            f"/api/v1/shop/products/"
            f"{self.draft_product.slug}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_published_product_detail_is_public(self):
        response = self.client.get(
            f"/api/v1/shop/products/"
            f"{self.published_product.slug}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.published_product.title)