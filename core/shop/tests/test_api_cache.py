from django.core.cache import cache
from django.test import override_settings

from api.tests.base import APIBaseTestCase


@override_settings(
    CACHES={
        "default": {
            "BACKEND": (
                "django.core.cache.backends.locmem.LocMemCache"
            ),
            "LOCATION": "shop-api-cache-test",
        }
    }
)
class ShopAPICacheTest(APIBaseTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_product_cache_is_invalidated_after_product_save(self):
        url = (
            f"/api/v1/shop/products/"
            f"{self.published_product.slug}/"
        )

        first_response = self.client.get(url)

        self.assertEqual(first_response.data["title"], "تیشرت تست")
        
        type(self.published_product).objects.filter(pk=self.published_product.pk).update(title="عنوان جدید بدون Signal")

        cached_response = self.client.get(url)

        self.assertEqual(cached_response.data["title"], "تیشرت تست")
        self.published_product.refresh_from_db()
        self.published_product.title = "عنوان جدید نهایی"

        with self.captureOnCommitCallbacks(execute=True):
            self.published_product.save()

        refreshed_response = self.client.get(url)
        self.assertEqual(refreshed_response.data["title"], "عنوان جدید نهایی")