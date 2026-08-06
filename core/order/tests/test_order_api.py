from api.tests.base import APIBaseTestCase
from rest_framework import status


class OrderAPITest(APIBaseTestCase):
    def test_order_api_requires_authentication(self):
        response = self.client.get("/api/v1/orders/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_see_own_orders(self):
        own_order = self.create_successful_order(self.customer, self.published_product)

        self.create_successful_order(self.other_customer, self.published_product)
        self.authenticate(self.customer)

        response = self.client.get("/api/v1/orders/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], own_order.id)

    def test_user_cannot_see_another_user_order(self):
        other_order = self.create_successful_order(self.other_customer, self.published_product)
        self.authenticate(self.customer)
        
        response = self.client.get(f"/api/v1/orders/{other_order.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_detail_contains_items_and_address(self):
        order = self.create_successful_order(self.customer, self.published_product)
        self.authenticate(self.customer)

        response = self.client.get(f"/api/v1/orders/{order.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["address_data"]["city"], "تهران")
        self.assertEqual(len(response.data["items"]), 1)